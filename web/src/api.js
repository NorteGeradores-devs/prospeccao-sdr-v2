// Cliente da API — mesma origem, sem autenticação (console aberto).
async function req(path, { method = 'GET', body, raw = false } = {}) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  const res = await fetch(`/api${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    let detalhe = `Erro ${res.status}`
    try { detalhe = (await res.json()).detail || detalhe } catch { /* ignore */ }
    throw new Error(detalhe)
  }
  if (raw) return res            // p/ downloads (blob)
  return res.json()
}

export const api = {
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
