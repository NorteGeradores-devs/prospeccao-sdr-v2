import { useEffect, useRef } from 'react'
import { countUp } from '../motion.js'

export default function MetricsBand({ resumo, runId }) {
  const cells = [
    { key: 'total', label: 'Total', val: resumo.total || 0 },
    { key: 'quentes', label: 'Quentes', val: resumo.quentes || 0, hot: true },
    { key: 'mornos', label: 'Mornos', val: resumo.mornos || 0 },
    { key: 'frios', label: 'Frios', val: resumo.frios || 0 },
    { key: 'contato', label: 'Com contato', val: resumo.com_contato || 0 },
  ]
  const refs = useRef([])

  // count-up só quando muda a busca (runId), nunca em filtro.
  useEffect(() => {
    cells.forEach((c, i) => countUp(refs.current[i], c.val))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [runId])

  return (
    <div className="metrics-band">
      {cells.map((c, i) => (
        <div key={c.key} className={`metric-cell ${c.hot ? 'hot' : ''}`}>
          <span className="eyebrow">
            {c.hot && <span className="beacon" style={{ width: 6, height: 6, boxShadow: 'none' }} />}
            {c.label}
          </span>
          <div className="val" ref={(el) => (refs.current[i] = el)}>{c.val}</div>
        </div>
      ))}
    </div>
  )
}
