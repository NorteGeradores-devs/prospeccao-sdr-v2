"""Exportação de leads para CSV/Excel com sanitização anti CSV-injection.

Células que começam com = + - @ podem virar fórmulas maliciosas ao abrir no
Excel; prefixamos com apóstrofo (mesma proteção usada no BI de Faturamento).
"""
from __future__ import annotations

import io

import pandas as pd

_PERIGOSOS = ("=", "+", "-", "@")
_CONTROLE = ("\t", "\r", "\n")


def _sanitizar_celula(valor):
    if isinstance(valor, str) and valor:
        # fórmula direta, após espaços à esquerda, ou iniciada por TAB/CR/LF
        if valor[0] in _PERIGOSOS or valor[0] in _CONTROLE or valor.lstrip()[:1] in _PERIGOSOS:
            return "'" + valor
    return valor


def sanitizar(df: pd.DataFrame) -> pd.DataFrame:
    # pandas >= 2.1 usa DataFrame.map; applymap foi removido no pandas 3.0.
    if hasattr(df, "map"):
        return df.map(_sanitizar_celula)
    return df.applymap(_sanitizar_celula)


def para_csv(df: pd.DataFrame) -> bytes:
    return sanitizar(df).to_csv(index=False).encode("utf-8-sig")


def para_excel(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        sanitizar(df).to_excel(writer, index=False, sheet_name="Leads")
    return buffer.getvalue()
