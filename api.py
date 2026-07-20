"""API FastAPI da Prospecção SDR — embrulha o pipeline Python e serve o front React.

Um único serviço: expõe `/api/*` (JSON) e serve o build do React (`web/dist`) em `/`.
Assim não há CORS em produção (mesma origem) e o deploy é um serviço só.

Rodar dev:   uvicorn api:app --reload --port 8000   (React em :5173 faz proxy /api)
Rodar prod:  uvicorn api:app --host 0.0.0.0 --port 8519
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import logging
import os
import time

import pandas as pd
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import (
    APP_PASSWORD,
    KEYWORDS_GERADOR,
    SCORE_MORNO,
    SCORE_QUENTE,
    UF_PRIORITARIAS,
    UF_SECUNDARIAS,
)
from prospeccao import export, pipeline
from prospeccao.agendor import enviar_leads
from prospeccao.fontes import FONTES, ccee
from prospeccao.models import COLUNAS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("prospeccao.api")

app = FastAPI(title="Prospecção SDR — Norte Geradores", docs_url=None, redoc_url=None)

# CORS só para o dev server do Vite (em produção é mesma origem, não usa).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TODAS_UFS = UF_PRIORITARIAS + UF_SECUNDARIAS + [
    "SP", "RJ", "MG", "ES", "PR", "SC", "RS", "GO", "DF",
    "CE", "PE", "PB", "RN", "AL", "SE", "PI",
]


# --------------------------------------------------------------------------- #
# Auth — token HMAC stateless (sobrevive a restart; segredo = APP_PASSWORD)
# --------------------------------------------------------------------------- #
_SECRET = (APP_PASSWORD or "").encode()


def _make_token(horas: int = 12) -> str:
    exp = int(time.time()) + horas * 3600
    sig = base64.urlsafe_b64encode(
        hmac.new(_SECRET, str(exp).encode(), hashlib.sha256).digest()
    ).decode()
    return f"{exp}.{sig}"


def _token_valido(tok: str) -> bool:
    try:
        exp_str, sig = tok.split(".", 1)
        esperado = base64.urlsafe_b64encode(
            hmac.new(_SECRET, exp_str.encode(), hashlib.sha256).digest()
        ).decode()
        return hmac.compare_digest(sig, esperado) and int(exp_str) > time.time()
    except Exception:                                   # noqa: BLE001
        return False


def exigir_auth(authorization: str = Header(default="")) -> None:
    """Dependency: exige Bearer token válido. 503 se o painel não tem senha."""
    if not APP_PASSWORD:
        raise HTTPException(503, "Painel bloqueado: defina APP_PASSWORD no .env/Secrets.")
    tok = authorization.removeprefix("Bearer ").strip()
    if not _token_valido(tok):
        raise HTTPException(401, "Sessão inválida ou expirada.")


# --------------------------------------------------------------------------- #
# Schemas de entrada
# --------------------------------------------------------------------------- #
class LoginIn(BaseModel):
    senha: str


class BuscaIn(BaseModel):
    fontes: list[str]
    ufs: list[str] | None = None
    municipios: list[str] = []
    keywords: list[str] | None = None
    cnpjs: list[str] = []
    google_queries: list[str] | None = None
    pncp_status: str = "recebendo_proposta"
    sympla_termo: str = ""
    limite: int = 40
    enriquecer: bool = True
    resolver_cnpj: bool = False
    sisloc_dias_sem_locar: int | None = None
    sisloc_apenas_com_locacao: bool = False


class ExportIn(BaseModel):
    leads: list[dict]
    formato: str = "xlsx"          # xlsx | csv


class AgendorIn(BaseModel):
    leads: list[dict]
    apenas_temperatura: list[str] | None = None


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _df_para_registros(df: pd.DataFrame) -> list[dict]:
    """DataFrame -> lista de dicts com NaN/tipos numpy tratados (JSON-safe)."""
    if df.empty:
        return []
    return json.loads(df.to_json(orient="records", force_ascii=False))


def _registros_para_df(leads: list[dict]) -> pd.DataFrame:
    """Reconstrói o DataFrame na ordem canônica de colunas (p/ export/Agendor)."""
    if not leads:
        return pd.DataFrame(columns=COLUNAS)
    return pd.DataFrame(leads).reindex(columns=COLUNAS)


# --------------------------------------------------------------------------- #
# Rotas
# --------------------------------------------------------------------------- #
@app.post("/api/login")
def login(body: LoginIn):
    if not APP_PASSWORD:
        raise HTTPException(503, "Painel bloqueado: defina APP_PASSWORD no .env/Secrets.")
    # .strip() tolera espaços colados; compare_digest é tempo-constante.
    if not hmac.compare_digest(body.senha.strip().encode(), APP_PASSWORD.encode()):
        raise HTTPException(401, "Senha incorreta.")
    return {"token": _make_token()}


@app.get("/api/config")
def get_config(_: None = Depends(exigir_auth)):
    return {
        "fontes": [
            {"key": k, "label": v["label"], "descricao": v["descricao"]}
            for k, v in FONTES.items()
        ],
        "ufs_prioritarias": UF_PRIORITARIAS,
        "ufs_secundarias": UF_SECUNDARIAS,
        "todas_ufs": TODAS_UFS,
        "keywords_padrao": list(KEYWORDS_GERADOR),
        "score_quente": SCORE_QUENTE,
        "score_morno": SCORE_MORNO,
        "ccee_total": ccee.total_cache(),
    }


@app.post("/api/buscar")
def buscar(body: BuscaIn, _: None = Depends(exigir_auth)):
    fontes = [f for f in body.fontes if f in FONTES]
    if not fontes:
        raise HTTPException(400, "Selecione ao menos uma fonte válida.")

    params = pipeline.parametros_padrao()
    params.update({
        "ufs": [u.upper() for u in (body.ufs or UF_PRIORITARIAS)],
        "municipios": body.municipios,
        "keywords": body.keywords or list(KEYWORDS_GERADOR),
        "google_queries": body.google_queries or params.get("google_queries", []),
        "cnpjs": body.cnpjs,
        "pncp_status": body.pncp_status,
        "sympla_termo": body.sympla_termo,
        "limite": body.limite,
        "sisloc_dias_sem_locar": body.sisloc_dias_sem_locar,
        "sisloc_apenas_com_locacao": body.sisloc_apenas_com_locacao,
    })

    df = pipeline.executar(fontes, params, enriquecar=body.enriquecer,
                           resolver_cnpj=body.resolver_cnpj)
    return {"leads": _df_para_registros(df), "resumo": pipeline.resumo(df)}


MAX_LEADS = 5000  # teto p/ payloads de export/Agendor (evita trabalho ilimitado)


@app.post("/api/exportar")
def exportar(body: ExportIn, _: None = Depends(exigir_auth)):
    if len(body.leads) > MAX_LEADS:
        raise HTTPException(413, f"Muitos leads (máx. {MAX_LEADS}).")
    df = _registros_para_df(body.leads)
    if body.formato == "csv":
        return Response(
            export.para_csv(df),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="leads_norte_geradores.csv"'},
        )
    return Response(
        export.para_excel(df),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="leads_norte_geradores.xlsx"'},
    )


@app.post("/api/agendor")
def agendor(body: AgendorIn, _: None = Depends(exigir_auth)):
    if len(body.leads) > MAX_LEADS:
        raise HTTPException(413, f"Muitos leads (máx. {MAX_LEADS}).")
    df = _registros_para_df(body.leads)
    return enviar_leads(df, apenas_temperatura=body.apenas_temperatura)


@app.post("/api/ccee/atualizar")
def ccee_atualizar(_: None = Depends(exigir_auth)):
    total = ccee.atualizar_cache_aneel()
    return {"total": total, "ok": total > 0}


@app.get("/api/health")
def health():
    return {"ok": True, "fontes": list(FONTES), "ccee_total": ccee.total_cache()}


# --------------------------------------------------------------------------- #
# Front React (build). Servido por último para não sombrear /api/*.
# --------------------------------------------------------------------------- #
_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web", "dist")
if os.path.isdir(_DIST):
    # html=True serve index.html na raiz; catch-all abaixo cobre o SPA.
    app.mount("/assets", StaticFiles(directory=os.path.join(_DIST, "assets")), name="assets")

    @app.get("/")
    def _root():
        return FileResponse(os.path.join(_DIST, "index.html"))

    _RAIZ = os.path.realpath(_DIST)

    @app.get("/{path:path}")
    def _spa(path: str):
        # Rotas /api desconhecidas devem dar 404 (não servir o index como 200).
        if path.startswith("api/"):
            raise HTTPException(404, "Rota de API não encontrada.")
        index = os.path.join(_RAIZ, "index.html")
        # Contém o caminho dentro do dist (bloqueia path traversal ../).
        alvo = os.path.realpath(os.path.join(_RAIZ, path))
        if os.path.isfile(alvo) and (alvo == _RAIZ or alvo.startswith(_RAIZ + os.sep)):
            return FileResponse(alvo)
        return FileResponse(index)
else:
    @app.get("/")
    def _sem_build():
        return JSONResponse(
            {"msg": "API no ar. Build do React ausente (web/dist). Rode `npm run build` em web/."},
            status_code=200,
        )
