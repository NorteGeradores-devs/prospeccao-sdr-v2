import { useEffect, useRef } from 'react'
import { ScoreMeter, TempBadge, FonteTag, ContactIcons } from './bits.jsx'
import { brl, fmtCNPJ, copy } from '../lib/format.js'
import { IconExternal, IconDots, IconCheck } from '../lib/icons.jsx'
import { animateScoreBars } from '../motion.js'
import { useMediaQuery } from '../lib/hooks.js'

const accent = (t) => (t === 'quente' ? 'var(--yellow)' : t === 'morno' ? 'var(--morno-dot)' : 'var(--frio-dot)')

export default function LeadsTable({ leads, selected, onToggle, onToggleAll, onOpen, sort, onSort, onToast, focusedId }) {
  const isMobile = useMediaQuery('(max-width: 900px)')
  const bodyRef = useRef(null)

  useEffect(() => {
    if (bodyRef.current) animateScoreBars(bodyRef.current)
  }, [leads, isMobile])

  // mantém a linha focada por teclado (J/K) visível
  useEffect(() => {
    if (focusedId == null || !bodyRef.current) return
    bodyRef.current.querySelector(`[data-id="${focusedId}"]`)?.scrollIntoView({ block: 'nearest' })
  }, [focusedId])

  async function copiar(e, texto) {
    e.stopPropagation()
    const el = e.currentTarget          // capturar ANTES do await (React anula currentTarget)
    if (await copy(texto)) {
      el?.classList.add('copy-flash')
      setTimeout(() => el?.classList.remove('copy-flash'), 400)
      onToast?.({ kind: 'success', title: 'Copiado', msg: texto })
    }
  }

  const ariaSort = (col) => (sort.key === col ? (sort.dir === 'desc' ? 'descending' : 'ascending') : 'none')

  const allChecked = leads.length > 0 && leads.every((l) => selected.has(l._id))

  if (isMobile) {
    return (
      <div className="lead-cards" ref={bodyRef}>
        {leads.map((l) => (
          <div className="lead-card" key={l._id} data-id={l._id} onClick={() => onOpen(l)}>
            <span className="temp-accent" style={{ background: accent(l.temperatura) }} />
            <div className="l1">
              <ScoreMeter score={l.score} temperatura={l.temperatura} />
              <span className="nome">{l.nome}</span>
            </div>
            <div className="l2">
              <FonteTag fonte={l.fonte} />
              <span className="mono-sm" style={{ color: 'var(--muted)' }}>{[l.municipio, l.uf].filter(Boolean).join(' · ')}</span>
            </div>
            <div className="l3">
              <span className="valor num">{brl(l.valor_estimado)}</span>
              <ContactIcons telefone={l.telefone} email={l.email} />
            </div>
          </div>
        ))}
      </div>
    )
  }

  const Arrow = ({ col }) => (sort.key === col ? <span className="arrow">{sort.dir === 'desc' ? '↓' : '↑'}</span> : <span className="arrow">↕</span>)

  return (
    <div className="table-wrap">
      <div className="table-scroll">
        <table className="leads">
          <thead>
            <tr>
              <th className="cell-check" scope="col">
                <input type="checkbox" aria-label="Selecionar todos os leads" checked={allChecked} onChange={(e) => onToggleAll(e.target.checked, leads.map((l) => l._id))} />
              </th>
              <th scope="col" aria-sort={ariaSort('score')}>
                <button type="button" className="th-sort" onClick={() => onSort('score')}>Score <Arrow col="score" /></button>
              </th>
              <th scope="col">Empresa</th>
              <th scope="col">Fonte</th>
              <th scope="col">CNPJ</th>
              <th scope="col">Contato</th>
              <th className="right" scope="col" aria-sort={ariaSort('valor_estimado')}>
                <button type="button" className="th-sort" onClick={() => onSort('valor_estimado')}>Valor est. <Arrow col="valor_estimado" /></button>
              </th>
              <th scope="col">Oportunidade</th>
              <th scope="col"><span className="sr-only">Ações</span></th>
            </tr>
          </thead>
          <tbody ref={bodyRef}>
            {leads.map((l) => {
              const k = l._id
              return (
                <tr key={k} data-id={k} aria-selected={focusedId === k} className={`${selected.has(k) ? 'selected' : ''} ${focusedId === k ? 'focused' : ''}`} onClick={() => onOpen(l)}>
                  <td className="cell-check" onClick={(e) => e.stopPropagation()}>
                    <span className="temp-accent" style={{ background: accent(l.temperatura) }} />
                    <input type="checkbox" aria-label={`Selecionar ${l.nome || 'lead'}`} checked={selected.has(k)} onChange={() => onToggle(k)} />
                  </td>
                  <td><ScoreMeter score={l.score} temperatura={l.temperatura} /></td>
                  <td className="col-empresa">
                    <div className="nome">{l.nome || '—'}</div>
                    <div className="sub">{[l.segmento, [l.municipio, l.uf].filter(Boolean).join('/')].filter(Boolean).join(' · ')}</div>
                  </td>
                  <td><FonteTag fonte={l.fonte} /></td>
                  <td>
                    {l.cnpj
                      ? <button type="button" className="num copyable" title="Copiar CNPJ" aria-label={`Copiar CNPJ ${fmtCNPJ(l.cnpj)}`} onClick={(e) => copiar(e, l.cnpj)}>{fmtCNPJ(l.cnpj)}</button>
                      : <span className="mono-sm" style={{ color: 'var(--faint)' }}>—</span>}
                  </td>
                  <td><ContactIcons telefone={l.telefone} email={l.email} /></td>
                  <td className="right num">{brl(l.valor_estimado)}</td>
                  <td style={{ maxWidth: 240 }}>
                    <span title={l.titulo} style={{ display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--muted)', fontSize: 13 }}>
                      {l.titulo || '—'}
                    </span>
                  </td>
                  <td onClick={(e) => e.stopPropagation()}>
                    <span className="row-actions">
                      {l.url && (
                        <a className="icon-btn" href={l.url} target="_blank" rel="noreferrer" title="Abrir link"><IconExternal size={15} /></a>
                      )}
                      <button className="icon-btn" title="Detalhes" onClick={() => onOpen(l)}><IconDots size={15} /></button>
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
