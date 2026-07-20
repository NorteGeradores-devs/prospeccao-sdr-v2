import { useEffect, useRef } from 'react'
import { TempBadge, FonteTag, MotivosChips } from './bits.jsx'
import { brl, fmtCNPJ, fmtTel, copy } from '../lib/format.js'
import { IconClose, IconExternal } from '../lib/icons.jsx'
import { drawerIn } from '../motion.js'

function Field({ k, children, mono, onCopy }) {
  if (children === null || children === undefined || children === '' || children === '—') return null
  return (
    <div className="d-field">
      <div className="k">{k}</div>
      <div className={`v ${mono ? 'mono' : ''} ${onCopy ? 'copyable' : ''}`} onClick={onCopy}>{children}</div>
    </div>
  )
}

export default function LeadDrawer({ lead, onClose, onToast }) {
  const ref = useRef(null)
  const closeRef = useRef(null)

  useEffect(() => { if (ref.current) drawerIn(ref.current) }, [lead])

  // Move o foco para dentro do diálogo ao abrir e o devolve ao fechar.
  useEffect(() => {
    const anterior = document.activeElement
    closeRef.current?.focus()
    return () => { if (anterior && anterior.focus) anterior.focus() }
  }, [])

  // Prende Tab/Shift+Tab dentro do drawer enquanto aberto.
  function trapTab(e) {
    if (e.key !== 'Tab' || !ref.current) return
    const foco = Array.from(
      ref.current.querySelectorAll('a[href], button, input, textarea, select, [tabindex]:not([tabindex="-1"])'),
    ).filter((el) => !el.disabled && el.offsetParent !== null)
    if (!foco.length) return
    const primeiro = foco[0]
    const ultimo = foco[foco.length - 1]
    if (e.shiftKey && document.activeElement === primeiro) { e.preventDefault(); ultimo.focus() }
    else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primeiro.focus() }
  }

  const cop = (txt) => async () => {
    if (await copy(txt)) onToast?.({ kind: 'success', title: 'Copiado', msg: txt })
  }

  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} />
      <aside className="drawer" ref={ref} role="dialog" aria-modal="true" aria-label="Detalhe do lead" onKeyDown={trapTab}>
        <div className="d-head">
          <button ref={closeRef} className="icon-btn d-close" onClick={onClose} aria-label="Fechar"><IconClose size={18} /></button>
          <div className="nome">{lead.nome}</div>
          <div className="meta">
            <TempBadge temperatura={lead.temperatura} />
            <FonteTag fonte={lead.fonte} />
            <span className="num" style={{ color: 'var(--muted)', fontSize: 13 }}>Score {lead.score}</span>
          </div>
        </div>
        <div className="d-body">
          <Field k="Oportunidade">{lead.titulo}</Field>
          <Field k="Segmento">{[lead.segmento, lead.cnae_descricao].filter(Boolean).join(' · ') || null}</Field>
          <Field k="CNPJ" mono onCopy={lead.cnpj ? cop(lead.cnpj) : undefined}>{lead.cnpj ? fmtCNPJ(lead.cnpj) : null}</Field>
          <Field k="Telefone" mono onCopy={lead.telefone ? cop(lead.telefone) : undefined}>{lead.telefone ? fmtTel(lead.telefone) : null}</Field>
          <Field k="E-mail" onCopy={lead.email ? cop(lead.email) : undefined}>{lead.email || null}</Field>
          <Field k="Contato">{lead.contato_nome ? `${lead.contato_nome}${lead.contato_cargo ? ` — ${lead.contato_cargo}` : ''}` : null}</Field>
          <Field k="Local">{[lead.municipio, lead.uf].filter(Boolean).join(' / ') || null}</Field>
          <Field k="Endereço">{lead.endereco || null}</Field>
          <Field k="Valor estimado" mono>{lead.valor_estimado ? brl(lead.valor_estimado) : null}</Field>
          <Field k="Situação cadastral">{lead.situacao_cadastral || null}</Field>
          <Field k="Prazo / data" mono>{lead.data_evento || null}</Field>
          <Field k="Observações">{lead.observacoes || null}</Field>

          {lead.url && (
            <a className="btn btn-secondary btn-block" style={{ marginTop: 'var(--sp-4)' }} href={lead.url} target="_blank" rel="noreferrer">
              <IconExternal size={16} /> Abrir link
            </a>
          )}

          <div className="d-field" style={{ borderBottom: 'none', marginTop: 'var(--sp-4)' }}>
            <div className="k">Motivos do score</div>
            <MotivosChips motivos={lead.motivos_score} />
          </div>
        </div>
      </aside>
    </>
  )
}
