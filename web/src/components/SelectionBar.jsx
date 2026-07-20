import { useEffect, useRef } from 'react'
import { selectionIn } from '../motion.js'
import { IconSend, IconClose } from '../lib/icons.jsx'

export default function SelectionBar({ count, onCsv, onXlsx, onAgendor, onClear }) {
  const ref = useRef(null)
  useEffect(() => { if (ref.current) selectionIn(ref.current) }, [])
  return (
    <div className="selection-bar" ref={ref}>
      <span className="sel-count">{count} selecionado{count > 1 ? 's' : ''}</span>
      <div className="sel-actions">
        <button className="btn btn-sm btn-outline-dark" onClick={onCsv} type="button">CSV</button>
        <button className="btn btn-sm btn-outline-dark" onClick={onXlsx} type="button">Excel</button>
        <button className="btn btn-sm btn-on-dark" onClick={onAgendor} type="button"><IconSend size={14} /> Enviar ao Agendor</button>
        <button className="btn btn-sm clear" onClick={onClear} aria-label="Limpar seleção" type="button"><IconClose size={16} /></button>
      </div>
    </div>
  )
}
