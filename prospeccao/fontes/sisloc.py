"""SISLOC — clientes do ERP de locação da Norte (SQL Server, somente leitura).

Portado do projeto do David Ladislau. É a fonte de maior valor: quem JÁ locou é
o lead mais quente, e clientes parados há X dias são candidatos a reativação.

Conexão read-only reusando o usuário Leitor_norte (mesmo da Preventiva). O
`pyodbc` é importado preguiçosamente — em ambientes sem driver ODBC (ex.:
Streamlit Cloud) o módulo ainda importa, e `buscar` degrada devolvendo [].
"""
from __future__ import annotations

import logging
from contextlib import contextmanager

from config import (
    SISLOC_DATABASE,
    SISLOC_HOST,
    SISLOC_PASSWORD,
    SISLOC_PORT,
    SISLOC_USER,
)
from prospeccao.models import Lead

log = logging.getLogger("prospeccao")

FONTE = "sisloc"

SITUACAO_LABEL = {"N": "Normal", "A": "Alerta", "B": "Bloqueado", "P": "Pendente"}


def _connection_string() -> str:
    if not SISLOC_USER or not SISLOC_PASSWORD:
        raise RuntimeError(
            "Credenciais SISLOC ausentes. Defina SISLOC_USER e SISLOC_PASSWORD no .env/Secrets."
        )
    return (
        "DRIVER={SQL Server};"
        f"SERVER={SISLOC_HOST},{SISLOC_PORT};"
        f"DATABASE={SISLOC_DATABASE};"
        f"UID={SISLOC_USER};PWD={SISLOC_PASSWORD};"
        "TrustServerCertificate=yes;"
    )


@contextmanager
def conectar(timeout: int = 15):
    import pyodbc                          # import preguiçoso: driver pode não existir
    conn = pyodbc.connect(_connection_string(), timeout=timeout, readonly=True)
    try:
        yield conn
    finally:
        conn.close()


def disponivel() -> bool:
    """True se dá para conectar (driver instalado + credenciais presentes)."""
    if not SISLOC_USER or not SISLOC_PASSWORD:
        return False
    try:
        import pyodbc  # noqa: F401
    except ImportError:
        return False
    try:
        with conectar(timeout=8) as cn:
            cn.cursor().execute("SELECT 1")
        return True
    except Exception as e:                  # noqa: BLE001
        log.warning("SISLOC indisponível: %s", e)
        return False


def listar_clientes(apenas_ativos: bool = False, fl_alerta=None, uf=None,
                    dias_sem_locar_min: int | None = None,
                    apenas_com_locacao: bool = False,
                    limite: int | None = None) -> list[dict]:
    """Cadastros marcados como cliente (`fl_cliente_pessoa = 1`), cruzados com a
    última locação (`fich_loc`) e a última mudança de situação."""
    where = ["p.fl_cliente_pessoa = 1"]
    params: list = []

    if apenas_ativos:
        where.append("p.fl_ativo = 'S'")
    if fl_alerta:
        codigos = [fl_alerta] if isinstance(fl_alerta, str) else list(fl_alerta)
        where.append("p.fl_alerta IN (" + ",".join("?" for _ in codigos) + ")")
        params.extend(codigos)
    if uf:
        ufs = [uf] if isinstance(uf, str) else list(uf)
        where.append("p.uf_pessoa IN (" + ",".join("?" for _ in ufs) + ")")
        params.extend(ufs)
    if dias_sem_locar_min is not None:
        where.append(
            "(loc.dt_ult_locacao IS NULL "
            "OR DATEDIFF(day, loc.dt_ult_locacao, CAST(GETDATE() AS date)) >= ?)"
        )
        params.append(int(dias_sem_locar_min))
    if apenas_com_locacao:
        where.append("loc.qtd_locacoes > 0")

    top = f"TOP {int(limite)} " if limite else ""
    sql = f"""
        SELECT {top}
            p.cd_pessoa, p.nm_pessoa, p.nm_fan_pessoa, p.fl_tipo_pessoa,
            p.nr_cnpj_pessoa, p.nr_cpf_pessoa, p.uf_pessoa, p.cidade_pessoa,
            p.bairro_pessoa, p.log_pessoa, p.num_pessoa, p.tel_pessoa, p.tl_cel_pessoa,
            CAST(p.en_mail_pessoa AS varchar(200)) AS email, p.en_site_pessoa,
            p.fl_ativo, p.fl_alerta, p.dt_cad_pessoa,
            DATEDIFF(day,
                COALESCE(ult.dt_ult_situacao, p.dt_atu_cadastro, p.dt_mov, p.dt_cad_pessoa),
                CAST(GETDATE() AS date)) AS dias_no_status,
            loc.dt_ult_locacao, loc.qtd_locacoes,
            CASE WHEN loc.dt_ult_locacao IS NULL THEN NULL
                 ELSE DATEDIFF(day, loc.dt_ult_locacao, CAST(GETDATE() AS date))
            END AS dias_sem_locar
        FROM pessoa p
        OUTER APPLY (
            SELECT TOP 1 s.dt_registro AS dt_ult_situacao
            FROM cad_pessoa_xsituacao s
            WHERE s.cd_pessoa_cli = p.cd_pessoa
            ORDER BY s.dt_registro DESC, s.cd_pessoasituacao DESC
        ) ult
        OUTER APPLY (
            SELECT MAX(f.dt_pedido) AS dt_ult_locacao, COUNT(*) AS qtd_locacoes
            FROM fich_loc f WHERE f.cd_pessoa = p.cd_pessoa
        ) loc
        WHERE {' AND '.join(where)}
        ORDER BY CASE WHEN loc.dt_ult_locacao IS NULL THEN 1 ELSE 0 END,
                 loc.dt_ult_locacao DESC, p.nm_pessoa
    """
    with conectar() as cn:
        cur = cn.cursor()
        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


def _so_digitos(s) -> str:
    return "".join(ch for ch in (s or "") if str(ch).isdigit())


def _cliente_para_lead(c: dict) -> Lead:
    nome = (c.get("nm_pessoa") or "").strip()
    fantasia = (c.get("nm_fan_pessoa") or "").strip()
    cnpj = _so_digitos(c.get("nr_cnpj_pessoa"))
    cpf = _so_digitos(c.get("nr_cpf_pessoa"))
    if c.get("fl_tipo_pessoa") == "F" or (cpf and not cnpj):
        tipo_pessoa = "PF"
    elif cnpj:
        tipo_pessoa = "PJ"
    else:
        tipo_pessoa = None

    ativo = c.get("fl_ativo")
    alerta = c.get("fl_alerta")
    status_label = "Ativo" if ativo == "S" else "Inativo"
    situacao_label = SITUACAO_LABEL.get(alerta, alerta)

    partes = [f"Cliente SISLOC #{c['cd_pessoa']} — {status_label}/{situacao_label}"]
    if c.get("dt_ult_locacao"):
        partes.append(
            f"Última locação: {c['dt_ult_locacao'].strftime('%d/%m/%Y')} "
            f"({c.get('dias_sem_locar')} dias atrás, {c.get('qtd_locacoes')} no total)"
        )
    elif c.get("qtd_locacoes"):
        partes.append(f"{c['qtd_locacoes']} locação(ões) sem data")
    else:
        partes.append("Nunca locou")
    if c.get("dias_no_status"):
        partes.append(f"Há {c['dias_no_status']} dias no status atual")

    endereco = ", ".join(
        p.strip() for p in (c.get("log_pessoa"), c.get("num_pessoa"), c.get("bairro_pessoa"))
        if p and str(p).strip()
    )
    telefone = (c.get("tl_cel_pessoa") or c.get("tel_pessoa") or "").strip()

    return Lead(
        fonte=FONTE,
        nome=nome,
        nome_fantasia=fantasia,
        cnpj=cnpj,
        segmento="Cliente Norte (SISLOC)",
        municipio=(c.get("cidade_pessoa") or "").strip(),
        uf=(c.get("uf_pessoa") or "").strip().upper(),
        telefone=telefone,
        email=(c.get("email") or "").strip(),
        site=(c.get("en_site_pessoa") or "").strip(),
        endereco=endereco,
        titulo=f"{fantasia or nome} — {status_label}/{situacao_label}",
        observacoes=" | ".join(partes),
        extra={
            "cd_pessoa": c["cd_pessoa"],
            "tipo_pessoa": tipo_pessoa,
            "qtd_locacoes": c.get("qtd_locacoes") or 0,
            "dias_sem_locar": c.get("dias_sem_locar"),
            "situacao": alerta,
            "ativo": ativo,
        },
    )


def buscar(http, ufs: list[str] | None = None, limite: int | None = 200,
           apenas_ativos: bool = False, fl_alerta=None,
           dias_sem_locar_min: int | None = None,
           apenas_com_locacao: bool = False, **_ignore) -> list[Lead]:
    """Contrato do pipeline. Devolve clientes do SISLOC como Leads.

    Sem credenciais/driver, loga e devolve [] (não derruba o lote).
    """
    if not SISLOC_USER or not SISLOC_PASSWORD:
        log.warning("SISLOC: credenciais ausentes — pulando (defina SISLOC_USER/SISLOC_PASSWORD).")
        return []
    try:
        clientes = listar_clientes(
            apenas_ativos=apenas_ativos, fl_alerta=fl_alerta, uf=ufs,
            dias_sem_locar_min=dias_sem_locar_min,
            apenas_com_locacao=apenas_com_locacao, limite=limite,
        )
    except ImportError:
        log.warning("SISLOC: driver ODBC/pyodbc indisponível — pulando.")
        return []
    leads = [_cliente_para_lead(c) for c in clientes]
    log.info("SISLOC → %d clientes", len(leads))
    return leads
