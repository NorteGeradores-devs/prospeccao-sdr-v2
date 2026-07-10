"""Scoring de leads (0–100) pelo ICP de uma empresa de geradores.

Pontua fit de segmento, região (Norte), porte, existência de contato, situação
cadastral e sinais de intenção (licitação de gerador aberta = forte compra).
"""
from __future__ import annotations

from config import (
    SCORE_MORNO,
    SCORE_QUENTE,
    UF_PRIORITARIAS,
    UF_SECUNDARIAS,
)
from prospeccao.models import Lead

PESO_FONTE = {
    "pncp": 30,            # licitação com objeto "gerador" = intenção explícita
    "sigmine": 18,         # mineração remota, forte consumidor de geração própria
    "sympla": 16,          # evento presencial precisa de energia temporária
    "cnpj": 12,            # empresa do segmento‑alvo
    "google_places": 10,   # negócio do segmento na praça
}


def pontuar(lead: Lead) -> Lead:
    score = 0
    motivos: list[str] = []

    # Lead mesclado tem fonte "a+b" (ex.: google_places+cnpj); usa o MAIOR peso
    # entre as fontes de origem, senão cairia no default e subpontuaria.
    peso = max((PESO_FONTE.get(p, 8) for p in lead.fonte.split("+")), default=8)
    score += peso
    motivos.append(f"fonte {lead.fonte} (+{peso})")

    if lead.segmento:
        score += 15
        motivos.append(f"segmento‑alvo: {lead.segmento} (+15)")

    uf = (lead.uf or "").upper()
    if uf in UF_PRIORITARIAS:
        score += 20
        motivos.append(f"UF prioritária {uf} (+20)")
    elif uf in UF_SECUNDARIAS:
        score += 10
        motivos.append(f"UF secundária {uf} (+10)")

    if lead.telefone:
        score += 8
        motivos.append("tem telefone (+8)")
    if lead.email:
        score += 6
        motivos.append("tem e‑mail (+6)")
    if lead.contato_nome:
        score += 6
        motivos.append("tem contato/sócio (+6)")

    if lead.valor_estimado >= 500_000:
        score += 15
        motivos.append("licitação ≥ R$500k (+15)")
    elif lead.valor_estimado > 0:
        score += 8
        motivos.append("licitação com valor (+8)")

    if lead.capital_social >= 1_000_000:
        score += 8
        motivos.append("capital ≥ R$1M (+8)")

    sit = (lead.situacao_cadastral or "").upper()
    if sit and "ATIVA" in sit:
        score += 5
        motivos.append("CNPJ ativo (+5)")
    elif sit and "ATIVA" not in sit:
        score -= 15
        motivos.append(f"situação '{lead.situacao_cadastral}' (-15)")

    score = max(0, min(100, score))
    lead.score = score
    lead.motivos_score = motivos
    lead.temperatura = (
        "quente" if score >= SCORE_QUENTE
        else "morno" if score >= SCORE_MORNO
        else "frio"
    )
    return lead
