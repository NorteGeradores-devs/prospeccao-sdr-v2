"""CLI de prospecção — para rodar manualmente ou agendado (Task Scheduler).

Exemplos:
  python cli.py --fontes pncp --uf AM PA --saida leads.xlsx
  python cli.py --fontes pncp google_places sigmine --uf AM --limite 30
  python cli.py --fontes cnpj --cnpjs 12345678000199 98765432000110
  python cli.py --fontes pncp --uf AM --enviar-agendor --temperatura quente
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from prospeccao import export, pipeline
from prospeccao.agendor import enviar_leads
from prospeccao.fontes import FONTES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def parse_args():
    p = argparse.ArgumentParser(description="Prospecção de leads — Norte Geradores")
    p.add_argument("--fontes", nargs="+", default=["pncp"],
                   choices=list(FONTES.keys()),
                   help="Fontes a consultar.")
    p.add_argument("--uf", nargs="+", dest="ufs", default=None,
                   help="UFs alvo (padrão: Norte).")
    p.add_argument("--municipios", nargs="+", default=[],
                   help="Cidades (Google Places / Sympla).")
    p.add_argument("--keywords", nargs="+", default=None,
                   help="Palavras-chave de licitação (PNCP).")
    p.add_argument("--cnpjs", nargs="+", default=[],
                   help="Lista de CNPJs para enriquecer (fonte cnpj).")
    p.add_argument("--limite", type=int, default=40,
                   help="Máximo de itens por termo/fonte.")
    p.add_argument("--sem-enriquecer", action="store_true",
                   help="Não consultar a Receita (mais rápido).")
    p.add_argument("--resolver-cnpj", action="store_true",
                   help="Descobre o CNPJ por nome (best-effort grátis) para leads "
                        "sem CNPJ (Google Places/SIGMINE). Mais lento.")
    p.add_argument("--dias-sem-locar", type=int, default=None,
                   help="SISLOC: só clientes parados há pelo menos N dias (reativação).")
    p.add_argument("--sisloc-com-locacao", action="store_true",
                   help="SISLOC: exclui cadastros que nunca locaram.")
    p.add_argument("--atualizar-ccee", action="store_true",
                   help="Baixa/atualiza a base de consumidores livres (CCEE/ANEEL) e sai.")
    p.add_argument("--saida", default="leads.xlsx",
                   help="Arquivo de saída (.xlsx ou .csv).")
    p.add_argument("--enviar-agendor", action="store_true",
                   help="Sobe os leads para o CRM Agendor.")
    p.add_argument("--temperatura", nargs="+", default=None,
                   choices=["quente", "morno", "frio"],
                   help="Filtra o que enviar ao Agendor.")
    return p.parse_args()


def main():
    args = parse_args()

    if args.atualizar_ccee:
        from prospeccao.fontes import ccee
        print(">> Atualizando base de consumidores livres (CCEE/ANEEL)...")
        qtd = ccee.atualizar_cache_aneel()
        print(f">> {qtd} consumidores na base." if qtd
              else ">> Falhou: a ANEEL não expôs a base agora. Tente mais tarde ou "
                   "importe um CSV lista_perfil da CCEE.")
        return

    params = pipeline.parametros_padrao()
    if args.ufs:
        params["ufs"] = [u.upper() for u in args.ufs]
    if args.municipios:
        params["municipios"] = args.municipios
    if args.keywords:
        params["keywords"] = args.keywords
    if args.cnpjs:
        params["cnpjs"] = args.cnpjs
    params["limite"] = args.limite
    params["sisloc_dias_sem_locar"] = args.dias_sem_locar
    params["sisloc_apenas_com_locacao"] = args.sisloc_com_locacao

    print(f">> Fontes: {', '.join(args.fontes)} | UFs: {', '.join(params['ufs'])}")
    df = pipeline.executar(args.fontes, params, enriquecar=not args.sem_enriquecer,
                           resolver_cnpj=args.resolver_cnpj,
                           on_progress=lambda f, n: print(f"   [{f}] parcial: {n} leads"))

    r = pipeline.resumo(df)
    print(f"\n== {r['total']} leads | quentes {r['quentes']} · "
          f"mornos {r['mornos']} · frios {r['frios']} "
          f"| com contato: {r.get('com_contato', 0)}")

    if df.empty:
        print("Nenhum lead encontrado.")
        return

    saida = Path(args.saida)
    if saida.parent and not saida.parent.exists():
        saida.parent.mkdir(parents=True, exist_ok=True)   # cria a pasta de saída
    dados = export.para_excel(df) if saida.suffix.lower() == ".xlsx" else export.para_csv(df)
    saida.write_bytes(dados)
    print(f">> Salvo em {saida.resolve()}")

    if args.enviar_agendor:
        print(">> Enviando ao Agendor...")
        res = enviar_leads(df, apenas_temperatura=args.temperatura)
        if res["ok"]:
            print(f"   Criados: {res['criados']} | Falhas: {res['falhas']}")
            for d in res["detalhes"]:
                print(f"   - {d}")
        else:
            print(f"   Erro: {res['erro']}")


if __name__ == "__main__":
    main()
