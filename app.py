"""Painel de Prospecção SDR — Norte Geradores (Streamlit).

Rodar local:  python -m streamlit run app.py   → http://localhost:8501
Acesso aberto (sem login). Deploy: Streamlit Community Cloud (secrets).
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from config import (
    GOOGLE_PLACES_QUERIES,
    KEYWORDS_GERADOR,
    SCORE_MORNO,
    SCORE_QUENTE,
    UF_PRIORITARIAS,
    UF_SECUNDARIAS,
)
from prospeccao import export, pipeline
from prospeccao.agendor import enviar_leads
from prospeccao.fontes import FONTES

st.set_page_config(page_title="Prospecção SDR — Norte Geradores",
                   page_icon="⚡", layout="wide")

TODAS_UFS = UF_PRIORITARIAS + UF_SECUNDARIAS + [
    "SP", "RJ", "MG", "ES", "PR", "SC", "RS", "GO", "DF", "CE", "PE",
    "PB", "RN", "AL", "SE", "PI",
]


# --------------------------------------------------------------------------- #
# Sidebar — configuração da busca
# --------------------------------------------------------------------------- #
st.sidebar.header("🔎 Configurar busca")

selecao = st.sidebar.multiselect(
    "Fontes",
    options=list(FONTES.keys()),
    default=["pncp"],
    format_func=lambda k: FONTES[k]["label"],
)
for f in selecao:
    st.sidebar.caption(f"• {FONTES[f]['descricao']}")

ufs = st.sidebar.multiselect("Estados (UF)", options=TODAS_UFS,
                             default=UF_PRIORITARIAS)
limite = st.sidebar.slider("Máx. por termo/fonte", 10, 100, 40, step=10)
enriquecer = st.sidebar.toggle("Enriquecer via Receita Federal", value=True,
                               help="Preenche CNPJ, contato e sócios (mais lento).")
resolver_cnpj = st.sidebar.toggle("Descobrir CNPJ por nome (best-effort)", value=False,
                                  help="Para leads sem CNPJ (Google Places/SIGMINE), "
                                       "busca o CNPJ em fontes gratuitas e confere na "
                                       "Receita. Mais lento e sem garantia — os leads "
                                       "resolvidos vêm marcados como 'confira'.")

with st.sidebar.expander("PNCP — licitações"):
    keywords_txt = st.text_area("Palavras-chave (uma por linha)",
                                value="\n".join(KEYWORDS_GERADOR), height=120)
    pncp_status = st.selectbox("Situação do edital",
                               ["recebendo_proposta", "encerrada", ""], index=0)

with st.sidebar.expander("Google Places / Sympla"):
    municipios_txt = st.text_area("Cidades (uma por linha)",
                                  value="Manaus\nBelém\nPorto Velho", height=90)
    google_queries_txt = st.text_area("Segmentos (Google, um por linha)",
                                      value="\n".join(GOOGLE_PLACES_QUERIES[:5]),
                                      height=110)
    sympla_termo = st.text_input("Termo de evento (Sympla)", value="")

with st.sidebar.expander("CNPJ — lista para enriquecer"):
    cnpjs_txt = st.text_area("CNPJs (um por linha)", value="", height=90)

with st.sidebar.expander("SISLOC — clientes da Norte"):
    sisloc_dias = st.number_input(
        "Parados há ao menos (dias)", min_value=0, max_value=3650, value=0, step=30,
        help="0 = todos. Ex.: 90 traz clientes sem locar há 90+ dias (reativação).")
    sisloc_com_loc = st.toggle("Só quem já locou", value=True,
                               help="Exclui cadastros que nunca locaram.")

with st.sidebar.expander("CCEE/ANEEL — consumidores livres"):
    from prospeccao.fontes import ccee as _ccee
    st.caption(f"Base atual: **{_ccee.total_cache()}** consumidores livres.")
    if st.button("🔄 Atualizar base (ANEEL)", use_container_width=True):
        with st.spinner("Baixando a base de consumidores livres da ANEEL..."):
            qtd = _ccee.atualizar_cache_aneel()
        if qtd:
            st.success(f"Base atualizada: {qtd} consumidores.")
        else:
            st.warning("A ANEEL não expôs a base agora. Tente mais tarde ou importe "
                       "um CSV lista_perfil da CCEE.")

rodar = st.sidebar.button("🚀 Buscar leads", type="primary", use_container_width=True)


# --------------------------------------------------------------------------- #
# Execução
# --------------------------------------------------------------------------- #
def _linhas(txt: str) -> list[str]:
    return [x.strip() for x in txt.splitlines() if x.strip()]


if rodar:
    if not selecao:
        st.warning("Selecione ao menos uma fonte.")
        st.stop()

    params = pipeline.parametros_padrao()
    params.update({
        "ufs": ufs or UF_PRIORITARIAS,
        "municipios": _linhas(municipios_txt),
        "keywords": _linhas(keywords_txt) or list(KEYWORDS_GERADOR),
        "google_queries": _linhas(google_queries_txt),
        "cnpjs": _linhas(cnpjs_txt),
        "pncp_status": pncp_status,
        "sympla_termo": sympla_termo,
        "limite": limite,
        "sisloc_dias_sem_locar": int(sisloc_dias) or None,
        "sisloc_apenas_com_locacao": sisloc_com_loc,
    })

    barra = st.progress(0.0, text="Iniciando...")
    total_passos = max(len(selecao), 1)

    def progresso(fonte: str, n: int):
        idx = min(selecao.index(fonte) + 1, total_passos) if fonte in selecao else total_passos
        barra.progress(idx / total_passos, text=f"{fonte}: {n} leads coletados...")

    with st.spinner("Buscando em fontes públicas e enriquecendo contatos..."):
        df = pipeline.executar(selecao, params, enriquecar=enriquecer,
                               resolver_cnpj=resolver_cnpj, on_progress=progresso)
    barra.empty()
    st.session_state["df"] = df


# --------------------------------------------------------------------------- #
# Resultados
# --------------------------------------------------------------------------- #
df: pd.DataFrame = st.session_state.get("df", pd.DataFrame())

st.title("⚡ Prospecção SDR — Norte Geradores")

if df.empty:
    st.info("Configure as fontes na barra lateral e clique em **Buscar leads**. "
            "Dica: comece pelo PNCP nos estados do Norte — são licitações de "
            "gerador com intenção de compra explícita.")
    st.stop()

r = pipeline.resumo(df)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total de leads", r["total"])
c2.metric("🔥 Quentes", r["quentes"])
c3.metric("🟡 Mornos", r["mornos"])
c4.metric("⚪ Frios", r["frios"])
c5.metric("Com contato", r.get("com_contato", 0))

# Filtros
fc1, fc2, fc3 = st.columns([1, 1, 2])
temp_sel = fc1.multiselect("Temperatura", ["quente", "morno", "frio"],
                           default=["quente", "morno"])
fontes_disp = sorted(df["fonte"].unique())
fonte_sel = fc2.multiselect("Fonte", fontes_disp, default=fontes_disp)
score_min = fc3.slider("Score mínimo", 0, 100, SCORE_MORNO)

visao = df[
    df["temperatura"].isin(temp_sel or ["quente", "morno", "frio"])
    & df["fonte"].isin(fonte_sel or fontes_disp)
    & (df["score"] >= score_min)
]

st.caption(f"Exibindo {len(visao)} de {len(df)} leads "
           f"(quente ≥ {SCORE_QUENTE}, morno ≥ {SCORE_MORNO}).")

st.dataframe(
    visao,
    use_container_width=True, hide_index=True,
    column_config={
        "score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100,
                                                 format="%d"),
        "url": st.column_config.LinkColumn("Link"),
        "valor_estimado": st.column_config.NumberColumn("Valor est.", format="R$ %.0f"),
        "capital_social": st.column_config.NumberColumn("Capital", format="R$ %.0f"),
    },
)

# Exportação
d1, d2, d3 = st.columns(3)
d1.download_button("⬇️ Excel (.xlsx)", export.para_excel(visao),
                   "leads_norte_geradores.xlsx", use_container_width=True,
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
d2.download_button("⬇️ CSV", export.para_csv(visao),
                   "leads_norte_geradores.csv", mime="text/csv",
                   use_container_width=True)

with d3:
    st.write("")
    if st.button("📤 Enviar ao Agendor", use_container_width=True):
        with st.spinner("Criando organizações no Agendor..."):
            res = enviar_leads(visao)
        if res["ok"]:
            st.success(f"Criados: {res['criados']} · Falhas: {res['falhas']}")
            if res["detalhes"]:
                st.expander("Detalhes das falhas").write(res["detalhes"])
        else:
            st.error(res["erro"])
