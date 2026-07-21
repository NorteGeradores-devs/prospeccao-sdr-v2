import { useEffect, useRef, useState } from 'react'
import { api } from '../api.js'
import { beacon, fadeInUp } from '../motion.js'

export default function LoginScreen({ onAuthed }) {
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)
  const [caps, setCaps] = useState(false)
  const beaconRef = useRef(null)
  const cardRef = useRef(null)

  useEffect(() => {
    const anim = beacon(beaconRef.current)
    if (cardRef.current) fadeInUp(cardRef.current)
    return () => anim && anim.pause()
  }, [])

  async function submit(e) {
    e.preventDefault()
    setErro('')
    setCarregando(true)
    try {
      await api.login(senha)
      onAuthed()
    } catch (err) {
      setErro(err.message === 'Sessão expirada' ? 'Senha incorreta.' : err.message || 'Falha no login.')
      setCarregando(false)
    }
  }

  return (
    <div className="login">
      <div className="login-brand">
        <svg className="river" viewBox="0 0 400 600" preserveAspectRatio="none" aria-hidden="true">
          <path d="M-20 120 C120 180 60 300 200 340 S340 460 460 520" stroke="#fff" strokeWidth="1.5" fill="none" />
          <path d="M-20 200 C140 250 90 380 240 420 S380 520 460 560" stroke="#fff" strokeWidth="1" fill="none" />
        </svg>
        <div className="wordmark">
          <span ref={beaconRef} className="beacon beacon-lg" />
          Norte · Prospecção
        </div>
        <div className="tagline">
          Console de prospecção ativa — leads pontuados por ICP de geradores, prontos para o time comercial.
        </div>
        <div className="foot">Norte Geradores · Pará</div>
      </div>

      <div className="login-form">
        <div className="login-card" ref={cardRef}>
          <h1>Entrar</h1>
          <p className="sub">Acesse o console com a senha do time.</p>
          <form onSubmit={submit}>
            <div className="field">
              <label htmlFor="senha">Senha de acesso</label>
              <input
                id="senha"
                className="input num"
                type="password"
                autoFocus
                autoComplete="current-password"
                aria-describedby="caps-hint"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                onKeyUp={(e) => setCaps(!!e.getModifierState && e.getModifierState('CapsLock'))}
                onKeyDown={(e) => setCaps(!!e.getModifierState && e.getModifierState('CapsLock'))}
              />
            </div>
            <span id="caps-hint" className="hint" role="status" aria-live="polite">
              {caps ? '⇪ Caps Lock ativado.' : ''}
            </span>
            {erro && <span className="error">{erro}</span>}
            <button className="btn btn-primary btn-block" type="submit" disabled={carregando || !senha}>
              {carregando ? 'Entrando…' : 'Entrar'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
