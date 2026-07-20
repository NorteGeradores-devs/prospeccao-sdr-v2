"""Testes da fonte SISLOC (offline — sem pyodbc/rede; só a lógica pura)."""
from __future__ import annotations

from datetime import date, datetime

from prospeccao.fontes import sisloc
from prospeccao.models import Lead


def _cliente(**over) -> dict:
    base = {
        "cd_pessoa": 123,
        "nm_pessoa": "CONSTRUTORA NORTE LTDA",
        "nm_fan_pessoa": "Norte Obras",
        "fl_tipo_pessoa": "J",
        "nr_cnpj_pessoa": "00.000.000/0001-91",
        "nr_cpf_pessoa": None,
        "uf_pessoa": "am",
        "cidade_pessoa": "Manaus",
        "bairro_pessoa": "Centro",
        "log_pessoa": "Rua A",
        "num_pessoa": "100",
        "tel_pessoa": "9233334444",
        "tl_cel_pessoa": "92999998888",
        "email": "contato@norteobras.com",
        "en_site_pessoa": "",
        "fl_ativo": "S",
        "fl_alerta": "N",
        "dt_cad_pessoa": date(2020, 1, 1),
        "dias_no_status": 30,
        "dt_ult_locacao": datetime(2026, 1, 10),
        "qtd_locacoes": 12,
        "dias_sem_locar": 120,
    }
    base.update(over)
    return base


def test_cliente_para_lead_mapeia_campos_e_extra():
    lead = sisloc._cliente_para_lead(_cliente())
    assert isinstance(lead, Lead)
    assert lead.fonte == "sisloc"
    assert lead.cnpj == "00000000000191"          # só dígitos
    assert lead.uf == "AM"                          # normalizado p/ maiúsculo
    assert lead.telefone == "92999998888"           # celular tem prioridade
    assert lead.nome_fantasia == "Norte Obras"
    assert lead.extra["qtd_locacoes"] == 12
    assert lead.extra["dias_sem_locar"] == 120
    assert lead.extra["tipo_pessoa"] == "PJ"
    assert "Última locação" in lead.observacoes


def test_cliente_nunca_locou():
    lead = sisloc._cliente_para_lead(
        _cliente(dt_ult_locacao=None, qtd_locacoes=0, dias_sem_locar=None))
    assert lead.extra["qtd_locacoes"] == 0
    assert lead.extra["dias_sem_locar"] is None
    assert "Nunca locou" in lead.observacoes


def test_pessoa_fisica_detectada():
    lead = sisloc._cliente_para_lead(
        _cliente(fl_tipo_pessoa="F", nr_cnpj_pessoa=None, nr_cpf_pessoa="12345678909"))
    assert lead.extra["tipo_pessoa"] == "PF"
    assert lead.cnpj == ""


def test_buscar_sem_credenciais_retorna_vazio(monkeypatch):
    monkeypatch.setattr(sisloc, "SISLOC_USER", "")
    monkeypatch.setattr(sisloc, "SISLOC_PASSWORD", "")
    assert sisloc.buscar(http=None) == []


def test_buscar_converte_clientes(monkeypatch):
    monkeypatch.setattr(sisloc, "SISLOC_USER", "u")
    monkeypatch.setattr(sisloc, "SISLOC_PASSWORD", "p")
    monkeypatch.setattr(sisloc, "listar_clientes",
                        lambda **kw: [_cliente(), _cliente(cd_pessoa=456)])
    leads = sisloc.buscar(http=None, ufs=["AM"])
    assert len(leads) == 2
    assert all(l.fonte == "sisloc" for l in leads)


def test_buscar_driver_ausente_degrada(monkeypatch):
    monkeypatch.setattr(sisloc, "SISLOC_USER", "u")
    monkeypatch.setattr(sisloc, "SISLOC_PASSWORD", "p")

    def _boom(**kw):
        raise ImportError("no pyodbc")

    monkeypatch.setattr(sisloc, "listar_clientes", _boom)
    assert sisloc.buscar(http=None) == []
