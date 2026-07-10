"""Sympla — eventos que demandam energia temporária (palco, som, iluminação,
food trucks, arena). O organizador do evento é o lead.

Limitação honesta: a API pública da Sympla (header s_token) só lista os eventos
da CONTA dona do token — NÃO permite varrer eventos de terceiros. Não existe
endpoint público estável de busca por cidade. Portanto:
  • com SYMPLA_TOKEN: pull dos eventos da conta/parceiro (própria carteira);
  • sem token: a fonte é ignorada com aviso (em vez de fingir busca pública).

Para prospecção ampla de eventos, o caminho realista é parceria com produtores
ou uma fonte de dados de eventos licenciada.
"""
from __future__ import annotations

import logging

from config import SYMPLA_TOKEN
from prospeccao.http import HttpClient
from prospeccao.models import Lead
from prospeccao.utils import uf_valida

log = logging.getLogger("prospeccao")

API_OFICIAL = "https://api.sympla.com.br/public/v3/events"


def buscar(http: HttpClient, cidades: list[str] | None = None,
           uf: str = "", termo: str = "", max_eventos: int = 60,
           **_ignore) -> list[Lead]:
    if not SYMPLA_TOKEN:
        log.warning("Sympla: sem SYMPLA_TOKEN — a API pública não permite varrer "
                    "eventos de terceiros; fonte ignorada.")
        return []
    try:
        return _api_oficial(http, max_eventos)
    except Exception as exc:                            # noqa: BLE001
        log.warning("Sympla (API oficial) falhou: %s", exc)
        return []


def _api_oficial(http: HttpClient, limite: int) -> list[Lead]:
    headers = {"s_token": SYMPLA_TOKEN}
    resp = http.get(API_OFICIAL, headers=headers,
                    params={"page_size": min(limite, 100), "page": 1})
    resp.raise_for_status()
    eventos = resp.json().get("data", []) or []
    return [_parse_oficial(e) for e in eventos[:limite]]


def _parse_oficial(e: dict) -> Lead:
    address = e.get("address", {}) or {}
    host = e.get("host", {}) or {}
    return Lead(
        fonte="sympla",
        nome=host.get("name") or e.get("name", "") or "Organizador Sympla",
        titulo=e.get("name", ""),
        municipio=address.get("city", ""),
        uf=uf_valida(address.get("state", "")),
        data_evento=e.get("start_date", ""),
        url=e.get("url", ""),
        segmento="Eventos e Cultura",
        observacoes="Evento Sympla (API oficial). Contatar produtor.",
    )
