// Cliente da API — token guardado no localStorage, injetado como Bearer.
const TOKEN_KEY = 'sdr_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

class AuthError extends Error {}
export { AuthError }

async function req(path, { method = 'GET', body, raw = false } = {}) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  const tok = getToken()
  if (tok) headers.Authorization = `Bearer ${tok}`

  const res = await fetch(`/api${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (res.status === 401) {
    clearToken()
    throw new AuthError('Sessão expirada')
  }
  if (!res.ok) {
    let detalhe = `Erro ${res.status}`
    try { detalhe = (await res.json()).detail || detalhe } catch { /* ignore */ }
    throw new Error(detalhe)
  }
  if (raw) return res            // p/ downloads (blob)
  return res.json()
}

export const api = {
  async login(senha) {
    const r = await req('/login', { method: 'POST', body: { senha } })
    setToken(r.token)
    return r
  },
  config: () => req('/config'),
  buscar: (params) => req('/buscar', { method: 'POST', body: params }),
  agendor: (leads, apenas_temperatura) =>
    req('/agendor', { method: 'POST', body: { leads, apenas_temperatura } }),
  atualizarCcee: () => req('/ccee/atualizar', { method: 'POST', body: {} }),

  async exportar(leads, formato) {
    const res = await req('/exportar', { method: 'POST', body: { leads, formato }, raw: true })
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `leads_norte_geradores.${formato}`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  },
}
