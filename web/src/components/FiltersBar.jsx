import { fonteLabel } from '../lib/format.js'
import { IconSearch } from '../lib/icons.jsx'

const TEMPS = [
  { key: 'todos', label: 'Todos', dot: null },
  { key: 'quente', label: 'Quente', dot: 'var(--yellow)' },
  { key: 'morno', label: 'Morno', dot: 'var(--morno-dot)' },
  { key: 'frio', label: 'Frio', dot: 'var(--frio-dot)' },
]

export default function FiltersBar({ filtros, setFiltros, fontesDisponiveis, mostrando, total, buscaRef }) {
  const set = (patch) => setFiltros({ ...filtros, ...patch })
  const toggleFonte = (f) => {
    const has = filtros.fontes.includes(f)
    set({ fontes: has ? filtros.fontes.filter((x) => x !== f) : [...filtros.fontes, f] })
  }

  return (
    <div className="filters-bar">
      <div className="segmented" role="group" aria-label="Temperatura">
        {TEMPS.map((t) => (
          <button
            key={t.key}
            className={t.key === 'quente' ? 'seg-quente' : ''}
            aria-pressed={filtros.temp === t.key}
            onClick={() => set({ temp: t.key })}
            type="button"
          >
            {t.dot && <span style={{ width: 6, height: 6, borderRadius: '50%', background: t.dot, display: 'inline-block' }} />}
            {t.label}
          </button>
        ))}
      </div>

      {fontesDisponiveis.length > 1 && (
        <div className="chip-row">
          {fontesDisponiveis.map((f) => (
            <button key={f} className="chip" aria-pressed={filtros.fontes.includes(f)} onClick={() => toggleFonte(f)} type="button">
              {fonteLabel(f)}
            </button>
          ))}
        </div>
      )}

      <div className="slider" style={{ minWidth: 160 }}>
        <label className="eyebrow" style={{ margin: 0 }}>Score</label>
        <input type="range" min="0" max="100" step="5" value={filtros.scoreMin}
          aria-label="Score mínimo" onChange={(e) => set({ scoreMin: Number(e.target.value) })} />
        <span className="readout num">{filtros.scoreMin}</span>
      </div>

      <div className="search-inline">
        <span className="ico"><IconSearch size={15} /></span>
        <input ref={buscaRef} className="input" aria-label="Buscar empresa pelo nome" placeholder="Buscar empresa…  ( / )" value={filtros.q}
          onChange={(e) => set({ q: e.target.value })} />
      </div>

      <span className="count num">Mostrando {mostrando} de {total}</span>
    </div>
  )
}
