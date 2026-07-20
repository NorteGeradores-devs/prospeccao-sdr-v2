import { useEffect, useRef } from 'react'
import { toastIn } from '../motion.js'

export default function Toast({ kind = 'info', title, msg }) {
  const ref = useRef(null)
  useEffect(() => { if (ref.current) toastIn(ref.current) }, [])
  return (
    <div className={`toast ${kind}`} ref={ref} role={kind === 'error' ? 'alert' : 'status'}>
      {title && <div className="t-title">{title}</div>}
      {msg && <div className="t-msg">{msg}</div>}
    </div>
  )
}
