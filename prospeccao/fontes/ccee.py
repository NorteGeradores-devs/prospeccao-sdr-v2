"""CCEE/ANEEL — consumidores livres do Mercado Livre de Energia como leads.

Premissa de negócio (portada do projeto do David Ladislau): empresa que compra
energia no ACL (Ambiente de Contratação Livre) tem demanda contratada alta
(>500 kW), o que a torna candidata fortíssima à locação de gerador de backup.

Fonte: ANEEL Dados Abertos (CKAN) — dataset "Relação de Consumidores Livres e
Especiais" (grátis). A base é baixada AO VIVO e cacheada em `.cache/` — nenhum
dado é versionado no repositório. Também aceita importação manual de um CSV
lista_perfil da CCEE (fallback quando o CKAN não expõe o CSV direto).

Interface: `buscar(http, ...) -> list[Lead]` (contrato das fontes). Além disso,
expõe `marcar_grande_consumidor(lead)` para o pipeline sinalizar leads de OUTRAS
fontes que também constam como consumidor livre.
"""
from __future__ import annotations

import csv
import io
import json
import logging
import os
import re
import unicodedata

import requests

from config import CACHE_DIR
from prospeccao.models import Lead

log = logging.getLogger("prospeccao")

TIMEOUT = 30
_CACHE_PATH = os.path.join(str(CACHE_DIR), "consumidores_livres.json")

# ANEEL CKAN — portal de Dados Abertos
CKAN_BASE = "https://dadosabertos.aneel.gov.br"
CKAN_SEARCH = f"{CKAN_BASE}/api/3/action/package_search"
CKAN_PACKAGE = f"{CKAN_BASE}/api/3/action/package_show"

# Dataset-alvo: "Beneficiários da CDE — rede básica". São os grandes consumidores
# conectados à rede básica (indústrias, minero-metalurgia, papel/celulose etc.),
# publicados em arquivos ANUAIS com CNPJ+nome+classe. É a MESMA família que o
# projeto do David usava (ele pegou o de 2017); aqui miramos o ano mais recente.
# ⚠️ Não usar package_search fuzzy: ele casa com "subsidios-tarifarios" (errado).
SLUG_BENEFICIARIOS_CDE = "beneficiarios-da-cde"

_CANDIDATOS_CNPJ = ["NumCNPJ", "CNPJ", "NUM_CNPJ", "NR_CNPJ", "NU_CNPJ", "CPF_CNPJ", "NumCnpj", "NrCnpjCpf"]
_CANDIDATOS_NOME = ["NomAgente", "RAZAO_SOCIAL", "RAZAOSOCIAL", "NOME", "NomConsumidor", "SIG_AGENTE", "NOME_AGENTE", "NOME_EMPRESARIAL"]
_CANDIDATOS_UF = ["UF", "SIG_UF", "DSC_ESTADO", "SigUfConsumo", "ESTADO"]
_CANDIDATOS_CLASSE = ["IdcClasseConsumidor", "DscGrupoTarifario", "CLASSE", "CLASSE_CONSUMO", "DSC_CLASSE", "SUBCLASSE", "ATIVIDADE_ECONOMICA", "DSC_RAMO_ATIVIDADE"]
_CANDIDATOS_SUBMERCADO = ["SUBMERCADO", "DSC_SUBMERCADO", "SUB_MERCADO"]
_CANDIDATOS_CONSUMO = ["CONSUMO", "MWH", "CONSUMO_MWH", "CONSUMO_MWMED", "DEMANDA", "DEMANDA_KW"]

_STOPWORDS = {
    "LTDA", "SA", "S", "A", "ME", "EPP", "EIRELI", "LIMITADA",
    "DE", "DO", "DA", "DOS", "DAS", "E", "EM", "RECUPERACAO", "JUDICIAL",
    "CIA", "COMPANHIA", "GRUPO", "INDUSTRIA", "COMERCIO", "IND", "COM",
}


# --------------------------------------------------------------------------- #
# Cache (em .cache/, gitignored — a base é sempre baixada, nunca versionada)
# --------------------------------------------------------------------------- #
def _carregar_cache() -> dict:
    if os.path.exists(_CACHE_PATH):
        try:
            with open(_CACHE_PATH, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"por_cnpj": {}, "por_nome": {}, "meta": {}}


def _salvar_cache(cache: dict) -> None:
    os.makedirs(os.path.dirname(_CACHE_PATH), exist_ok=True)
    tmp = f"{_CACHE_PATH}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=0)
    os.replace(tmp, _CACHE_PATH)          # escrita atômica


# --------------------------------------------------------------------------- #
# Download automático via CKAN (múltiplas estratégias)
# --------------------------------------------------------------------------- #
def _ano_do_recurso(rec: dict) -> int:
    m = re.search(r"(20\d{2})", (rec.get("name") or "") + (rec.get("url") or ""))
    return int(m.group(1)) if m else 0


def _candidatos_urls() -> list[tuple[str, str]]:
    """URLs CSV do dataset beneficiarios-da-cde, do ano mais recente para o mais
    antigo (o parser usa a primeira que der certo)."""
    candidatos: list[tuple[str, str]] = []
    try:
        r = requests.get(CKAN_PACKAGE, params={"id": SLUG_BENEFICIARIOS_CDE}, timeout=TIMEOUT)
        if r.status_code == 200 and r.json().get("success"):
            recs = [rec for rec in r.json()["result"].get("resources", [])
                    if (rec.get("format") or "").upper() in ("CSV", "XLSX", "XLS") and rec.get("url")]
            for rec in sorted(recs, key=_ano_do_recurso, reverse=True):
                candidatos.append((rec["url"], f"{SLUG_BENEFICIARIOS_CDE}/{_ano_do_recurso(rec)}"))
    except Exception as e:                              # noqa: BLE001
        log.debug("package_show %s erro: %s", SLUG_BENEFICIARIOS_CDE, e)
    return candidatos


def _achar_coluna(fieldnames: list[str], candidatos: list[str]) -> str | None:
    normalizados = {c.upper(): c for c in fieldnames}
    for cand in candidatos:
        if cand.upper() in normalizados:
            return normalizados[cand.upper()]
    for cand in candidatos:
        for fn_up, fn_orig in normalizados.items():
            if cand.upper() in fn_up:
                return fn_orig
    return None


def _parsear_resource(url: str) -> list[dict] | None:
    try:
        r = requests.get(url, timeout=120, allow_redirects=True)
        r.raise_for_status()
    except Exception as e:                              # noqa: BLE001
        log.error("Download %s erro: %s", url, e)
        return None

    url_lower = url.lower()
    if url_lower.endswith((".xlsx", ".xls")) or "xlsx" in (r.headers.get("Content-Type") or ""):
        try:
            import pandas as pd
            df = pd.read_excel(io.BytesIO(r.content), dtype=str)
            return df.fillna("").to_dict("records")
        except Exception as e:                          # noqa: BLE001
            log.error("XLSX parse %s: %s", url, e)
            return None

    texto = None
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            texto = r.content.decode(enc)
            if texto.count("�") < 10:
                break
        except Exception:                               # noqa: BLE001
            continue
    if not texto:
        return None
    delim = ";" if texto.count(";") > texto.count(",") else ","
    try:
        return list(csv.DictReader(io.StringIO(texto), delimiter=delim))
    except Exception as e:                              # noqa: BLE001
        log.error("CSV parse erro: %s", e)
        return None


def _linhas_para_cache(linhas: list[dict], origem: str) -> dict | None:
    if not linhas:
        return None
    fieldnames = list(linhas[0].keys())
    col_nome = _achar_coluna(fieldnames, _CANDIDATOS_NOME)
    if not col_nome:
        log.warning("Sem coluna de nome em %s. Campos: %s", origem, fieldnames[:20])
        return None
    col_cnpj = _achar_coluna(fieldnames, _CANDIDATOS_CNPJ)
    col_uf = _achar_coluna(fieldnames, _CANDIDATOS_UF)
    col_classe = _achar_coluna(fieldnames, _CANDIDATOS_CLASSE)
    col_sub = _achar_coluna(fieldnames, _CANDIDATOS_SUBMERCADO)
    col_cons = _achar_coluna(fieldnames, _CANDIDATOS_CONSUMO)

    cache = {"por_cnpj": {}, "por_nome": {}, "meta": {"url": origem, "fonte": "ANEEL"}}
    total = 0
    for row in linhas:
        nome = (row.get(col_nome) or "").strip() if col_nome else ""
        if not nome:
            continue
        cnpj = re.sub(r"\D", "", row.get(col_cnpj) or "") if col_cnpj else ""
        dados = {
            "razao_social": nome,
            "uf": (row.get(col_uf) or "").strip() if col_uf else None,
            "classe": (row.get(col_classe) or "").strip() if col_classe else None,
            "submercado": (row.get(col_sub) or "").strip() if col_sub else None,
            "consumo": (row.get(col_cons) or "").strip() if col_cons else None,
        }
        if len(cnpj) == 14:
            cache["por_cnpj"][cnpj] = dados
            cache["por_nome"][_normalizar(nome)] = cnpj
        else:
            cache["por_nome"][_normalizar(nome)] = None
        total += 1
    cache["meta"]["total"] = total
    return cache if total else None


def atualizar_cache_aneel() -> int:
    """Baixa o dataset de consumidores livres da ANEEL e reconstrói o cache.

    Retorna o total carregado (0 se todas as estratégias falharam). NÃO versiona
    nada — grava só em `.cache/`.
    """
    candidatos = _candidatos_urls()
    if not candidatos:
        log.warning("Nenhum recurso CSV/XLSX encontrado no CKAN ANEEL")
        return 0
    log.info("ANEEL: %d URL(s) candidata(s)", len(candidatos))
    for url, estrategia in candidatos:
        linhas = _parsear_resource(url)
        if not linhas:
            continue
        cache = _linhas_para_cache(linhas, origem=url)
        if not cache:
            continue
        _salvar_cache(cache)
        log.info("Cache ANEEL atualizado: %d consumidores (%s)", cache["meta"]["total"], estrategia)
        return cache["meta"]["total"]
    log.warning("Todas as %d URLs ANEEL falharam", len(candidatos))
    return 0


def importar_ccee_perfil_csv(caminho: str, encoding: str = "latin-1",
                             apenas_ativos: bool = True) -> int:
    """Reconstrói o cache a partir do CSV lista_perfil da CCEE (baixado manualmente).

    Schema esperado:
      CNPJ;NOME_EMPRESARIAL;SIGLA_AGENTE;SIGLAS_PERFIL;SUBMERCADOS;STATUS;QTD_PERFIS;VAREJISTA
    CNPJ vem sem zeros à esquerda (zfill 14); nome vem entre aspas duplas.
    """
    cache = {"por_cnpj": {}, "por_nome": {},
             "meta": {"fonte": "CCEE", "dataset": "lista_perfil", "arquivo": caminho}}
    with open(caminho, encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            status = (row.get("STATUS") or "").strip().upper()
            if apenas_ativos and status != "ATIVO":
                continue
            cnpj_raw = re.sub(r"\D", "", row.get("CNPJ") or "")
            if not cnpj_raw or len(cnpj_raw) > 14:
                continue
            cnpj = cnpj_raw.zfill(14)
            nome = (row.get("NOME_EMPRESARIAL") or "").strip().strip("'\" ").strip()
            if not nome:
                continue
            submercados = [s.strip() for s in (row.get("SUBMERCADOS") or "").split(";") if s.strip()]
            cache["por_cnpj"][cnpj] = {
                "razao_social": nome,
                "uf": None,
                "classe": "Consumidor Livre",
                "submercado": submercados[0] if submercados else None,
                "submercados": submercados if len(submercados) > 1 else None,
                "consumo": None,
                "sigla_agente": (row.get("SIGLA_AGENTE") or "").strip() or None,
                "status": status,
            }
            cache["por_nome"][_normalizar(nome)] = cnpj
    cache["meta"]["total"] = len(cache["por_cnpj"])
    _salvar_cache(cache)
    log.info("Cache CCEE reconstruído: %d empresas", len(cache["por_cnpj"]))
    return len(cache["por_cnpj"])


# --------------------------------------------------------------------------- #
# Lookup
# --------------------------------------------------------------------------- #
def _normalizar(nome: str) -> str:
    nome = unicodedata.normalize("NFKD", nome).encode("ASCII", "ignore").decode("ASCII")
    nome = re.sub(r"[^A-Z0-9 ]", " ", nome.upper())
    return re.sub(r"\s+", " ", nome).strip()


def dados_consumidor(cnpj: str | None = None, nome: str | None = None) -> dict | None:
    cache = _carregar_cache()
    if cnpj:
        cnpj_limpo = re.sub(r"\D", "", cnpj)
        if cnpj_limpo in cache.get("por_cnpj", {}):
            return cache["por_cnpj"][cnpj_limpo]
    if not nome:
        return None
    nome_norm = _normalizar(nome)
    por_nome = cache.get("por_nome", {})
    if nome_norm in por_nome:
        cnpj_hit = por_nome[nome_norm]
        if cnpj_hit and cnpj_hit in cache.get("por_cnpj", {}):
            return cache["por_cnpj"][cnpj_hit]
        return {"razao_social": nome, "cnpj": cnpj_hit}

    tokens_busca = set(nome_norm.split()) - _STOPWORDS
    if len(tokens_busca) < 2:
        return None
    melhor_hit, melhor_score = None, 0
    for nome_cache, cnpj_hit in por_nome.items():
        inter = tokens_busca & (set(nome_cache.split()) - _STOPWORDS)
        if len(inter) >= min(2, len(tokens_busca)) and len(inter) > melhor_score:
            melhor_score, melhor_hit = len(inter), cnpj_hit or nome_cache
    if melhor_hit:
        if isinstance(melhor_hit, str) and len(melhor_hit) == 14 and melhor_hit.isdigit():
            return cache.get("por_cnpj", {}).get(melhor_hit, {"cnpj": melhor_hit})
        return {"razao_social": melhor_hit}
    return None


def eh_grande_consumidor(cnpj: str | None = None, nome: str | None = None) -> bool:
    return dados_consumidor(cnpj=cnpj, nome=nome) is not None


def marcar_grande_consumidor(lead: Lead) -> bool:
    """Sinaliza (no `extra`) se o lead consta como consumidor livre CCEE/ANEEL.

    Usado pelo pipeline para cruzar leads de OUTRAS fontes com a base de energia.
    Retorna True se marcou. No-op silencioso se o cache está vazio.
    """
    dados = dados_consumidor(cnpj=lead.cnpj or None, nome=lead.nome or None)
    if not dados:
        return False
    lead.extra["grande_consumidor_energia"] = True
    if dados.get("classe"):
        lead.extra["energia_classe"] = dados["classe"]
    if dados.get("submercado"):
        lead.extra["energia_submercado"] = dados["submercado"]
    nota = "⚡ Consumidor livre (CCEE/ANEEL)"
    if nota not in (lead.observacoes or ""):
        lead.observacoes = f"{lead.observacoes} | {nota}".strip(" |")
    return True


def total_cache() -> int:
    return len(_carregar_cache().get("por_cnpj", {}))


def precisa_atualizar(max_dias: int = 30) -> bool:
    if total_cache() == 0:
        return True
    if not os.path.exists(_CACHE_PATH):
        return True
    import datetime as _dt
    idade = (_dt.datetime.now() - _dt.datetime.fromtimestamp(os.path.getmtime(_CACHE_PATH))).days
    return idade > max_dias


def submercados_disponiveis() -> list[str]:
    subs = set()
    for dados in _carregar_cache().get("por_cnpj", {}).values():
        if dados.get("submercado"):
            subs.add(dados["submercado"].upper())
        for s in (dados.get("submercados") or []):
            subs.add(s.upper())
    return sorted(subs)


# --------------------------------------------------------------------------- #
# Fonte de leads (contrato do pipeline)
# --------------------------------------------------------------------------- #
def buscar(http, ufs: list[str] | None = None, submercado: str | list[str] | None = None,
           classe: str | list[str] | None = None, limite: int = 500,
           excluir_cnpjs=None, **_ignore) -> list[Lead]:
    """Converte consumidores livres (cache) em Leads prontos.

    `ufs`/`submercado`/`classe` filtram; `limite` limita (0 = sem limite).
    Se o cache está vazio, retorna [] e loga um aviso (rode `atualizar_cache_aneel`).
    """
    excluir = {re.sub(r"\D", "", c) for c in (excluir_cnpjs or []) if c}
    por_cnpj = _carregar_cache().get("por_cnpj", {})
    if not por_cnpj:
        log.warning("Cache CCEE vazio — atualize a base (ANEEL) antes de buscar consumidores livres.")
        return []

    def _norm_set(v):
        if not v:
            return None
        return {v.upper()} if isinstance(v, str) else {x.upper() for x in v}

    ufs_filtro = _norm_set(ufs)
    classes_filtro = _norm_set(classe)
    submercados_filtro = _norm_set(submercado)

    # O dataset da ANEEL (beneficiários CDE) NÃO traz UF — só o CNPJ. Se pedirem
    # filtro de UF mas a base não tem UF, ignoramos o filtro (senão zeraria tudo);
    # a UF real é preenchida depois pelo enriquecimento na Receita.
    if ufs_filtro and not any(d.get("uf") for d in por_cnpj.values()):
        log.info("CCEE: base sem UF — ignorando filtro de UF (será preenchida no enriquecimento).")
        ufs_filtro = None

    leads: list[Lead] = []
    for cnpj, dados in por_cnpj.items():
        if cnpj in excluir:
            continue
        razao = (dados.get("razao_social") or "").strip()
        if not razao:
            continue
        dados_uf = (dados.get("uf") or "").upper()
        dados_classe = (dados.get("classe") or "").upper()
        subs_empresa = set()
        if dados.get("submercado"):
            subs_empresa.add(dados["submercado"].upper())
        for s in (dados.get("submercados") or []):
            subs_empresa.add(s.upper())

        if ufs_filtro and dados_uf not in ufs_filtro:
            continue
        if classes_filtro and not any(c in dados_classe for c in classes_filtro):
            continue
        if submercados_filtro and not (subs_empresa & submercados_filtro):
            continue

        partes = ["⚡ Consumidor livre (CCEE/ANEEL)"]
        if dados.get("classe"):
            partes.append(f"Classe: {dados['classe']}")
        if subs_empresa:
            partes.append(f"Submercado: {', '.join(sorted(subs_empresa))}")
        if dados.get("consumo"):
            partes.append(f"Consumo: {dados['consumo']}")

        leads.append(Lead(
            fonte="ccee",
            nome=razao,
            cnpj=cnpj,
            uf=dados_uf,
            titulo=f"{razao} — Grande consumidor (rede básica)",
            # segmento legível e fixo; a classe numérica da ANEEL vai na descrição.
            # O enriquecimento via Receita refina o segmento pelo CNAE real.
            segmento="Energia / Grande consumidor",
            observacoes=" • ".join(partes),
            url="https://www.ccee.org.br/",
            extra={"grande_consumidor_energia": True,
                   "energia_classe": dados.get("classe"),
                   "energia_submercado": dados.get("submercado")},
        ))
        if limite and len(leads) >= limite:
            break

    log.info("CCEE/ANEEL → %d leads (uf=%s, submercado=%s, classe=%s)",
             len(leads), ufs, submercado, classe)
    return leads
