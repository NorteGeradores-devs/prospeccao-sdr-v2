"""Conectores de fontes públicas de leads.

Cada módulo expõe uma função `buscar(http, **params) -> list[Lead]`.
O dicionário FONTES abaixo é o registro usado pelo pipeline e pela UI.
"""
from prospeccao.fontes import ccee, cnpj, google_places, pncp, sigmine, sisloc, sympla

FONTES = {
    "pncp": {
        "buscar": pncp.buscar,
        "label": "PNCP — Licitações públicas",
        "descricao": "Editais com objeto ligado a geradores (compra/locação).",
    },
    "sisloc": {
        "buscar": sisloc.buscar,
        "label": "SISLOC — Clientes da Norte (ERP)",
        "descricao": "Clientes que já locaram; inclui parados há X dias (reativação).",
    },
    "ccee": {
        "buscar": ccee.buscar,
        "label": "CCEE/ANEEL — Consumidores livres de energia",
        "descricao": "Grandes consumidores do mercado livre (candidatos a backup).",
    },
    "google_places": {
        "buscar": google_places.buscar,
        "label": "Google Places — Empresas na praça",
        "descricao": "Negócios do segmento‑alvo por cidade (requer API key).",
    },
    "cnpj": {
        "buscar": cnpj.buscar,
        "label": "CNPJ — Empresas por segmento/lista",
        "descricao": "Busca por CNAE (CNPJá) ou enriquece uma lista de CNPJs.",
    },
    "sympla": {
        "buscar": sympla.buscar,
        "label": "Sympla — Eventos",
        "descricao": "Eventos presenciais que demandam energia temporária.",
    },
    "sigmine": {
        "buscar": sigmine.buscar,
        "label": "SIGMINE/ANM — Mineração",
        "descricao": "Titulares de processos minerários por UF.",
    },
}
