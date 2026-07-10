"""Configuração central da Prospecção SDR — Norte Geradores.

Carrega segredos do .env e define o ICP (perfil de cliente ideal) usado pelas
fontes de busca e pelo scoring: uma empresa de locação/venda de grupos moto
geradores atende quem precisa de energia própria ou de backup — obras,
mineração, saúde, eventos, agro, telecom, indústria, hotelaria e varejo.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _secret(nome: str, padrao: str = "") -> str:
    """Lê um segredo de variável de ambiente (.env local ou Secrets do Streamlit
    Cloud, que também as expõe como env vars). Faz fallback para st.secrets — o
    import é preguiçoso para não pesar no CLI, que usa só o .env."""
    valor = os.getenv(nome)
    if valor is None:
        try:
            import streamlit as st
            valor = st.secrets.get(nome)             # type: ignore[attr-defined]
        except Exception:                            # noqa: BLE001
            valor = None
    return (valor or padrao).strip()


# --------------------------------------------------------------------------- #
# Segredos / credenciais (todos opcionais — cada fonte degrada com elegância)
# --------------------------------------------------------------------------- #
GOOGLE_PLACES_API_KEY = _secret("GOOGLE_PLACES_API_KEY")
SYMPLA_TOKEN = _secret("SYMPLA_TOKEN")
CNPJ_SEARCH_TOKEN = _secret("CNPJ_SEARCH_TOKEN")                    # CNPJá (opcional)
AGENDOR_TOKEN = _secret("AGENDOR_TOKEN")
# Sem senha no .env/secrets o painel fica BLOQUEADO (fail-closed). Não há senha
# padrão embutida no código — defina APP_PASSWORD para liberar o acesso.
APP_PASSWORD = _secret("APP_PASSWORD")

# --------------------------------------------------------------------------- #
# Rede
# --------------------------------------------------------------------------- #
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "25"))
HTTP_RETRIES = int(os.getenv("HTTP_RETRIES", "3"))
USER_AGENT = "NorteGeradores-Prospeccao/1.0 (+comercial@nortegeradores.com.br)"

# Cache em disco (enriquecimento de CNPJ e downloads pesados do SIGMINE)
CACHE_DIR = BASE_DIR / ".cache"
CACHE_TTL_HORAS = int(os.getenv("CACHE_TTL_HORAS", "168"))          # 7 dias

# --------------------------------------------------------------------------- #
# ICP — Perfil de Cliente Ideal
# --------------------------------------------------------------------------- #
# Estados prioritários (a Norte atua na Amazônia/Norte, onde falta rede elétrica
# confiável e a demanda por geração própria é maior).
UF_PRIORITARIAS = ["AM", "PA", "RR", "RO", "AC", "AP", "TO"]
UF_SECUNDARIAS = ["MA", "MT", "MS", "BA"]

# Palavras‑chave para licitações (PNCP) e eventos — objeto ligado a geração.
KEYWORDS_GERADOR = [
    "grupo gerador",
    "grupos geradores",
    "gerador de energia",
    "geradores de energia",
    "moto gerador",
    "motogerador",
    "locação de gerador",
    "locacao de grupo gerador",
    "geração de energia",
    "energia de emergência",
    "usina diesel",
]

# Consultas padrão para o Google Places — segmentos que consomem geradores.
GOOGLE_PLACES_QUERIES = [
    "construtora",
    "mineradora",
    "hospital",
    "produtora de eventos",
    "hotel",
    "supermercado atacadista",
    "frigorífico",
    "provedor de internet",
    "indústria",
    "usina de asfalto",
]

# Prefixos de CNAE → segmento do ICP (usado no scoring e no enriquecimento).
CNAE_SEGMENTOS = {
    "41": "Construção Civil",
    "42": "Construção - Infraestrutura",
    "43": "Construção - Instalações",
    "05": "Mineração",
    "07": "Mineração",
    "08": "Mineração",
    "09": "Mineração",
    "06": "Petróleo e Gás",
    "86": "Saúde / Hospitais",
    "55": "Hotelaria",
    "47": "Varejo / Supermercados",
    "10": "Indústria de Alimentos",
    "01": "Agronegócio",
    "02": "Agronegócio",
    "03": "Agronegócio",
    "61": "Telecom",
    "35": "Energia / Utilities",
    "90": "Eventos e Cultura",
    "93": "Eventos e Lazer",
    "63": "TI / Data Centers",
}

# CNAEs‑alvo para busca por segmento na fonte "CNPJ" (provider CNPJá, opcional).
CNAE_ALVO_BUSCA = [
    "4120400",   # Construção de edifícios
    "4211101",   # Construção de rodovias
    "0710301",   # Extração de minério de ferro
    "0810001",   # Extração de pedra/areia
    "8610101",   # Hospitais
    "5510801",   # Hotéis
    "4711302",   # Supermercados
    "1011201",   # Frigoríficos
    "6110801",   # Telecom por fio / provedores
]

# Situação cadastral desejada (Receita Federal): 02 = ATIVA
SITUACAO_ATIVA = {"02", "ATIVA"}

# Peso por segmento (fit com geração de energia): quem depende mais de energia
# própria/backup pontua mais. Ajuste livre conforme a estratégia comercial.
SEGMENTO_PESO = {
    "Mineração": 20,
    "Petróleo e Gás": 20,
    "Construção Civil": 18,
    "Construção - Infraestrutura": 18,
    "Construção - Instalações": 16,
    "Saúde / Hospitais": 18,
    "TI / Data Centers": 18,
    "Energia / Utilities": 16,
    "Indústria de Alimentos": 14,
    "Agronegócio": 14,
    "Telecom": 14,
    "Eventos e Cultura": 14,
    "Eventos e Lazer": 14,
    "Hotelaria": 12,
    "Varejo / Supermercados": 12,
    "Setor Público / Licitação": 12,
}
SEGMENTO_PESO_PADRAO = 10          # segmento reconhecido, mas fora da lista fina

# Urgência: licitação/evento com data próxima vira prioridade do SDR.
URGENCIA_DIAS = 10                 # ≤ isso = bônus alto; ≤ 30 = bônus menor

# Limiar de score para marcar um lead como "quente".
SCORE_QUENTE = 65
SCORE_MORNO = 40
