"""Google Places API (New) — Text Search.

Descobre empresas do segmento‑alvo por cidade (construtoras, mineradoras,
hospitais, hotéis, supermercados, indústrias...). Retorna nome, endereço,
telefone e site. NÃO retorna CNPJ — o enriquecimento posterior fica manual
(ou via busca por nome). Requer GOOGLE_PLACES_API_KEY; sem chave, degrada p/ [].
"""
from __future__ import annotations

import logging

from config import GOOGLE_PLACES_API_KEY
from prospeccao.http import HttpClient
from prospeccao.models import Lead
from prospeccao.utils import limpar_telefone, uf_valida

log = logging.getLogger("prospeccao")

URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = ",".join([
    "places.displayName",
    "places.formattedAddress",
    "places.nationalPhoneNumber",
    "places.websiteUri",
    "places.types",
    "places.businessStatus",
    "places.addressComponents",
    "nextPageToken",
])

# tipos do Google → segmento do ICP
TIPO_SEGMENTO = {
    "general_contractor": "Construção Civil",
    "hospital": "Saúde / Hospitais",
    "lodging": "Hotelaria",
    "supermarket": "Varejo / Supermercados",
    "grocery_store": "Varejo / Supermercados",
    "event_venue": "Eventos e Cultura",
}


def buscar(http: HttpClient, queries: list[str], municipios: list[str],
           uf: str = "", max_por_query: int = 40, **_ignore) -> list[Lead]:
    if not GOOGLE_PLACES_API_KEY:
        log.warning("Google Places: sem GOOGLE_PLACES_API_KEY no .env — pulando fonte.")
        return []

    leads: list[Lead] = []
    vistos: set[str] = set()
    headers = {
        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": FIELD_MASK,
        "Content-Type": "application/json",
    }
    for municipio in municipios or [""]:
        for query in queries:
            termo = f"{query} em {municipio}".strip() if municipio else query
            try:
                leads += _text_search(http, headers, termo, query,
                                      max_por_query, vistos)
            except Exception as exc:                   # noqa: BLE001
                log.warning("Google Places falhou para '%s': %s", termo, exc)
    return leads


FECHADOS = {"CLOSED_PERMANENTLY", "CLOSED_TEMPORARILY"}


def _text_search(http, headers, termo, query, limite, vistos) -> list[Lead]:
    coletados: list[Lead] = []
    body = {"textQuery": termo, "languageCode": "pt-BR", "regionCode": "BR",
            "pageSize": 20}
    while len(coletados) < limite:
        resp = http.post(URL, headers=headers, json=body)
        if resp.status_code != 200:
            log.warning("Google Places HTTP %s: %s", resp.status_code, resp.text[:200])
            break
        data = resp.json()
        for place in data.get("places", []):
            if place.get("businessStatus") in FECHADOS:   # não prospectar fechados
                continue
            lead = _parse(place, query)
            chave = f"{lead.nome}|{lead.endereco}".lower()
            if chave in vistos:
                continue
            vistos.add(chave)
            coletados.append(lead)
        token = data.get("nextPageToken")
        if not token or len(coletados) >= limite:
            break
        body["pageToken"] = token
    return coletados


def _parse(place: dict, query: str) -> Lead:
    nome = (place.get("displayName") or {}).get("text", "")
    tipos = place.get("types", []) or []
    segmento = next((TIPO_SEGMENTO[t] for t in tipos if t in TIPO_SEGMENTO), "")

    municipio, uf = "", ""
    for comp in place.get("addressComponents", []) or []:
        kinds = comp.get("types", [])
        if "administrative_area_level_1" in kinds:
            uf = uf_valida(comp.get("shortText") or comp.get("longText")) or uf
        if "administrative_area_level_2" in kinds or "locality" in kinds:
            municipio = municipio or comp.get("longText", "")

    return Lead(
        fonte="google_places",
        nome=nome,
        segmento=segmento,          # vazio se não for segmento‑alvo (não infla o score)
        municipio=municipio,
        uf=uf,                      # vazio se o Places não trouxer a UF (não chutar)
        telefone=limpar_telefone(place.get("nationalPhoneNumber", "")),
        site=place.get("websiteUri", ""),
        endereco=place.get("formattedAddress", ""),
        observacoes=f"Segmento buscado: {query}. Sem CNPJ (Google Places) — "
                    "enriquecer manualmente por nome/razão social.",
    )
