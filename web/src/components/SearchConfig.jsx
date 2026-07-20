import { useState } from 'react'
import { SourceIcon, IconCheck, IconRefresh } from '../lib/icons.jsx'

const lines = (t) => String(t || '').split('\n').map((s) => s.trim()).filter(Boolean)

export default function SearchConfig({ config, params, update, onBuscar, onAtualizarCcee, cceeTotal, cceeBusy }) {
  const [outrasUfs, setOutrasUfs] = useState(false)
  const set = (patch) => update(patch)

  const toggleFonte = (key) => {
    const has = params.fontes.includes(key)
    set({ fontes: has ? params.fontes.filter((f) => f !== key) : [...params.fontes, key] })
  }
  const toggleUf = (uf) => {
    const has = params.ufs.includes(uf)
    set({ ufs: has ? params.ufs.filter((u) => u !== uf) : [...params.ufs, uf] })
  }

  const norte = config.ufs_prioritarias
  const outras = config.todas_ufs.filter((u) => !norte.includes(u))
  const sel = new Set(params.fontes)

  return (
    <div className="search-grid">
      <div>
        {/* Fontes */}
        <section className="section">
          <span className="eyebrow">Fontes</span>
          <div className="source-grid">
            {config.fontes.map((f) => (
              <button
                key={f.key}
                className="source-card"
                aria-pressed={sel.has(f.key)}
                onClick={() => toggleFonte(f.key)}
                type="button"
              >
                <span className="ico"><SourceIcon fonte={f.key} /></span>
                <span>
                  <span className="s-label">{f.label.split('—')[0].trim()}</span>
                  <span className="s-desc">{f.descricao}</span>
                </span>
                <span className="check"><IconCheck size={16} /></span>
              </button>
            ))}
          </div>
        </section>

        {/* Região */}
        <section className="section">
          <span className="eyebrow">Região · Amazônia / Norte</span>
          <div className="chip-row">
            {norte.map((uf) => (
              <button key={uf} className="chip" aria-pressed={params.ufs.includes(uf)} onClick={() => toggleUf(uf)} type="button">
                {uf}
              </button>
            ))}
          </div>
          {!outrasUfs ? (
            <button className="reveal-link" onClick={() => setOutrasUfs(true)} type="button">+ outras UFs</button>
          ) : (
            <div className="chip-row" style={{ marginTop: 'var(--sp-3)' }}>
              {outras.map((uf) => (
                <button key={uf} className="chip" aria-pressed={params.ufs.includes(uf)} onClick={() => toggleUf(uf)} type="button">
                  {uf}
                </button>
              ))}
            </div>
          )}
        </section>

        {/* Parâmetros */}
        <section className="section">
          <span className="eyebrow">Parâmetros</span>
          <div className="param-grid">
            <div className="field">
              <label>Máx. por termo/fonte</label>
              <div className="slider">
                <input type="range" min="10" max="100" step="10" value={params.limite}
                  aria-label="Máximo por termo/fonte"
                  onChange={(e) => set({ limite: Number(e.target.value) })} />
                <span className="readout num">{params.limite}</span>
              </div>
            </div>
            {sel.has('pncp') && (
              <div className="field">
                <label>Situação do edital (PNCP)</label>
                <select className="select" aria-label="Situação do edital (PNCP)" value={params.pncp_status} onChange={(e) => set({ pncp_status: e.target.value })}>
                  <option value="recebendo_proposta">Recebendo proposta</option>
                  <option value="encerrada">Encerrada</option>
                  <option value="">Todas</option>
                </select>
              </div>
            )}
          </div>
        </section>

        {/* Enriquecimento */}
        <section className="section">
          <span className="eyebrow">Enriquecimento</span>
          <Toggle label="Enriquecer via Receita Federal" desc="Preenche CNPJ, contato e sócios (mais lento)."
            checked={params.enriquecer} onChange={(v) => set({ enriquecer: v })} />
          <Toggle label="Descobrir CNPJ por nome (best-effort)" desc="Para leads sem CNPJ (Places/SIGMINE). Confere na Receita."
            checked={params.resolver_cnpj} onChange={(v) => set({ resolver_cnpj: v })} />
          {sel.has('sisloc') && (
            <>
              <Toggle label="SISLOC: só quem já locou" desc="Exclui cadastros que nunca locaram."
                checked={params.sisloc_apenas_com_locacao} onChange={(v) => set({ sisloc_apenas_com_locacao: v })} />
              <div className="toggle-row">
                <div>
                  <div className="t-label">SISLOC: parados para reativação</div>
                  <div className="t-desc">Só clientes sem locar há ao menos N dias.</div>
                </div>
                <div className="stepper">
                  {params.sisloc_dias_ativo && (
                    <input className="input num" type="number" min="0" step="30"
                      aria-label="Dias sem locar (mínimo)" value={params.sisloc_dias}
                      onChange={(e) => { const v = e.target.value; set({ sisloc_dias: v === '' ? '' : Number(v) }) }} />
                  )}
                  <Switch checked={params.sisloc_dias_ativo} onChange={(v) => set({ sisloc_dias_ativo: v })}
                    label="Ativar filtro de dias sem locar" />
                </div>
              </div>
            </>
          )}
          {sel.has('ccee') && (
            <div className="toggle-row">
              <div>
                <div className="t-label">Base CCEE (consumidores livres)</div>
                <div className="t-desc num">{cceeTotal} empresas na base · fonte ANEEL</div>
              </div>
              <button className="btn btn-secondary btn-sm" onClick={onAtualizarCcee} disabled={cceeBusy} type="button">
                <IconRefresh size={15} /> {cceeBusy ? 'Atualizando…' : 'Atualizar'}
              </button>
            </div>
          )}
        </section>

        {/* Fontes por termo/cidade/lista */}
        {sel.has('pncp') && (
          <section className="section">
            <span className="eyebrow">Palavras-chave · PNCP</span>
            <textarea className="textarea" aria-label="Palavras-chave do PNCP (uma por linha)" value={params.keywords} onChange={(e) => set({ keywords: e.target.value })} />
          </section>
        )}
        {(sel.has('google_places') || sel.has('sympla')) && (
          <section className="section">
            <span className="eyebrow">Cidades · Places / Sympla</span>
            <textarea className="textarea" aria-label="Cidades (Places/Sympla, uma por linha)" value={params.cidades} onChange={(e) => set({ cidades: e.target.value })}
              placeholder={'Manaus\nBelém\nPorto Velho'} />
            {sel.has('sympla') && (
              <div className="field" style={{ marginTop: 'var(--sp-3)' }}>
                <label>Termo de evento (Sympla)</label>
                <input className="input" aria-label="Termo de evento (Sympla)" value={params.sympla_termo} onChange={(e) => set({ sympla_termo: e.target.value })} />
              </div>
            )}
          </section>
        )}
        {sel.has('cnpj') && (
          <section className="section">
            <span className="eyebrow">CNPJs para enriquecer</span>
            <textarea className="textarea" aria-label="CNPJs para enriquecer (um por linha)" value={params.cnpjs} onChange={(e) => set({ cnpjs: e.target.value })}
              placeholder={'00.000.000/0001-91'} />
          </section>
        )}
      </div>

      {/* Resumo lateral */}
      <div className="summary-rail">
        <div className="summary-card">
          <h3>Resumo da busca</h3>
          <div className="summary-line"><span className="k">Fontes</span><span className="v num">{params.fontes.length}</span></div>
          <div className="summary-line"><span className="k">Estados</span><span className="v num">{params.ufs.length}</span></div>
          <div className="summary-line"><span className="k">Limite/fonte</span><span className="v num">{params.limite}</span></div>
          <div className="summary-line"><span className="k">Enriquecer</span><span className="v">{params.enriquecer ? 'Sim' : 'Não'}</span></div>
          <div className="summary-line"><span className="k">Resolver CNPJ</span><span className="v">{params.resolver_cnpj ? 'Sim' : 'Não'}</span></div>
          <button className="btn btn-primary btn-block" onClick={() => onBuscar(buildBusca(params))} disabled={!params.fontes.length} type="button">
            Buscar leads
          </button>
          <div className="summary-meta">
            {params.fontes.length ? `${params.fontes.map((f) => f.toUpperCase()).join(' · ')}` : 'Selecione ao menos uma fonte'}
          </div>
        </div>
      </div>
    </div>
  )
}

function Toggle({ label, desc, checked, onChange }) {
  return (
    <div className="toggle-row">
      <div>
        <div className="t-label">{label}</div>
        {desc && <div className="t-desc">{desc}</div>}
      </div>
      <Switch checked={checked} onChange={onChange} label={label} />
    </div>
  )
}

function Switch({ checked, onChange, label }) {
  return (
    <label className="switch">
      <input type="checkbox" aria-label={label} checked={checked} onChange={(e) => onChange(e.target.checked)} />
      <span className="track"><span className="knob" /></span>
    </label>
  )
}

export function buildBusca(p) {
  return {
    fontes: p.fontes,
    ufs: p.ufs,
    limite: p.limite,
    enriquecer: p.enriquecer,
    resolver_cnpj: p.resolver_cnpj,
    pncp_status: p.pncp_status,
    keywords: lines(p.keywords),
    municipios: lines(p.cidades),
    google_queries: lines(p.google_queries),
    sympla_termo: p.sympla_termo,
    cnpjs: lines(p.cnpjs),
    sisloc_dias_sem_locar: p.sisloc_dias_ativo ? (p.sisloc_dias === '' ? 0 : Number(p.sisloc_dias)) : null,
    sisloc_apenas_com_locacao: p.sisloc_apenas_com_locacao,
  }
}
