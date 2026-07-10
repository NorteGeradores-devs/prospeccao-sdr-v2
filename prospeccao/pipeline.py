"""Orquestração: buscar → deduplicar → enriquecer (Receita) → pontuar → ordenar."""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

import pandas as pd

from config import (
    GOOGLE_PLACES_QUERIES,
    KEYWORDS_GERADOR,
    UF_PRIORITARIAS,
)
from prospeccao.enriquecimento import enriquecer
from prospeccao.fontes import FONTES
from prospeccao.http import HttpClient
from prospeccao.models import COLUNAS, Lead
from prospeccao.scoring import pontuar

log = logging.getLogger("prospeccao")


def parametros_padrao() -> dict:
    """Parâmetros iniciais coerentes com o ICP da Norte Geradores."""
    return {
        "keywords": list(KEYWORDS_GERADOR),
        "ufs": list(UF_PRIORITARIAS),
        "municipios": [],
        "google_queries": list(GOOGLE_PLACES_QUERIES),
        "cnpjs": [],
        "cnaes": [],
        "pncp_status": "recebendo_proposta",
        "sympla_termo": "",
        "limite": 40,
    }


def _kwargs_por_fonte(fonte: str, p: dict) -> dict:
    lim = p.get("limite", 40)
    ufs = p.get("ufs", [])
    if fonte == "pncp":
        return {"keywords": p["keywords"], "ufs": ufs,
                "status": p.get("pncp_status", "recebendo_proposta"),
                "max_por_termo": lim}
    if fonte == "google_places":
        return {"queries": p.get("google_queries", []),
                "municipios": p.get("municipios", []),
                "uf": ufs[0] if ufs else "", "max_por_query": lim}
    if fonte == "cnpj":
        return {"cnpjs": p.get("cnpjs", []), "cnaes": p.get("cnaes", []),
                "ufs": ufs, "max_por_cnae": lim}
    if fonte == "sympla":
        return {"cidades": p.get("municipios", []), "uf": ufs[0] if ufs else "",
                "termo": p.get("sympla_termo", ""), "max_eventos": lim}
    if fonte == "sigmine":
        return {"ufs": ufs, "max_por_uf": lim}
    return {}


def _dedup(leads: list[Lead]) -> list[Lead]:
    """Mescla leads com a mesma chave, preenchendo campos vazios."""
    por_chave: dict[str, Lead] = {}
    for lead in leads:
        chave = lead.chave()
        if chave not in por_chave:
            por_chave[chave] = lead
            continue
        base = por_chave[chave]
        for campo, valor in vars(lead).items():
            if campo in ("motivos_score",):
                continue
            if not getattr(base, campo) and valor:
                setattr(base, campo, valor)
        if lead.fonte not in base.fonte:
            base.fonte = f"{base.fonte}+{lead.fonte}"
    return list(por_chave.values())


def _enriquecer_seguro(lead: Lead, http: HttpClient) -> None:
    """Enriquece um lead sem deixar uma falha derrubar o lote inteiro."""
    try:
        enriquecer(lead, http)
    except Exception as exc:                            # noqa: BLE001
        log.warning("Enriquecimento falhou p/ CNPJ %s: %s", lead.cnpj, exc)


def _enriquecer_em_lote(leads: list[Lead], http: HttpClient,
                        on_progress: Callable[[str, int], None] | None,
                        total: int) -> None:
    """Enriquece via Receita em paralelo (I/O-bound) com concorrência limitada.

    A Session do requests é reutilizada com segurança entre threads; o cache em
    disco por CNPJ evita rebater a BrasilAPI.
    """
    if not leads:
        return
    concluidos = 0
    with ThreadPoolExecutor(max_workers=6) as pool:
        futuros = [pool.submit(_enriquecer_seguro, l, http) for l in leads]
        for _ in as_completed(futuros):
            concluidos += 1
            if on_progress and concluidos % 10 == 0:
                on_progress(f"enriquecendo ({concluidos}/{len(leads)})", total)


def executar(selecao: list[str], params: dict, enriquecar: bool = True,
             on_progress: Callable[[str, int], None] | None = None) -> pd.DataFrame:
    """Roda o pipeline completo e devolve um DataFrame ordenado por score."""
    leads: list[Lead] = []
    with HttpClient() as http:
        for fonte in selecao:
            if fonte not in FONTES:
                log.warning("Fonte desconhecida ignorada: %s", fonte)
                continue
            try:
                achados = FONTES[fonte]["buscar"](http, **_kwargs_por_fonte(fonte, params))
                leads += achados
                log.info("Fonte %s: %d leads", fonte, len(achados))
            except Exception as exc:                   # noqa: BLE001
                log.error("Fonte %s falhou: %s", fonte, exc)
            if on_progress:
                on_progress(fonte, len(leads))

        leads = _dedup(leads)

        if enriquecar:
            alvo = [l for l in leads if l.cnpj]
            _enriquecer_em_lote(alvo, http, on_progress, len(leads))

    for lead in leads:
        pontuar(lead)
    leads.sort(key=lambda l: l.score, reverse=True)

    if not leads:
        return pd.DataFrame(columns=COLUNAS)
    return pd.DataFrame([l.to_row() for l in leads], columns=COLUNAS)


def resumo(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"total": 0, "quentes": 0, "mornos": 0, "frios": 0,
                "por_fonte": {}, "com_contato": 0}
    temp = df["temperatura"].value_counts()
    return {
        "total": len(df),
        "quentes": int(temp.get("quente", 0)),
        "mornos": int(temp.get("morno", 0)),
        "frios": int(temp.get("frio", 0)),
        "por_fonte": df["fonte"].value_counts().to_dict(),
        "com_contato": int(((df["telefone"] != "") | (df["email"] != "")).sum()),
    }
