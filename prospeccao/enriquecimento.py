"""Enriquecimento de contatos via Receita Federal.

Fonte primária: BrasilAPI (https://brasilapi.com.br/api/cnpj/v1/{cnpj}) — dados
públicos da Receita Federal, gratuita e sem chave. Fallback: ReceitaWS.
Resultado é cacheado em disco por CNPJ para não rebater a API a cada busca.
"""
from __future__ import annotations

import logging

from prospeccao import cache
from prospeccao.http import HttpClient
from prospeccao.models import Lead
from prospeccao.utils import (
    cnpj_valido,
    limpar_telefone,
    normalizar_cnae,
    parse_dinheiro,
    segmento_por_cnae,
    so_digitos,
)

log = logging.getLogger("prospeccao")

BRASILAPI = "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
RECEITAWS = "https://receitaws.com.br/v1/cnpj/{cnpj}"


def consultar_cnpj(cnpj: str, http: HttpClient) -> dict | None:
    """Retorna o cadastro da Receita para um CNPJ (com cache), ou None."""
    n = so_digitos(cnpj)
    if not cnpj_valido(n):
        return None

    cacheado = cache.get("cnpj", n)
    if cacheado is not None:
        return cacheado or None

    dados = _via_brasilapi(n, http) or _via_receitaws(n, http)
    cache.set("cnpj", n, dados or {})     # cacheia vazio p/ evitar retry em loop
    return dados


def _via_brasilapi(n: str, http: HttpClient) -> dict | None:
    try:
        resp = http.get(BRASILAPI.format(cnpj=n))
        if resp.status_code != 200:
            return None
        d = resp.json()
        socios = [
            {"nome": s.get("nome_socio") or "", "cargo": s.get("qualificacao_socio") or ""}
            for s in (d.get("qsa") or [])
        ]
        # .get(chave, "") NÃO protege contra JSON null (chave presente = None);
        # por isso o "or ''" em cada campo.
        return {
            "razao_social": d.get("razao_social") or "",
            "nome_fantasia": d.get("nome_fantasia") or "",
            "cnae": normalizar_cnae(d.get("cnae_fiscal")),
            "cnae_descricao": d.get("cnae_fiscal_descricao") or "",
            "telefone": d.get("ddd_telefone_1") or "",
            "email": d.get("email") or "",
            "municipio": d.get("municipio") or "",
            "uf": d.get("uf") or "",
            "endereco": _endereco(d),
            "capital_social": parse_dinheiro(d.get("capital_social")),
            "situacao": d.get("descricao_situacao_cadastral") or "",
            "socios": socios,
        }
    except Exception as exc:                          # noqa: BLE001
        log.debug("BrasilAPI falhou p/ %s: %s", n, exc)
        return None


def _via_receitaws(n: str, http: HttpClient) -> dict | None:
    try:
        resp = http.get(RECEITAWS.format(cnpj=n))
        if resp.status_code != 200:
            return None
        d = resp.json()
        if d.get("status") == "ERROR":
            return None
        atividade = (d.get("atividade_principal") or [{}])[0]
        socios = [
            {"nome": s.get("nome") or "", "cargo": s.get("qual") or ""}
            for s in (d.get("qsa") or [])
        ]
        return {
            "razao_social": d.get("nome") or "",
            "nome_fantasia": d.get("fantasia") or "",
            "cnae": normalizar_cnae(atividade.get("code", "")),
            "cnae_descricao": atividade.get("text") or "",
            "telefone": d.get("telefone") or "",
            "email": d.get("email") or "",
            "municipio": d.get("municipio") or "",
            "uf": d.get("uf") or "",
            "endereco": f"{d.get('logradouro','')}, {d.get('numero','')} - {d.get('bairro','')}",
            "capital_social": parse_dinheiro(d.get("capital_social")),  # "10.000,00" != 1.000.000
            "situacao": d.get("situacao") or "",
            "socios": socios,
        }
    except Exception as exc:                          # noqa: BLE001
        log.debug("ReceitaWS falhou p/ %s: %s", n, exc)
        return None


def _endereco(d: dict) -> str:
    partes = [
        d.get("logradouro", ""), d.get("numero", ""),
        d.get("bairro", ""), d.get("cep", ""),
    ]
    return " ".join(p for p in partes if p).strip()


def enriquecer(lead: Lead, http: HttpClient) -> Lead:
    """Preenche campos vazios do lead com dados da Receita (não sobrescreve)."""
    dados = consultar_cnpj(lead.cnpj, http)
    if not dados:
        return lead

    lead.nome = lead.nome or dados["razao_social"]
    lead.nome_fantasia = lead.nome_fantasia or dados["nome_fantasia"]
    lead.cnae = lead.cnae or dados["cnae"]
    lead.cnae_descricao = lead.cnae_descricao or dados["cnae_descricao"]
    lead.segmento = lead.segmento or segmento_por_cnae(dados["cnae"])
    lead.telefone = lead.telefone or limpar_telefone(dados["telefone"])
    lead.email = lead.email or dados["email"]
    lead.municipio = lead.municipio or dados["municipio"]
    lead.uf = lead.uf or dados["uf"]
    lead.endereco = lead.endereco or dados["endereco"]
    lead.capital_social = lead.capital_social or dados["capital_social"]
    lead.situacao_cadastral = lead.situacao_cadastral or dados["situacao"]

    if not lead.contato_nome and dados["socios"]:
        socio = dados["socios"][0]
        lead.contato_nome = socio["nome"]
        lead.contato_cargo = socio["cargo"]
    return lead
