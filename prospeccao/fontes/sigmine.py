"""SIGMINE / ANM — processos minerários por UF.

Mineração acontece em áreas remotas, quase sempre fora da rede elétrica: forte
consumidora de grupos geradores. Este conector baixa os dados abertos da ANM
(shapefile por UF), lê os atributos (sem geometria) e transforma cada TITULAR
em um lead, agregando quantos processos e quais substâncias ele detém.

Dados: https://dadosabertos.anm.gov.br/SIGMINE/PROCESSOS_MINERARIOS/{UF}.zip
Leitura via pyshp (leve, sem dependências geoespaciais pesadas).
"""
from __future__ import annotations

import io
import logging
import zipfile

from prospeccao import cache
from prospeccao.http import HttpClient
from prospeccao.models import Lead
from prospeccao.utils import normalizar_texto, uf_valida

log = logging.getLogger("prospeccao")

BASE_ANM = "https://dadosabertos.anm.gov.br/SIGMINE/PROCESSOS_MINERARIOS/{uf}.zip"

# Campos candidatos (variam entre camadas/versões do SIGMINE).
CAMPOS_TITULAR = ["NOME", "TITULAR", "NM_TITULAR"]
CAMPOS_SUBS = ["SUBS", "SUBSTANCIA", "DSSubstanc"]
CAMPOS_FASE = ["FASE", "DSProcesso", "ULT_EVENTO"]


def buscar(http: HttpClient, ufs: list[str], max_por_uf: int = 40,
           **_ignore) -> list[Lead]:
    try:
        import shapefile  # noqa: F401  (pyshp)
    except ImportError:
        log.warning("SIGMINE: pyshp não instalado (pip install pyshp) — pulando.")
        return []

    leads: list[Lead] = []
    for uf in [u.upper() for u in (ufs or [])]:
        if not uf_valida(uf):        # UF entra em URL e nome de arquivo de cache
            log.warning("SIGMINE: UF inválida ignorada: %r", uf)
            continue
        try:
            leads += _processar_uf(http, uf, max_por_uf)
        except Exception as exc:                       # noqa: BLE001
            log.warning("SIGMINE falhou para %s: %s", uf, exc)
    return leads


def _baixar_zip(http: HttpClient, uf: str):
    """Baixa (e cacheia em disco) o zip da UF. Retorna o caminho local ou None."""
    destino = cache.caminho_arquivo("sigmine", f"{uf}.zip")   # uf já validada
    if not destino.exists() or destino.stat().st_size == 0:
        log.info("SIGMINE: baixando processos minerários de %s...", uf)
        resp = http.get(BASE_ANM.format(uf=uf), timeout=180)
        if resp.status_code != 200 or not resp.content:
            log.warning("SIGMINE: download de %s retornou HTTP %s", uf, resp.status_code)
            return None
        destino.write_bytes(resp.content)
    return destino


def _processar_uf(http: HttpClient, uf: str, limite: int) -> list[Lead]:
    import shapefile

    caminho = _baixar_zip(http, uf)
    if caminho is None:
        return []

    try:
        with zipfile.ZipFile(caminho) as zf:            # fecha o handle ao sair
            dbf = next((n for n in zf.namelist() if n.lower().endswith(".dbf")), None)
            if not dbf:
                log.warning("SIGMINE: nenhum .dbf dentro de %s.zip", uf)
                return []
            # Só os atributos importam (titular/substância/fase); ler apenas o
            # .dbf evita carregar a geometria (.shp/.shx) na memória.
            # O .dbf da ANM é UTF-8 (latin-1 gera mojibake em "MINERAÇÃO").
            reader = shapefile.Reader(
                dbf=io.BytesIO(zf.read(dbf)),
                encoding="utf-8", encodingErrors="replace",
            )
    except zipfile.BadZipFile:
        caminho.unlink(missing_ok=True)
        return []

    campos = [f[0] for f in reader.fields[1:]]           # ignora DeletionFlag

    def idx(cands):
        return next((campos.index(c) for c in cands if c in campos), None)

    i_tit, i_sub, i_fase = idx(CAMPOS_TITULAR), idx(CAMPOS_SUBS), idx(CAMPOS_FASE)
    if i_tit is None:
        log.warning("SIGMINE %s: campo de titular não encontrado em %s", uf, campos)
        return []

    agregado: dict[str, dict] = {}
    for rec in reader.iterRecords():
        titular = str(rec[i_tit] or "").strip()
        if not titular or normalizar_texto(titular) in ("disponibilidade", "dnpm"):
            continue
        ag = agregado.setdefault(titular, {"processos": 0, "subs": set(), "fase": ""})
        ag["processos"] += 1
        if i_sub is not None and rec[i_sub]:
            ag["subs"].add(str(rec[i_sub]).strip())
        if i_fase is not None and not ag["fase"] and rec[i_fase]:
            ag["fase"] = str(rec[i_fase]).strip()

    ranking = sorted(agregado.items(), key=lambda kv: kv[1]["processos"], reverse=True)
    leads = []
    for titular, ag in ranking[:limite]:
        subs = ", ".join(sorted(ag["subs"])[:5]) or "n/d"
        leads.append(Lead(
            fonte="sigmine",
            nome=titular,
            uf=uf,
            segmento="Mineração",
            titulo=f"{ag['processos']} processo(s) minerário(s) — {subs}",
            observacoes=f"Titular ANM em {uf}. Fase: {ag['fase'] or 'n/d'}. "
                        "Sem CNPJ na base — enriquecer por razão social.",
        ))
    return leads
