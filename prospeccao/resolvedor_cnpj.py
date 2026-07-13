"""Resolução best-effort de CNPJ a partir do nome da empresa (fontes gratuitas).

Google Places e SIGMINE trazem o NOME da empresa, mas não o CNPJ — sem CNPJ o
enriquecimento pela Receita não roda. Este módulo tenta descobrir o CNPJ de graça,
com uma trava forte contra falso-positivo:

  1. busca web gratuita (DuckDuckGo HTML, sem chave) por  "<nome>" <cidade> <uf> CNPJ;
  2. extrai CNPJs candidatos do resultado e VALIDA o dígito verificador;
  3. confere cada candidato na Receita (BrasilAPI, já cacheada) e só ACEITA se a
     razão social/fantasia bate com o nome do lead (similaridade de tokens) e a UF
     confere — isso evita colar um CNPJ homônimo de outra cidade/empresa.

É "melhor esforço": a busca gratuita é frágil e pode não achar nada. Quando acha,
o lead ganha uma observação "confira" para o SDR validar antes de usar. Todo o
resultado (inclusive negativo) é cacheado por nome para não rebater o buscador.
"""
from __future__ import annotations

import logging
import re
import time

from config import RESOLVER_CNPJ_MAX, RESOLVER_CNPJ_SIMILARIDADE_MIN
from prospeccao import cache
from prospeccao.enriquecimento import consultar_cnpj
from prospeccao.http import HttpClient
from prospeccao.models import Lead
from prospeccao.utils import cnpj_valido, normalizar_texto, so_digitos, uf_valida

log = logging.getLogger("prospeccao")

DDG_HTML = "https://html.duckduckgo.com/html/"
DDG_LITE = "https://lite.duckduckgo.com/lite/"
_PAUSA_BUSCA = 0.4      # freia só buscas reais; cache hit não passa por _buscar_web

_RE_CNPJ_FMT = re.compile(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}")   # 00.000.000/0001-91
_RE_CNPJ_BARE = re.compile(r"\b\d{14}\b")                       # 00000000000191

# Formas jurídicas e conectivos que não ajudam a distinguir a empresa.
_STOP_EMPRESA = {
    "ltda", "sa", "s", "a", "eireli", "me", "epp", "mei", "cia", "ltd",
    "e", "de", "do", "da", "dos", "das", "em", "the",
}


def _tokens_empresa(nome: str | None) -> set[str]:
    """Tokens significativos do nome (sem acento, sem forma jurídica, >1 char)."""
    txt = re.sub(r"[^\w\s]", " ", normalizar_texto(nome))
    return {t for t in txt.split() if len(t) > 1 and t not in _STOP_EMPRESA}


def _similaridade(a: str | None, b: str | None) -> float:
    """Coeficiente de sobreposição entre dois nomes de empresa (0..1).

    |A∩B| / min(|A|,|B|): tolera que a razão social da Receita seja mais longa
    ou mais curta que o nome coletado na fonte.
    """
    ta, tb = _tokens_empresa(a), _tokens_empresa(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / min(len(ta), len(tb))


def _extrair_cnpjs(texto: str) -> list[str]:
    """CNPJs válidos encontrados no texto (formatados primeiro), sem repetir."""
    achados: list[str] = []
    for bruto in _RE_CNPJ_FMT.findall(texto) + _RE_CNPJ_BARE.findall(texto):
        n = so_digitos(bruto)
        if cnpj_valido(n) and n not in achados:
            achados.append(n)
    return achados


def _buscar_web(http: HttpClient, consulta: str) -> str:
    """HTML de um buscador gratuito para a consulta, ou "" em qualquer falha."""
    time.sleep(_PAUSA_BUSCA)                             # throttle só de busca real
    for url in (DDG_HTML, DDG_LITE):
        try:
            resp = http.post(url, data={"q": consulta, "kl": "br-pt"}, timeout=15)
            if resp.status_code == 200 and resp.text:
                return resp.text
        except Exception as exc:                        # noqa: BLE001
            log.debug("Busca web falhou (%s): %s", url, exc)
    return ""


def _resolver_online(nome: str, municipio: str, uf: str, http: HttpClient) -> dict | None:
    """Descobre e verifica o CNPJ. Retorna {'cnpj','similaridade'} ou None."""
    # Aspas no nome ajudam o buscador a fixar a razão social exata.
    consulta = " ".join(p for p in (f'"{nome}"', municipio, uf, "CNPJ") if p).strip()
    html = _buscar_web(http, consulta)
    if not html:
        return None

    melhor: dict | None = None
    for cnpj in _extrair_cnpjs(html)[:5]:
        dados = consultar_cnpj(cnpj, http)              # BrasilAPI, cacheado
        if not dados:
            continue
        # Guarda contra homônimo em outra UF (só quando ambas as UFs são conhecidas).
        if uf and dados.get("uf") and uf_valida(uf) != uf_valida(dados["uf"]):
            continue
        sim = max(_similaridade(nome, dados.get("razao_social")),
                  _similaridade(nome, dados.get("nome_fantasia")))
        if sim >= RESOLVER_CNPJ_SIMILARIDADE_MIN and (
                melhor is None or sim > melhor["similaridade"]):
            melhor = {"cnpj": cnpj, "similaridade": round(sim, 2)}
    return melhor


def resolver_cnpj(lead: Lead, http: HttpClient) -> dict | None:
    """Tenta resolver o CNPJ de um lead pelo nome. Não muta o lead.

    Retorna {'cnpj','similaridade'} quando encontra com confiança, senão None.
    Resultado é cacheado por (nome|município|uf), inclusive o negativo.
    """
    nome = (lead.nome or "").strip()
    if lead.cnpj or not _tokens_empresa(nome):
        return None

    chave = normalizar_texto(f"{nome}|{lead.municipio}|{lead.uf}")
    cacheado = cache.get("resolvido_cnpj", chave)
    if cacheado is not None:
        return cacheado or None                          # {} = negativo cacheado

    achado = _resolver_online(nome, lead.municipio, lead.uf, http)
    cache.set("resolvido_cnpj", chave, achado or {})
    return achado


def resolver_em_lote(leads: list[Lead], http: HttpClient,
                     on_progress=None, total: int = 0,
                     max_tentativas: int = RESOLVER_CNPJ_MAX) -> int:
    """Resolve CNPJ (best-effort) dos leads sem CNPJ. Retorna quantos resolveu.

    Mantém sequencial e com pausa curta para ser educado com o buscador gratuito;
    é opt-in justamente por ser mais lento que o resto do pipeline.
    """
    alvos = [l for l in leads if not l.cnpj and _tokens_empresa(l.nome)][:max_tentativas]
    if not alvos:
        return 0

    resolvidos = 0
    for i, lead in enumerate(alvos, 1):
        try:
            achado = resolver_cnpj(lead, http)
        except Exception as exc:                          # noqa: BLE001
            log.warning("Resolução de CNPJ falhou p/ %r: %s", lead.nome, exc)
            achado = None
        if achado:
            lead.cnpj = achado["cnpj"]
            nota = (f"CNPJ resolvido por nome (best-effort, "
                    f"sim={achado['similaridade']:.0%}) — confira.")
            lead.observacoes = f"{lead.observacoes} | {nota}" if lead.observacoes else nota
            resolvidos += 1
        if on_progress and i % 5 == 0:
            on_progress(f"resolvendo CNPJ ({i}/{len(alvos)})", total)
    return resolvidos
