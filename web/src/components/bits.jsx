import { fonteLabel, parseMotivos, TEMP_LABEL } from '../lib/format.js'
import { IconMail, IconPhone } from '../lib/icons.jsx'

export function ScoreMeter({ score, temperatura, animate = true }) {
  const t = temperatura || 'frio'
  return (
    <div className="score-meter" title={`Score ${score} · ${TEMP_LABEL[t]}`}>
      <span className="score-val">{score}</span>
      <span className="score-track">
        <span
          className={`score-fill ${t}`}
          data-score={score}
          style={animate ? undefined : { width: `${score}%` }}
        />
      </span>
    </div>
  )
}

export function TempBadge({ temperatura }) {
  const t = temperatura || 'frio'
  return (
    <span className={`temp-badge ${t}`}>
      <span className="dot" />
      {TEMP_LABEL[t]}
    </span>
  )
}

export function FonteTag({ fonte }) {
  return <span className="fonte-tag">{fonteLabel(fonte)}</span>
}

export function ContactIcons({ telefone, email }) {
  return (
    <span className="contact-icons">
      <span className={telefone ? 'on' : ''} role="img"
        aria-label={telefone ? `Telefone ${telefone}` : 'Sem telefone'} title={telefone || 'sem telefone'}>
        <IconPhone size={15} />
      </span>
      <span className={email ? 'on' : ''} role="img"
        aria-label={email ? `E-mail ${email}` : 'Sem e-mail'} title={email || 'sem e-mail'}>
        <IconMail size={15} />
      </span>
    </span>
  )
}

export function MotivosChips({ motivos }) {
  const items = parseMotivos(motivos)
  if (!items.length) return <span className="mono-sm" style={{ color: 'var(--faint)' }}>—</span>
  return (
    <div className="motivos">
      {items.map((m, i) => (
        <span key={i} className={`motivo-chip ${m.sign}`}>
          {m.text}
          {m.weight !== null && (
            <span className="w">
              {m.weight >= 0 ? '+' : ''}
              {m.weight}
            </span>
          )}
        </span>
      ))}
    </div>
  )
}
