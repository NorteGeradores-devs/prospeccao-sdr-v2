"""PNCP — Portal Nacional de Contratações Públicas.

Usa a API pública de busca do portal (a mesma do front-end):
https://pncp.gov.br/api/search/ — procurando editais cujo objeto contenha
palavras‑chave de geração de energia. Cada edital é uma OPORTUNIDADE: um
contrato de compra/locação de gerador a ser disputado.
"""
from __future__ import annotations

import logging
import time

from prospeccao.http import HttpClient
from prospeccao.models import Lead
from prospeccao.utils import so_digitos, uf_valida

log = logging.getLogger("prospeccao")

BASE = "https://pncp.gov.br/api/search/"
PORTAL = "https://pncp.gov.br"

MAX_PAGINAS = 8        # teto de páginas por termo (evita paginação profunda)
PAUSA_SEGUNDOS = 0.25  # cortesia entre requisições p/ não tomar rate-limit


def buscar(http: HttpClient, keywords: list[str], ufs: list[str] | None = None,
           status: str = "recebendo_proposta", max_por_termo: int = 60,
           **_ignore) -> list[Lead]:
    ufs = [u.upper() for u in (ufs or [])]
    leads: list[Lead] = []
    vistos: set[str] = set()

    for termo in keywords:
        try:
            leads += _buscar_termo(http, termo, ufs, status, max_por_termo, vistos)
        except Exception as exc:                       # noqa: BLE001
            log.warning("PNCP falhou para '%s': %s", termo, exc)
    return leads


def _buscar_termo(http, termo, ufs, status, limite, vistos) -> list[Lead]:
    coletados: list[Lead] = []
    pagina, tam = 1, 20
    while len(coletados) < limite and pagina <= MAX_PAGINAS:
        params = {
            "q": termo,
            "tipos_documento": "edital",
            "ordenacao": "-data",
            "pagina": pagina,
            "tam_pagina": tam,
        }
        if status:
            params["status"] = status
        if pagina > 1:
            time.sleep(PAUSA_SEGUNDOS)
        data = http.get_json(BASE, params=params)
        items = data.get("items") or []
        if not items:
            break
        for it in items:
            lead = _parse(it, termo)
            if ufs and lead.uf not in ufs:      # descarta também UF vazia ao filtrar
                continue
            chave = lead.url or lead.titulo
            if chave in vistos:
                continue
            vistos.add(chave)
            coletados.append(lead)
        if pagina * tam >= int(data.get("total") or 0):
            break
        pagina += 1
    return coletados[:limite]


def _parse(it: dict, termo: str) -> Lead:
    url = _link_edital(it)
    # O endpoint de BUSCA do PNCP não retorna o valor da contratação
    # (valor_global vem vazio); por isso valor_estimado fica 0 e o SDR consulta
    # o valor no portal pelo link. Não inventamos um número.
    encerramento = it.get("data_fim_vigencia") or ""

    return Lead(
        fonte="pncp",
        nome=it.get("orgao_nome") or it.get("razao_social") or "Órgão não informado",
        cnpj=so_digitos(it.get("orgao_cnpj") or ""),
        municipio=it.get("municipio_nome") or "",
        uf=uf_valida(it.get("uf")),
        titulo=(it.get("description") or it.get("title") or "").strip(),
        valor_estimado=0.0,
        data_evento=encerramento,
        url=url,
        segmento="Setor Público / Licitação",
        observacoes=(
            f"Edital PNCP (busca: '{termo}'). "
            f"Modalidade: {it.get('modalidade_licitacao_nome', 'n/d')}. "
            f"Encerramento das propostas: {encerramento or 'n/d'}. "
            f"Valor não consultado (não vem na busca) — ver no link."
        ),
    )


def _link_edital(it: dict) -> str:
    """Monta o link público do edital: /app/editais/{cnpj}/{ano}/{sequencial}.

    (O item_url da busca vem como /compras/... e não abre no portal.)
    """
    cnpj = so_digitos(it.get("orgao_cnpj") or "")
    ano = it.get("ano") or ""
    seq = it.get("numero_sequencial") or ""
    if cnpj and ano and seq:
        return f"{PORTAL}/app/editais/{cnpj}/{ano}/{seq}"
    item_url = it.get("item_url") or ""
    if item_url.startswith("http"):
        return item_url
    return (PORTAL + item_url) if item_url else ""
