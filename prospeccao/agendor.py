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
    descricao = _descricao(row)
    payload = {
        "name": (row.get("nome") or row.get("nome_fantasia") or "").strip(),
        "description": descricao,
    }
    cnpj = so_digitos(str(row.get("cnpj", "")))
    if cnpj_valido(cnpj):
        payload["cnpj"] = formatar_cnpj(cnpj)
    if row.get("site"):
        payload["website"] = str(row["site"])

    contato = {}
    if row.get("email"):
        contato["email"] = str(row["email"])
    if row.get("telefone"):
        contato["work"] = so_digitos(str(row["telefone"]))
    if contato:
        payload["contact"] = contato
    return payload


def _descricao(row) -> str:
    linhas = [
        f"[Prospecção SDR] Fonte: {row.get('fonte','')} | "
        f"Score: {row.get('score','')} ({row.get('temperatura','')})",
        f"Segmento: {row.get('segmento','')} | UF: {row.get('uf','')} | "
        f"Município: {row.get('municipio','')}",
    ]
    if row.get("contato_nome"):
        linhas.append(f"Contato: {row['contato_nome']} ({row.get('contato_cargo','')})")
    if row.get("titulo"):
        linhas.append(f"Oportunidade: {row['titulo']}")
    if row.get("valor_estimado"):
        linhas.append(f"Valor estimado: R$ {row['valor_estimado']}")
    if row.get("url"):
        linhas.append(f"Link: {row['url']}")
    if row.get("observacoes"):
        linhas.append(str(row["observacoes"]))
    return "\n".join(linhas)
