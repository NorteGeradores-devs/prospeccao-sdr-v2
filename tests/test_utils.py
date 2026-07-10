"""Testes das funções puras (sem rede). Rodar: python -m pytest -q"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from prospeccao.models import Lead
from prospeccao.scoring import pontuar
from prospeccao.utils import (
    chave_dedup,
    cnpj_valido,
    dias_ate_data,
    formatar_cnpj,
    limpar_telefone,
    normalizar_cnae,
    normalizar_texto,
    parse_dinheiro,
    segmento_por_cnae,
)


def test_cnpj_valido():
    assert cnpj_valido("00.000.000/0001-91")
    assert cnpj_valido("00000000000191")
    assert not cnpj_valido("00000000000000")
    assert not cnpj_valido("11222333000100")   # DV errado
    assert not cnpj_valido("123")


def test_formatar_cnpj():
    assert formatar_cnpj("00000000000191") == "00.000.000/0001-91"


def test_limpar_telefone():
    assert limpar_telefone("5592988887777") == "(92) 98888-7777"
    assert limpar_telefone("9233334444") == "(92) 3333-4444"


def test_normalizar_texto():
    assert normalizar_texto("  Mineração   AMAZÔNIA ") == "mineracao amazonia"


def test_segmento_por_cnae():
    assert segmento_por_cnae("4120400") == "Construção Civil"
    assert segmento_por_cnae("0710301") == "Mineração"
    assert segmento_por_cnae("9999999") == ""


def test_normalizar_cnae_preserva_zero_a_esquerda():
    # BrasilAPI devolve cnae_fiscal como int: 0710301 -> 710301
    assert normalizar_cnae(710301) == "0710301"
    assert normalizar_cnae("6422100") == "6422100"
    # o segmento de mineração só aparece com o padding correto
    assert segmento_por_cnae(710301) == "Mineração"


def test_parse_dinheiro_br_e_us():
    assert parse_dinheiro(120000000000) == 120000000000.0
    assert parse_dinheiro("10.000,00") == 10000.0      # formato BR
    assert parse_dinheiro("10000.00") == 10000.0       # formato US (bug antigo: 1.000.000)
    assert parse_dinheiro("R$ 1.234.567,89") == 1234567.89
    assert parse_dinheiro(None) == 0.0
    assert parse_dinheiro("") == 0.0


def test_chave_dedup_nao_funde_homonimos_em_cidades_diferentes():
    k1 = chave_dedup("", "Padaria Central", "Manaus", "AM")
    k2 = chave_dedup("", "Padaria Central", "Belém", "PA")
    assert k1 != k2


def test_chave_dedup_prefere_cnpj():
    k1 = chave_dedup("00000000000191", "Empresa X", "Manaus", "AM")
    k2 = chave_dedup("00.000.000/0001-91", "Nome diferente", "Belém", "PA")
    assert k1 == k2 == "cnpj:00000000000191"


def test_scoring_licitacao_norte_e_quente():
    lead = Lead(fonte="pncp", nome="Prefeitura de Manaus", uf="AM",
                segmento="Setor Público", valor_estimado=800_000, telefone="(92) 3232-3232")
    pontuar(lead)
    assert lead.temperatura == "quente"
    assert lead.score >= 65


def test_pncp_dedup_por_edital_nao_por_orgao():
    # Dois editais distintos do MESMO órgão (mesmo CNPJ) não podem colapsar.
    base = "https://pncp.gov.br/app/editais/00000000000191/2026"
    a = Lead(fonte="pncp", nome="Pref X", cnpj="00000000000191", url=f"{base}/1")
    b = Lead(fonte="pncp", nome="Pref X", cnpj="00000000000191", url=f"{base}/2")
    assert a.chave() != b.chave()


def test_scoring_fonte_combinada_usa_maior_peso():
    # mesclado: max(PESO google_places=10, cnpj=12) = 12, nunca o default 8
    lead = pontuar(Lead(fonte="google_places+cnpj", nome="X"))
    assert any("fonte google_places+cnpj (+12)" in m for m in lead.motivos_score)


def test_dias_ate_data():
    from datetime import date, timedelta
    assert dias_ate_data((date.today() + timedelta(days=5)).isoformat()) == 5
    assert dias_ate_data("2026-07-16T10:00") is not None      # ISO com hora
    assert dias_ate_data("31/12/2020") < 0                    # já passou
    assert dias_ate_data("") is None
    assert dias_ate_data("lixo") is None


def test_scoring_segmento_tiered():
    # mineração vale mais que varejo no bônus de segmento
    minerio = pontuar(Lead(fonte="sigmine", nome="X", segmento="Mineração"))
    varejo = pontuar(Lead(fonte="cnpj", nome="Y", segmento="Varejo / Supermercados"))
    assert any("Mineração (+20)" in m for m in minerio.motivos_score)
    assert any("Varejo / Supermercados (+12)" in m for m in varejo.motivos_score)


def test_scoring_urgencia_prazo_proximo():
    from datetime import date, timedelta
    perto = (date.today() + timedelta(days=3)).isoformat()
    lead = pontuar(Lead(fonte="pncp", nome="Edital", uf="AM", data_evento=perto))
    assert any("prazo em 3d (+12)" in m for m in lead.motivos_score)
