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
    "sisloc": 28,          # já é cliente da Norte — relação pré-existente
    "ccee": 24,            # consumidor livre = grande consumidor comprovado
    "sigmine": 18,         # mineração remota, forte consumidor de geração própria
    "sympla": 16,          # evento presencial precisa de energia temporária
    "cnpj": 12,            # empresa do segmento‑alvo
    "google_places": 10,   # negócio do segmento na praça
}


def _sinais_sisloc(lead: Lead, motivos: list[str]) -> int:
    """Bônus/penalidades de cliente SISLOC lidos de lead.extra (portado do David).

    Recompensa recorrência e a janela quente de reativação; penaliza cadastro
    que nunca locou, bloqueado/pendente ou inativo.
    """
    extra = lead.extra
    delta = 0

    qtd = extra.get("qtd_locacoes") or 0
    if qtd >= 50:
        delta += 15; motivos.append("cliente recorrente ≥50 locações (+15)")
    elif qtd >= 10:
        delta += 10; motivos.append("cliente ≥10 locações (+10)")
    elif qtd >= 1:
        delta += 5; motivos.append("cliente com locação (+5)")

    dias = extra.get("dias_sem_locar")
    if dias is not None:
        if 90 <= dias <= 180:
            delta += 12; motivos.append(f"reativação quente ({dias}d parado) (+12)")
        elif 181 <= dias <= 540:
            delta += 8; motivos.append(f"reativação ({dias}d parado) (+8)")
        elif dias > 1095:
            delta -= 5; motivos.append(f"esfriou ({dias}d parado) (-5)")
    else:
        delta -= 3; motivos.append("cadastro nunca locou (-3)")

    situacao = extra.get("situacao")
    if situacao == "B":
        delta -= 10; motivos.append("bloqueado (-10)")
    elif situacao == "P":
        delta -= 3; motivos.append("pendente (-3)")
    if extra.get("ativo") == "N":
        delta -= 5; motivos.append("cadastro inativo (-5)")

    return delta


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

    # Consumidor livre de energia (CCEE/ANEEL) — candidato forte a gerador de
    # backup. Vale para a fonte "ccee" e para leads cruzados de outras fontes.
    if lead.extra.get("grande_consumidor_energia"):
        score += 15
        motivos.append("consumidor livre de energia (+15)")

    # Sinais de cliente SISLOC (recorrência / janela de reativação).
    if "sisloc" in lead.fonte:
        score += _sinais_sisloc(lead, motivos)

    score = max(0, min(100, score))
    lead.score = score
    lead.motivos_score = motivos
    lead.temperatura = (
        "quente" if score >= SCORE_QUENTE
        else "morno" if score >= SCORE_MORNO
        else "frio"
    )
    return lead
