// Formatadores e parsers — números como "ledger", motivos auditáveis.

export const FONTE_LABEL = {
  pncp: 'PNCP',
  sisloc: 'SISLOC',
  ccee: 'CCEE',
  google_places: 'PLACES',
  cnpj: 'CNPJ',
  sympla: 'SYMPLA',
  sigmine: 'SIGMINE',
}

export function fonteLabel(fonte) {
  // leads mesclados vêm como "a+b"
  return String(fonte || '')
    .split('+')
    .map((f) => FONTE_LABEL[f] || f.toUpperCase())
    .join('+')
}

export function brl(v) {
  const n = Number(v)
  if (!n || Number.isNaN(n)) return '—'
  return n.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 0,
  })
}

const digits = (s) => String(s || '').replace(/\D/g, '')

export function fmtCNPJ(c) {
  const d = digits(c)
  if (d.length !== 14) return c || ''
  return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5, 8)}/${d.slice(8, 12)}-${d.slice(12)}`
}

export function fmtTel(t) {
  const d = digits(t)
  if (d.length === 11) return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`
  if (d.length === 10) return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`
  return t || ''
}

export function tempOf(score) {
  if (score >= 65) return 'quente'
  if (score >= 40) return 'morno'
  return 'frio'
}

export const TEMP_LABEL = { quente: 'Quente', morno: 'Morno', frio: 'Frio' }

// motivos_score chega como "a (+20); b (-15); c" → chips assinados.
export function parseMotivos(str) {
  if (!str) return []
  return String(str)
    .split(';')
    .map((s) => s.trim())
    .filter(Boolean)
    .map((item) => {
      const m = item.match(/\(([+-]?\d+)\)\s*$/)
      const weight = m ? Number(m[1]) : null
      const text = m ? item.slice(0, m.index).trim() : item
      const sign = weight === null ? 'neutral' : weight >= 0 ? 'pos' : 'neg'
      return { text, weight, sign }
    })
}

export async function copy(text) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    return false
  }
}
