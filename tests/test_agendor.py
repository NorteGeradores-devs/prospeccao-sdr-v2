"""Testes do payload do Agendor — foco na blindagem contra NaN do pandas."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from prospeccao.agendor import _payload, _txt


def test_txt_coage_nan_none_e_numeros():
    assert _txt(float("nan")) == ""
    assert _txt(None) == ""
    assert _txt("  Norte  ") == "Norte"
    assert _txt(87) == "87"


def test_payload_nao_quebra_com_nan_vindo_de_excel():
    # Simula um df lido de .xlsx onde células vazias viram NaN (float, truthy!).
    row = pd.Series({
        "nome": float("nan"), "nome_fantasia": "Norte Geradores",
        "cnpj": "00000000000191", "site": float("nan"),
        "email": "x@y.com", "telefone": "(92) 3232-3232",
        "fonte": "cnpj", "score": 80, "temperatura": "quente",
        "segmento": "Mineração", "uf": "AM", "municipio": "Manaus",
        "contato_nome": float("nan"), "titulo": float("nan"),
        "valor_estimado": float("nan"), "url": float("nan"),
        "observacoes": float("nan"),
    })
    p = _payload(row)
    assert p["name"] == "Norte Geradores"          # cai no fantasia, sem AttributeError
    assert p["cnpj"] == "00.000.000/0001-91"
    assert "website" not in p                       # site NaN não vira "nan"
    assert p["contact"]["email"] == "x@y.com"
    assert p["contact"]["work"] == "9232323232"
    assert "nan" not in p["description"].lower()    # nenhum NaN vazou p/ a descrição
