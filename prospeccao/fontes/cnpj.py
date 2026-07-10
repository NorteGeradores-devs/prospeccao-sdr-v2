"""Fonte CNPJ — empresas do segmento‑alvo.

Dois modos, ambos úteis:

1. LISTA: recebe uma lista de CNPJs (ex.: associados de sindicato, expositores
   de feira, carteira antiga) e transforma em leads — o enriquecimento posterior
   puxa razão social, contato e sócios da Receita (BrasilAPI, grátis).

2. SEGMENTO: busca empresas ativas por CNAE + UF usando a API da CNPJá
   (https://api.cnpja.com/office). Requer CNPJ_SEARCH_TOKEN. Sem token, o modo
   segmento é ignorado (a busca por lista continua funcionando de graça).
"""
from __future__ import annotations

import logging

from config import CNAE_ALVO_BUSCA, CNPJ_SEARCH_TOKEN
from prospeccao.http import HttpClient
from prospeccao.models import Lead
from prospeccao.utils import (
    cnpj_valido,
    formatar_cnpj,
    limpar_telefone,
    segmento_por_cnae,
    so_digitos,
    uf_valida,
)

log = logging.getLogger("prospeccao")

CNPJA_OFFICE = "https://api.cnpja.com/office"

# ATENÇÃO: o contrato da busca /office da CNPJá (nomes dos filtros e envelope de
# resposta) NÃO foi verificado contra a API real (exige chave paga). Antes de
# confiar no modo segmento em produção, valide os campos abaixo com a conta.
_CNPJA_CONTRATO_VERIFICADO = False


def buscar(http: HttpClient, cnpjs: list[str] | None = None,
           cnaes: list[str] | None = None, ufs: list[str] | None = None,
           max_por_cnae: int = 50, **_ignore) -> list[Lead]:
    leads: list[Lead] = []

    # Modo 1 — lista de CNPJs (sempre disponível; enriquecimento ocorre no pipeline)
    for c in cnpjs or []:
        n = so_digitos(c)
        if cnpj_valido(n):
            leads.append(Lead(fonte="cnpj", nome="", cnpj=n,
                              observacoes="CNPJ informado — enriquecer via Receita."))
        else:
            log.info("CNPJ inválido ignorado: %s", c)

    # Modo 2 — busca por segmento (CNAE) via CNPJá
    if CNPJ_SEARCH_TOKEN:
        alvo_cnaes = cnaes or CNAE_ALVO_BUSCA
        for cnae in alvo_cnaes:
            try:
                leads += _buscar_cnpja(http, cnae, ufs, max_por_cnae)
            except Exception as exc:                   # noqa: BLE001
                log.warning("CNPJá falhou para CNAE %s: %s", cnae, exc)
    elif not (cnpjs):
        log.warning("Fonte CNPJ: sem CNPJ_SEARCH_TOKEN e sem lista de CNPJs — "
                    "nada a fazer. Informe CNPJs ou configure a CNPJá.")
    return leads


def _buscar_cnpja(http, cnae, ufs, limite) -> list[Lead]:
    if not _CNPJA_CONTRATO_VERIFICADO:
        log.warning("CNPJ: busca por segmento usa contrato CNPJá NÃO verificado — "
                    "resultado vazio pode ser schema divergente, não ausência real.")
    coletados: list[Lead] = []
    headers = {"Authorization": CNPJ_SEARCH_TOKEN}
    pagina, tam = 1, 20
    while len(coletados) < limite:
        params = {
            "activity.id": so_digitos(cnae),
            "status.id": "2",                # ativa
            "head": "true",                  # matriz
            "page": pagina,
            "limit": tam,
        }
        if ufs:
            params["address.state"] = ",".join(u.upper() for u in ufs)
        resp = http.get(CNPJA_OFFICE, headers=headers, params=params)
        if resp.status_code != 200:
            log.warning("CNPJá HTTP %s: %s", resp.status_code, resp.text[:200])
            break
        data = resp.json()
        registros = data.get("records") or data.get("data") or []
        if not registros:
            break
        for r in registros:
            coletados.append(_parse_cnpja(r, cnae))
        if len(registros) < tam:
            break
        pagina += 1
    return coletados[:limite]


def _parse_cnpja(r: dict, cnae: str) -> Lead:
    company = r.get("company", {}) or {}
    address = r.get("address", {}) or {}
    phones = r.get("phones") or []
    emails = r.get("emails") or []
    telefone = ""
    if phones:
        p = phones[0]
        telefone = limpar_telefone(f"{p.get('area','')}{p.get('number','')}")
    return Lead(
        fonte="cnpj",
        nome=company.get("name") or r.get("alias") or "",
        cnpj=so_digitos(r.get("taxId", "")),
        nome_fantasia=r.get("alias", "") or "",
        segmento=segmento_por_cnae(cnae),
        cnae=so_digitos(cnae),
        municipio=address.get("city", ""),
        uf=uf_valida(address.get("state", "")),
        telefone=telefone,
        email=emails[0].get("address", "") if emails else "",
        capital_social=float(company.get("equity") or 0),
        observacoes=f"Busca CNPJá por CNAE {formatar_cnpj(cnae) if len(cnae)==14 else cnae}.",
    )
