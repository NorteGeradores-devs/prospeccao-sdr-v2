// Ícones inline (SVG stroke, currentColor) — nada de lib de ícone genérica.
const S = ({ size = 16, children, ...p }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    focusable="false"
    {...p}
  >
    {children}
  </svg>
)

export const IconPhone = (p) => (
  <S {...p}><path d="M4 5c0 8 7 15 15 15l2-3-4-2-2 2c-3-1.5-6-4.5-7.5-7.5l2-2-2-4Z" /></S>
)
export const IconMail = (p) => (
  <S {...p}><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 7 9 6 9-6" /></S>
)
export const IconExternal = (p) => (
  <S {...p}><path d="M14 4h6v6" /><path d="M20 4 10 14" /><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5" /></S>
)
export const IconCopy = (p) => (
  <S {...p}><rect x="9" y="9" width="11" height="11" rx="2" /><path d="M5 15V5a2 2 0 0 1 2-2h8" /></S>
)
export const IconCheck = (p) => (<S {...p}><path d="m5 12 4 4L19 6" /></S>)
export const IconSearch = (p) => (<S {...p}><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></S>)
export const IconClose = (p) => (<S {...p}><path d="M6 6l12 12M18 6 6 18" /></S>)
export const IconDownload = (p) => (<S {...p}><path d="M12 3v12" /><path d="m7 11 5 5 5-5" /><path d="M5 21h14" /></S>)
export const IconSend = (p) => (<S {...p}><path d="M22 2 11 13" /><path d="M22 2 15 22l-4-9-9-4 20-7Z" /></S>)
export const IconRefresh = (p) => (<S {...p}><path d="M21 12a9 9 0 1 1-3-6.7L21 8" /><path d="M21 3v5h-5" /></S>)
export const IconDots = (p) => (<S {...p}><circle cx="5" cy="12" r="1" /><circle cx="12" cy="12" r="1" /><circle cx="19" cy="12" r="1" /></S>)

// ícones de fonte (um por conector)
const SourceGavel = (p) => (<S {...p}><path d="m14 10-6 6" /><path d="m8 6 6 6" /><path d="M12 4l6 6" /><path d="M4 20h8" /></S>)
const SourceBuilding = (p) => (<S {...p}><rect x="5" y="3" width="14" height="18" rx="1" /><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2" /></S>)
const SourceBolt = (p) => (<S {...p}><path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z" /></S>)
const SourcePin = (p) => (<S {...p}><path d="M12 21s7-6.4 7-11a7 7 0 1 0-14 0c0 4.6 7 11 7 11Z" /><circle cx="12" cy="10" r="2.5" /></S>)
const SourceDoc = (p) => (<S {...p}><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8Z" /><path d="M14 3v5h5" /><path d="M9 13h6M9 17h4" /></S>)
const SourceTicket = (p) => (<S {...p}><path d="M4 8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2 2 2 0 0 0 0 4 2 2 0 0 1-2 2H6a2 2 0 0 1-2-2 2 2 0 0 0 0-4Z" /><path d="M14 6v12" /></S>)
const SourcePick = (p) => (<S {...p}><path d="M4 20 14 10" /><path d="M3 9c4-4 10-5 14-3-3-1-7 0-9 2M21 9c-1-4-5-6-9-6 3 1 5 3 6 6" /></S>)

const SOURCE_ICONS = {
  pncp: SourceGavel,
  sisloc: SourceBuilding,
  ccee: SourceBolt,
  google_places: SourcePin,
  cnpj: SourceDoc,
  sympla: SourceTicket,
  sigmine: SourcePick,
}

export function SourceIcon({ fonte, size = 18 }) {
  const Ico = SOURCE_ICONS[fonte] || SourceDoc
  return <Ico size={size} />
}
