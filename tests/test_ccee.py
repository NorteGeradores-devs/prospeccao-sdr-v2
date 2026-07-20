"""Testes da fonte CCEE/ANEEL (offline — cache monkeypatchado, sem rede)."""
from __future__ import annotations

import pytest

from prospeccao.fontes import ccee
from prospeccao.models import Lead

CACHE_FAKE = {
    "por_cnpj": {
        "33592510000154": {"razao_social": "VALE S.A.", "uf": "PA",
                           "classe": "Consumidor Livre", "submercado": "NORTE"},
        "60510195000141": {"razao_social": "MINERACAO MATHEUS LEME LTDA", "uf": "MG",
                           "classe": "Consumidor Livre", "submercado": "SUDESTE"},
    },
    "por_nome": {
        "VALE": "33592510000154",
        "MINERACAO MATHEUS LEME": "60510195000141",
    },
    "meta": {"total": 2},
}


@pytest.fixture(autouse=True)
def _cache(monkeypatch):
    monkeypatch.setattr(ccee, "_carregar_cache", lambda: CACHE_FAKE)


def test_normalizar_remove_acento_e_forma_juridica():
    assert ccee._normalizar("Mineração  Matheus Leme Ltda.") == "MINERACAO MATHEUS LEME LTDA"


def test_dados_consumidor_por_cnpj():
    d = ccee.dados_consumidor(cnpj="33.592.510/0001-54")
    assert d and d["razao_social"] == "VALE S.A."


def test_eh_grande_consumidor_por_nome():
    # match exato normalizado (token único só casa exato — evita falso positivo)
    assert ccee.eh_grande_consumidor(nome="Vale") is True
    # match fuzzy por tokens (≥2 tokens em comum, ignora forma jurídica)
    assert ccee.eh_grande_consumidor(nome="Mineração Matheus Leme S/A") is True
    assert ccee.eh_grande_consumidor(nome="Padaria do Zé") is False


def test_buscar_devolve_leads_flagados_e_filtra_uf():
    leads = ccee.buscar(http=None, ufs=["PA"])
    assert len(leads) == 1
    lead = leads[0]
    assert isinstance(lead, Lead)
    assert lead.fonte == "ccee"
    assert lead.cnpj == "33592510000154"
    assert lead.extra.get("grande_consumidor_energia") is True


def test_buscar_cache_vazio_retorna_lista_vazia(monkeypatch):
    monkeypatch.setattr(ccee, "_carregar_cache",
                        lambda: {"por_cnpj": {}, "por_nome": {}, "meta": {}})
    assert ccee.buscar(http=None) == []


def test_marcar_grande_consumidor_seta_extra_e_observacao():
    lead = Lead(fonte="cnpj", nome="VALE S.A.", cnpj="33592510000154")
    assert ccee.marcar_grande_consumidor(lead) is True
    assert lead.extra["grande_consumidor_energia"] is True
    assert "Consumidor livre" in lead.observacoes
    # Idempotente: não duplica a observação
    ccee.marcar_grande_consumidor(lead)
    assert lead.observacoes.count("Consumidor livre") == 1


def test_marcar_nao_altera_lead_desconhecido():
    lead = Lead(fonte="cnpj", nome="Empresa Fantasma", cnpj="99999999999999")
    assert ccee.marcar_grande_consumidor(lead) is False
    assert "grande_consumidor_energia" not in lead.extra
