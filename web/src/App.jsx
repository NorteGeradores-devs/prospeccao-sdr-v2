import { useEffect, useMemo, useRef, useState } from 'react'
import { api, getToken, clearToken, AuthError } from './api.js'
import LoginScreen from './components/LoginScreen.jsx'
import SearchConfig, { buildBusca } from './components/SearchConfig.jsx'
import MetricsBand from './components/MetricsBand.jsx'
import FiltersBar from './components/FiltersBar.jsx'
import LeadsTable from './components/LeadsTable.jsx'
import LeadDrawer from './components/LeadDrawer.jsx'
import SelectionBar from './components/SelectionBar.jsx'
import Toast from './components/Toast.jsx'
import { fonteLabel } from './lib/format.js'
import { beacon } from './motion.js'

const FILTROS_INICIAIS = { temp: 'todos', fontes: [], scoreMin: 0, q: '' }

function defaultParams(cfg) {
  return {
    fontes: ['pncp'],
    ufs: [...cfg.ufs_prioritarias],
    limite: 40,
    enriquecer: true,
    resolver_cnpj: false,
    pncp_status: 'recebendo_proposta',
    keywords: (cfg.keywords_padrao || []).join('\n'),
    cidades: 'Manaus\nBelém\nPorto Velho',
    google_queries: '',
    sympla_termo: '',
    cnpjs: '',
    sisloc_dias_ativo: false,
    sisloc_dias: 180,
    sisloc_apenas_com_locacao: true,
  }
}

export default function App() {
  const [authed, setAuthed] = useState(() => !!getToken())
  const [config, setConfig] = useState(null)
  const [params, setParams] = useState(null)

  const [mostrarConfig, setMostrarConfig] = useState(true)
  const [buscando, setBuscando] = useState(false)
  const [resultado, setResultado] = useState(null) // {leads, resumo}
  const [runId, setRunId] = useState(0)

  const [filtros, setFiltros] = useState(FILTROS_INICIAIS)
  const [sort, setSort] = useState({ key: 'score', dir: 'desc' })
  const [selecionados, setSelecionados] = useState(() => new Set())
  const [drawerLead, setDrawerLead] = useState(null)
  const [focusedId, setFocusedId] = useState(null)
  const [cceeBusy, setCceeBusy] = useState(false)
  const [cceeTotal, setCceeTotal] = useState(0)
  const [toasts, setToasts] = useState([])

  const buscaRef = useRef(null)
  const beaconRef = useRef(null)

  const addToast = (t) => {
    const id = Date.now() + Math.random()
    setToasts((ts) => [...ts, { id, ...t }])
    setTimeout(() => setToasts((ts) => ts.filter((x) => x.id !== id)), 3600)
  }

  // Carrega config ao autenticar
  useEffect(() => {
    if (!authed) return
    let vivo = true
    api.config()
      .then((cfg) => {
        if (!vivo) return
        setConfig(cfg)
        setParams(defaultParams(cfg))
        setCceeTotal(cfg.ccee_total || 0)
      })
      .catch((e) => {
        if (e instanceof AuthError) { setAuthed(false) }
        else addToast({ kind: 'error', title: 'Falha ao carregar', msg: e.message })
      })
    return () => { vivo = false }
  }, [authed])

  useEffect(() => {
    const a = beacon(beaconRef.current)
    return () => a && a.pause()
  }, [config])

  function logout() {
    clearToken()
    setAuthed(false)
    setConfig(null)
    setResultado(null)
  }

  async function onBuscar(busca) {
    if (!busca.fontes.length) return
    setBuscando(true)
    setSelecionados(new Set())
    try {
      const r = await api.buscar(busca)
      const leads = (r.leads || []).map((l, i) => ({ ...l, _id: i }))
      setResultado({ leads, resumo: r.resumo || {} })
      setFiltros(FILTROS_INICIAIS)
      setSort({ key: 'score', dir: 'desc' })
      setRunId((n) => n + 1)
      setMostrarConfig(false)
      setFocusedId(leads.length ? leads[0]._id : null)
      if (!leads.length) addToast({ kind: 'info', title: 'Nenhum lead', msg: 'Ajuste as fontes ou a região.' })
    } catch (e) {
      if (e instanceof AuthError) return logout()
      addToast({ kind: 'error', title: 'Busca falhou', msg: e.message })
    } finally {
      setBuscando(false)
    }
  }

  async function atualizarCcee() {
    setCceeBusy(true)
    try {
      const r = await api.atualizarCcee()
      setCceeTotal(r.total || 0)
      addToast(r.ok
        ? { kind: 'success', title: 'Base CCEE atualizada', msg: `${r.total} consumidores livres.` }
        : { kind: 'error', title: 'Falhou', msg: 'A ANEEL não respondeu agora. Tente mais tarde.' })
    } catch (e) {
      if (e instanceof AuthError) return logout()
      addToast({ kind: 'error', title: 'Erro', msg: e.message })
    } finally {
      setCceeBusy(false)
    }
  }

  // ---- filtros + ordenação ----
  const baseFontes = (f) => String(f || '').split('+')
  const fontesDisponiveis = useMemo(() => {
    if (!resultado) return []
    const s = new Set()
    resultado.leads.forEach((l) => baseFontes(l.fonte).forEach((f) => s.add(f)))
    return [...s].sort()
  }, [resultado])

  const filtrados = useMemo(() => {
    if (!resultado) return []
    const q = filtros.q.trim().toLowerCase()
    const arr = resultado.leads.filter((l) =>
      (filtros.temp === 'todos' || l.temperatura === filtros.temp) &&
      (Number(l.score) >= filtros.scoreMin) &&
      (filtros.fontes.length === 0 || baseFontes(l.fonte).some((f) => filtros.fontes.includes(f))) &&
      (!q || (l.nome || '').toLowerCase().includes(q) || (l.nome_fantasia || '').toLowerCase().includes(q)),
    )
    const dir = sort.dir === 'desc' ? -1 : 1
    arr.sort((a, b) => {
      const av = Number(a[sort.key]) || 0
      const bv = Number(b[sort.key]) || 0
      return (av - bv) * dir
    })
    return arr
  }, [resultado, filtros, sort])

  const sortedRef = useRef([])
  sortedRef.current = filtrados

  function onSort(key) {
    setSort((s) => (s.key === key ? { key, dir: s.dir === 'desc' ? 'asc' : 'desc' } : { key, dir: 'desc' }))
  }

  // ---- seleção ----
  const toggleSel = (id) => setSelecionados((s) => {
    const n = new Set(s)
    n.has(id) ? n.delete(id) : n.add(id)
    return n
  })
  const toggleAll = (checked, ids) => setSelecionados((s) => {
    const n = new Set(s)
    ids.forEach((id) => (checked ? n.add(id) : n.delete(id)))
    return n
  })
  const leadsSelecionados = useMemo(
    () => (resultado ? resultado.leads.filter((l) => selecionados.has(l._id)) : []),
    [resultado, selecionados],
  )

  // ---- export / agendor ----
  async function exportar(leads, formato) {
    if (!leads.length) return addToast({ kind: 'info', title: 'Nada para exportar', msg: 'Nenhum lead na visão atual.' })
    try {
      await api.exportar(leads, formato)
      addToast({ kind: 'success', title: 'Exportado', msg: `${leads.length} leads (${formato.toUpperCase()}).` })
    } catch (e) {
      if (e instanceof AuthError) return logout()
      addToast({ kind: 'error', title: 'Export falhou', msg: e.message })
    }
  }
  async function enviarAgendor(leads) {
    if (!leads.length) return
    if (!window.confirm(`Enviar ${leads.length} lead(s) ao Agendor como Organizações?`)) return
    try {
      const r = await api.agendor(leads)
      if (r.ok) addToast({ kind: 'success', title: 'Enviado ao Agendor', msg: `Criados: ${r.criados} · Falhas: ${r.falhas}` })
      else addToast({ kind: 'error', title: 'Agendor', msg: r.erro || 'Falha no envio.' })
    } catch (e) {
      if (e instanceof AuthError) return logout()
      addToast({ kind: 'error', title: 'Agendor falhou', msg: e.message })
    }
  }

  // ---- teclado ----
  useEffect(() => {
    function onKey(e) {
      const tag = (e.target.tagName || '').toLowerCase()
      const digitando = tag === 'input' || tag === 'textarea' || tag === 'select'
      if (e.key === 'Escape') {
        if (drawerLead) setDrawerLead(null)
        else if (digitando) e.target.blur()
        return
      }
      if (digitando) return
      if (e.key === '/') { e.preventDefault(); buscaRef.current?.focus(); return }
      const arr = sortedRef.current
      if (!arr.length) return
      if (e.key === 'j' || e.key === 'k') {
        e.preventDefault()
        const idx = arr.findIndex((l) => l._id === focusedId)
        const next = e.key === 'j' ? Math.min(arr.length - 1, idx + 1) : Math.max(0, idx - 1)
        setFocusedId(arr[next < 0 ? 0 : next]._id)
      } else if (e.key === 'Enter') {
        const l = arr.find((x) => x._id === focusedId)
        if (l) setDrawerLead(l)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [drawerLead, focusedId])

  // ---- render ----
  if (!authed) return <LoginScreen onAuthed={() => setAuthed(true)} />
  if (!config || !params) return <div className="empty" style={{ minHeight: '100vh' }}><span className="mono-sm">Carregando…</span></div>

  const resumoBusca = `${params.fontes.map((f) => f.toUpperCase()).join(' · ')} · ${params.ufs.length} UF`

  return (
    <div className="app-shell">
      {buscando && <div className="progress-top"><div className="bar" /></div>}
      <div className="sr-only" role="status" aria-live="polite">{buscando ? 'Buscando leads…' : ''}</div>

      <header className="toprail">
        <div className="wordmark"><span ref={beaconRef} className="beacon" /> Norte · Prospecção</div>
        <div className="center">{resultado ? resumoBusca : 'Console de prospecção ativa'}</div>
        <div className="right">
          <span className="base-pill"><span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--yellow)' }} /> CCEE <span className="num">{cceeTotal}</span></span>
          {resultado && !mostrarConfig && (
            <button className="btn btn-sm btn-outline-dark" onClick={() => setMostrarConfig(true)} type="button">Nova busca</button>
          )}
          <button className="logout" onClick={logout} type="button">Sair</button>
        </div>
      </header>

      <main className="main">
        <div className="container">
          {mostrarConfig ? (
            <SearchConfig
              config={config}
              params={params}
              update={(patch) => setParams((p) => ({ ...p, ...patch }))}
              onBuscar={onBuscar}
              onAtualizarCcee={atualizarCcee}
              cceeTotal={cceeTotal}
              cceeBusy={cceeBusy}
            />
          ) : (
            <div className="refine-bar">
              <span className="summary-txt">
                <strong>{params.fontes.length}</strong> fontes · <strong>{params.ufs.length}</strong> UFs · limite <strong>{params.limite}</strong>
              </span>
              <button className="btn btn-secondary btn-sm" onClick={() => setMostrarConfig(true)} type="button">Refinar busca ⌄</button>
            </div>
          )}

          {buscando && !resultado && <Skeletons />}

          {resultado && (
            <>
              <MetricsBand resumo={resultado.resumo} runId={runId} />

              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--sp-2)', margin: 'var(--sp-2) 0' }}>
                <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 20, color: 'var(--ink)', flex: 1 }}>Leads</h2>
                <button className="btn btn-secondary btn-sm" onClick={() => exportar(filtrados, 'csv')} type="button">CSV</button>
                <button className="btn btn-secondary btn-sm" onClick={() => exportar(filtrados, 'xlsx')} type="button">Excel</button>
                <button className="btn btn-primary btn-sm" onClick={() => enviarAgendor(filtrados)} type="button">Enviar ao Agendor</button>
              </div>

              <FiltersBar
                filtros={filtros}
                setFiltros={setFiltros}
                fontesDisponiveis={fontesDisponiveis}
                mostrando={filtrados.length}
                total={resultado.leads.length}
                buscaRef={buscaRef}
              />

              {filtrados.length ? (
                <LeadsTable
                  leads={filtrados}
                  selected={selecionados}
                  onToggle={toggleSel}
                  onToggleAll={toggleAll}
                  onOpen={setDrawerLead}
                  sort={sort}
                  onSort={onSort}
                  onToast={addToast}
                  focusedId={focusedId}
                />
              ) : (
                <div className="empty">
                  <div className="msg">Nenhum lead com esses filtros</div>
                  <button className="btn btn-ghost btn-sm" onClick={() => setFiltros(FILTROS_INICIAIS)} type="button">Limpar filtros</button>
                </div>
              )}
            </>
          )}

          {!resultado && !buscando && (
            <div className="empty">
              <div className="glyph"><span className="beacon" style={{ width: 14, height: 14 }} /></div>
              <div className="msg">Configure uma busca para acender o farol</div>
              <div className="sub">Comece pelo PNCP nos estados do Norte — são licitações de gerador com intenção de compra explícita.</div>
            </div>
          )}
        </div>
      </main>

      {drawerLead && <LeadDrawer lead={drawerLead} onClose={() => setDrawerLead(null)} onToast={addToast} />}

      {leadsSelecionados.length > 0 && (
        <SelectionBar
          count={leadsSelecionados.length}
          onCsv={() => exportar(leadsSelecionados, 'csv')}
          onXlsx={() => exportar(leadsSelecionados, 'xlsx')}
          onAgendor={() => enviarAgendor(leadsSelecionados)}
          onClear={() => setSelecionados(new Set())}
        />
      )}

      <div className="toast-stack" aria-live="polite" aria-atomic="false">
        {toasts.map((t) => <Toast key={t.id} kind={t.kind} title={t.title} msg={t.msg} />)}
      </div>
    </div>
  )
}

function Skeletons() {
  return (
    <div className="table-wrap" style={{ marginTop: 'var(--sp-4)' }}>
      {Array.from({ length: 8 }).map((_, i) => (
        <div className="skeleton-row" key={i}>
          <span className="sk" style={{ width: 90, height: 8 }} />
          <span className="sk" style={{ width: '30%', height: 12 }} />
          <span className="sk" style={{ width: 60, height: 12 }} />
          <span className="sk" style={{ width: 120, height: 12, marginLeft: 'auto' }} />
        </div>
      ))}
    </div>
  )
}
