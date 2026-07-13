"""Scoring de leads (0–100) pelo ICP de uma empresa de geradores.

Pontua fit de segmento, região (Norte), porte, existência de contato, situação
cadastral e sinais de intenção (licitação de gerador aberta = forte compra).
"""
from __future__ import annotations

from config import (
    SCORE_MORNO,
    SCORE_QUENTE,
    SEGMENTO_PESO,
    SEGMENTO_PESO_PADRAO,
    UF_PRIORITARIAS,
    UF_SECUNDARIAS,
    URGENCIA_DIAS,
)
from prospeccao.models import Lead
from prospeccao.utils import dias_ate_data

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
        peso_seg = SEGMENTO_PESO.get(lead.segmento, SEGMENTO_PESO_PADRAO)
        score += peso_seg
        motivos.append(f"segmento {lead.segmento} (+{peso_seg})")

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

    # Match EXATO com o enum da Receita (ATIVA/BAIXADA/INAPTA/SUSPENSA/NULA):
    # "ATIVA" como substring casaria com "INATIVA" e pontuaria errado.
    sit = (lead.situacao_cadastral or "").strip().upper()
    if sit == "ATIVA":
        score += 5
        motivos.append("CNPJ ativo (+5)")
    elif sit:
        score -= 15
        motivos.append(f"situação '{lead.situacao_cadastral}' (-15)")

    # Urgência: prazo próximo (licitação/evento) = priorizar contato agora.
    dias = dias_ate_data(lead.data_evento)
    if dias is not None and 0 <= dias <= URGENCIA_DIAS:
        score += 12
        motivos.append(f"prazo em {dias}d (+12)")
    elif dias is not None and URGENCIA_DIAS < dias <= 30:
        score += 6
        motivos.append(f"prazo em {dias}d (+6)")

    score = max(0, min(100, score))
    lead.score = score
    lead.motivos_score = motivos
    lead.temperatura = (
        "quente" if score >= SCORE_QUENTE
        else "morno" if score >= SCORE_MORNO
        else "frio"
    )
    return lead
