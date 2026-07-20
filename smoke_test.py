"""Smoke test offline — valida imports, dedup, scoring e exportação sem rede.

Rodar: python smoke_test.py
"""
from __future__ import annotations

import sys

from prospeccao import export
from prospeccao.fontes import FONTES
from prospeccao.models import COLUNAS, Lead
from prospeccao.pipeline import _dedup, _kwargs_por_fonte, parametros_padrao, resumo
from prospeccao.scoring import pontuar
from prospeccao.utils import cnpj_valido

import pandas as pd


def check(cond: bool, msg: str):
    print(("OK  " if cond else "FALHA ") + msg)
    if not cond:
        sys.exit(1)


def main():
    # 1. Registro de fontes completo (5 públicas + sisloc/ccee portadas do David)
    check(set(FONTES) == {"pncp", "google_places", "cnpj", "sympla", "sigmine",
                          "sisloc", "ccee"},
          "7 fontes registradas (inclui sisloc + ccee)")

    # 2. kwargs por fonte não quebram
    p = parametros_padrao()
    for f in FONTES:
        _kwargs_por_fonte(f, p)
    check(True, "mapeamento de parâmetros por fonte")

    # 3. Validação de CNPJ
    check(cnpj_valido("00000000000191") and not cnpj_valido("11111111111111"),
          "validação de CNPJ")

    # 4. Dedup mescla por CNPJ e preenche campos vazios
    a = Lead(fonte="google_places", nome="Mineradora Norte", cnpj="00000000000191",
             telefone="(92) 98888-7777")
    b = Lead(fonte="cnpj", nome="MINERADORA NORTE LTDA", cnpj="00.000.000/0001-91",
             email="contato@min.com", uf="AM", segmento="Mineração")
    merged = _dedup([a, b])
    check(len(merged) == 1, "dedup por CNPJ (2 -> 1)")
    check(merged[0].telefone and merged[0].email, "merge preenche telefone + email")
    check("google_places" in merged[0].fonte and "cnpj" in merged[0].fonte,
          "fonte combinada preservada")

    # 5. Scoring + temperatura
    quente = pontuar(Lead(fonte="pncp", nome="Pref. Manaus", uf="AM",
                          segmento="X", valor_estimado=900_000, telefone="x",
                          email="a@b.c"))
    frio = pontuar(Lead(fonte="google_places", nome="Loja", uf="SP"))
    check(quente.temperatura == "quente" and frio.score < quente.score,
          "scoring diferencia quente x frio")

    # 6. Exportação CSV/Excel com sanitização
    df = pd.DataFrame([l.to_row() for l in merged], columns=COLUNAS)
    csv = export.para_csv(df)
    xlsx = export.para_excel(df)
    check(len(csv) > 0 and len(xlsx) > 0, "exportação CSV + Excel")

    # 7. Sanitização anti CSV-injection
    perigoso = pd.DataFrame([{"nome": "=cmd()", "uf": "AM"}])
    texto = export.para_csv(perigoso).decode("utf-8-sig")
    check("'=cmd()" in texto, "sanitização de fórmula no CSV")

    # 8. Resumo
    r = resumo(df)
    check(r["total"] == 1, "resumo agrega corretamente")

    # 9. Correções de dados do code review
    from prospeccao.utils import normalizar_cnae, parse_dinheiro, segmento_por_cnae
    check(normalizar_cnae(710301) == "0710301" and segmento_por_cnae(710301) == "Mineração",
          "CNAE preserva zero à esquerda (segmento Mineração)")
    check(parse_dinheiro("10000.00") == 10000.0 and parse_dinheiro("10.000,00") == 10000.0,
          "capital_social BR/US sem inflar 100x")
    e1 = Lead(fonte="pncp", nome="Pref", cnpj="00000000000191",
              url="https://pncp.gov.br/app/editais/00000000000191/2026/1")
    e2 = Lead(fonte="pncp", nome="Pref", cnpj="00000000000191",
              url="https://pncp.gov.br/app/editais/00000000000191/2026/2")
    check(len(_dedup([e1, e2])) == 2, "editais distintos do mesmo órgão não colapsam")
    check("endereco" in COLUNAS, "coluna endereco exportada")

    # 10. Resolvedor de CNPJ por nome (lógica pura, sem rede)
    from prospeccao import resolvedor_cnpj as rc
    check(rc._extrair_cnpjs("x 00.000.000/0001-91 y 11.111.111/1111-11") == ["00000000000191"],
          "resolvedor extrai só CNPJ com DV válido")
    check(rc._similaridade("Mineradora Norte LTDA", "MINERADORA NORTE S/A") == 1.0
          and rc._similaridade("Padaria X", "Posto Y") == 0.0,
          "resolvedor mede similaridade ignorando forma jurídica")
    check(rc.resolver_em_lote([Lead(fonte="cnpj", nome="Tem", cnpj="00000000000191")],
                              http=None) == 0,
          "resolvedor pula lead que já tem CNPJ (sem rede)")

    # 11. Fontes portadas do David — scoring dos sinais SISLOC/CCEE (sem rede)
    cli_recorrente = pontuar(Lead(fonte="sisloc", nome="Cliente Fiel", uf="AM",
                                  extra={"qtd_locacoes": 60, "dias_sem_locar": 120,
                                         "situacao": "N", "ativo": "S"}))
    cli_bloqueado = pontuar(Lead(fonte="sisloc", nome="Cliente Ruim", uf="AM",
                                 extra={"qtd_locacoes": 0, "dias_sem_locar": None,
                                        "situacao": "B", "ativo": "N"}))
    check(cli_recorrente.score > cli_bloqueado.score,
          "SISLOC: recorrente+reativação pontua acima de bloqueado/nunca-locou")
    check(any("reativação" in m for m in cli_recorrente.motivos_score),
          "SISLOC: janela de reativação entra nos motivos")

    energia = pontuar(Lead(fonte="cnpj", nome="Fábrica X", uf="PA",
                           extra={"grande_consumidor_energia": True}))
    sem_energia = pontuar(Lead(fonte="cnpj", nome="Fábrica X", uf="PA"))
    check(energia.score == sem_energia.score + 15,
          "CCEE: selo de consumidor livre soma +15 no scoring")

    for f in ("sisloc", "ccee"):          # kwargs por fonte não quebram
        _kwargs_por_fonte(f, parametros_padrao())
    check(True, "kwargs de sisloc/ccee mapeados")

    print("\n>> SMOKE TEST OK — pipeline íntegro (sem rede).")


if __name__ == "__main__":
    main()
