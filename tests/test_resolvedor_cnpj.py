"""Testes da resolução best-effort de CNPJ por nome (offline, sem rede).

A busca web e a consulta à Receita são monkeypatchadas — aqui validamos a
lógica: extração/validação de CNPJ, similaridade de nome, guarda por UF,
marcação do lead e uso do cache.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from prospeccao import resolvedor_cnpj as rc
from prospeccao.models import Lead

CNPJ_OK = "00000000000191"        # válido (mesmo usado nos outros testes)


def test_extrair_cnpjs_valida_e_deduplica():
    texto = ("contato 00.000.000/0001-91 e também 00000000000191 "
             "mais um falso 11.111.111/1111-11")
    assert rc._extrair_cnpjs(texto) == [CNPJ_OK]      # dedup + descarta DV inválido


def test_similaridade_ignora_forma_juridica():
    # "LTDA"/"S/A" não contam; o núcleo "mineradora norte" bate.
    assert rc._similaridade("Mineradora Norte LTDA", "MINERADORA NORTE S/A") == 1.0
    assert rc._similaridade("Padaria Central", "Auto Posto Sol") == 0.0


def test_tokens_empresa_descarta_stopwords():
    assert rc._tokens_empresa("Comercial de Alimentos e Cia LTDA") == {
        "comercial", "alimentos"}


def _fake_receita(razao, uf=""):
    return lambda cnpj, http: {"razao_social": razao, "nome_fantasia": "",
                               "uf": uf}


def test_resolver_marca_lead_quando_nome_bate(monkeypatch):
    monkeypatch.setattr(rc.cache, "get", lambda *a, **k: None)
    monkeypatch.setattr(rc.cache, "set", lambda *a, **k: None)
    monkeypatch.setattr(rc, "_buscar_web", lambda http, q: f"CNPJ {CNPJ_OK}")
    monkeypatch.setattr(rc, "consultar_cnpj", _fake_receita("MINERADORA NORTE LTDA", "AM"))

    leads = [Lead(fonte="sigmine", nome="Mineradora Norte", uf="AM")]
    resolvidos = rc.resolver_em_lote(leads, http=None)
    assert resolvidos == 1
    assert leads[0].cnpj == CNPJ_OK
    assert "resolvido por nome" in leads[0].observacoes.lower()


def test_resolver_rejeita_nome_divergente(monkeypatch):
    monkeypatch.setattr(rc.cache, "get", lambda *a, **k: None)
    monkeypatch.setattr(rc.cache, "set", lambda *a, **k: None)
    monkeypatch.setattr(rc, "_buscar_web", lambda http, q: f"CNPJ {CNPJ_OK}")
    monkeypatch.setattr(rc, "consultar_cnpj", _fake_receita("SUPERMERCADO XYZ", "AM"))

    lead = Lead(fonte="google_places", nome="Mineradora Norte", uf="AM")
    assert rc.resolver_cnpj(lead, http=None) is None


def test_resolver_rejeita_uf_divergente(monkeypatch):
    monkeypatch.setattr(rc.cache, "get", lambda *a, **k: None)
    monkeypatch.setattr(rc.cache, "set", lambda *a, **k: None)
    monkeypatch.setattr(rc, "_buscar_web", lambda http, q: f"CNPJ {CNPJ_OK}")
    monkeypatch.setattr(rc, "consultar_cnpj", _fake_receita("MINERADORA NORTE LTDA", "SP"))

    lead = Lead(fonte="sigmine", nome="Mineradora Norte", uf="AM")   # AM != SP
    assert rc.resolver_cnpj(lead, http=None) is None


def test_resolver_pula_quem_ja_tem_cnpj(monkeypatch):
    chamou = {"web": 0}
    monkeypatch.setattr(rc.cache, "get", lambda *a, **k: None)
    monkeypatch.setattr(rc.cache, "set", lambda *a, **k: None)

    def _web(http, q):
        chamou["web"] += 1
        return ""
    monkeypatch.setattr(rc, "_buscar_web", _web)

    leads = [Lead(fonte="cnpj", nome="Já tem", cnpj=CNPJ_OK)]
    assert rc.resolver_em_lote(leads, http=None) == 0
    assert chamou["web"] == 0                          # nem tentou buscar


def test_cache_negativo_evita_rebater_busca(monkeypatch):
    store = {}
    monkeypatch.setattr(rc.cache, "get", lambda ns, ch, **k: store.get(ch))
    monkeypatch.setattr(rc.cache, "set", lambda ns, ch, v: store.__setitem__(ch, v))
    chamou = {"web": 0}

    def _web(http, q):
        chamou["web"] += 1
        return ""                                      # nada encontrado
    monkeypatch.setattr(rc, "_buscar_web", _web)

    lead = Lead(fonte="google_places", nome="Empresa Sem Registro", uf="AM")
    assert rc.resolver_cnpj(lead, http=None) is None
    assert rc.resolver_cnpj(lead, http=None) is None   # 2ª vez sai do cache
    assert chamou["web"] == 1                           # buscou só uma vez
