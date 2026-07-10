"""Cache simples em disco (JSON) com TTL — evita rebater APIs a cada busca.

Usado no enriquecimento de CNPJ (Receita Federal via BrasilAPI) e para não
rebaixar os servidores da ANM/PNCP durante iterações de teste.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional

from config import CACHE_DIR, CACHE_TTL_HORAS


def _slug(chave: str) -> str:
    return hashlib.sha256(chave.encode("utf-8")).hexdigest()[:32]


def _caminho(namespace: str, chave: str) -> Path:
    pasta = CACHE_DIR / namespace
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta / f"{_slug(chave)}.json"


def get(namespace: str, chave: str, ttl_horas: int = CACHE_TTL_HORAS) -> Optional[Any]:
    caminho = _caminho(namespace, chave)
    if not caminho.exists():
        return None
    try:
        idade_h = (time.time() - caminho.stat().st_mtime) / 3600
        if idade_h > ttl_horas:
            return None
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def set(namespace: str, chave: str, valor: Any) -> None:
    caminho = _caminho(namespace, chave)
    try:
        caminho.write_text(json.dumps(valor, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def caminho_arquivo(namespace: str, nome: str) -> Path:
    """Caminho estável para artefatos binários (ex.: shapefiles do SIGMINE)."""
    pasta = CACHE_DIR / namespace
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta / nome
