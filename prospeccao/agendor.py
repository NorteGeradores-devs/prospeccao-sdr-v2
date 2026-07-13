"""Integração com o CRM Agendor — envia leads prospectados como Organizações.

A Norte já usa o Agendor (mesma conta do BI de Faturamento). Aqui empurramos os
leads qualificados direto para o funil, evitando digitação manual do SDR.
API v3: https://api.agendor.com.br/v3  (header Authorization: Token <token>)
"""
from __future__ import annotations

import logging

import pandas as pd

from config import AGENDOR_TOKEN
from prospeccao.http import HttpClient
from prospeccao.utils import cnpj_valido, formatar_cnpj, so_digitos

log = logging.getLogger("prospeccao")

BASE = "https://api.agendor.com.br/v3"


def _txt(v) -> str:
    """Coage célula (str/None/NaN do pandas) para string limpa e sem espaços."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return str(v).strip()


def enviar_leads(df: pd.DataFrame, token: str | None = None,
                 apenas_temperatura: list[str] | None = None) -> dict:
    """Cria uma Organização no Agendor por lead. Retorna um resumo do envio.

    apenas_temperatura: se informado (ex.: ['quente']), filtra o que subir.
    """
    token = (token or AGENDOR_TOKEN).strip()
    if not token:
        return {"ok": False, "erro": "AGENDOR_TOKEN ausente no .env."}
    if df.empty:
        return {"ok": True, "criados": 0, "falhas": 0, "detalhes": []}

    if apenas_temperatura:
        df = df[df["temperatura"].isin(apenas_temperatura)]

    headers = {"Authorization": f"Token {token}",
               "Content-Type": "application/json"}
    criados, falhas, detalhes = 0, 0, []

    with HttpClient(headers=headers) as http:
        for _, row in df.iterrows():
            payload = _payload(row)
            if not payload["name"]:
                continue
            try:
                resp = http.post(f"{BASE}/organizations", json=payload)
                if resp.status_code in (200, 201):
                    criados += 1
                else:
                    falhas += 1
                    detalhes.append(f"{payload['name']}: HTTP {resp.status_code} "
                                    f"{resp.text[:120]}")
            except Exception as exc:                   # noqa: BLE001
                falhas += 1
                detalhes.append(f"{payload['name']}: {exc}")

    return {"ok": True, "criados": criados, "falhas": falhas, "detalhes": detalhes[:20]}


def _payload(row) -> dict:
    payload = {
        "name": _txt(row.get("nome")) or _txt(row.get("nome_fantasia")),
        "description": _descricao(row),
    }
    cnpj = so_digitos(_txt(row.get("cnpj")))
    if cnpj_valido(cnpj):
        payload["cnpj"] = formatar_cnpj(cnpj)
    if _txt(row.get("site")):
        payload["website"] = _txt(row["site"])

    contato = {}
    if _txt(row.get("email")):
        contato["email"] = _txt(row["email"])
    if _txt(row.get("telefone")):
        contato["work"] = so_digitos(_txt(row["telefone"]))
    if contato:
        payload["contact"] = contato
    return payload


def _descricao(row) -> str:
    linhas = [
        f"[Prospecção SDR] Fonte: {_txt(row.get('fonte'))} | "
        f"Score: {_txt(row.get('score'))} ({_txt(row.get('temperatura'))})",
        f"Segmento: {_txt(row.get('segmento'))} | UF: {_txt(row.get('uf'))} | "
        f"Município: {_txt(row.get('municipio'))}",
    ]
    if _txt(row.get("contato_nome")):
        linhas.append(f"Contato: {_txt(row['contato_nome'])} ({_txt(row.get('contato_cargo'))})")
    if _txt(row.get("titulo")):
        linhas.append(f"Oportunidade: {_txt(row['titulo'])}")
    valor = row.get("valor_estimado")
    if valor and not (isinstance(valor, float) and pd.isna(valor)):
        linhas.append(f"Valor estimado: R$ {valor}")
    if _txt(row.get("url")):
        linhas.append(f"Link: {_txt(row['url'])}")
    if _txt(row.get("observacoes")):
        linhas.append(_txt(row["observacoes"]))
    return "\n".join(linhas)
