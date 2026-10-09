// Cliente del backend. En desarrollo, Vite redirige /api a http://localhost:8000.
const BASE = import.meta.env.VITE_API_URL ?? ''

export async function analizarVoz(wav) {
  const datos = new FormData()
  datos.append('audio', wav, 'vocal_a.wav')
  const respuesta = await fetch(`${BASE}/api/analizar`, { method: 'POST', body: datos })
  const cuerpo = await respuesta.json().catch(() => ({}))
  if (!respuesta.ok) {
    // El backend responde los errores como { codigo, mensaje }.
    throw new Error(cuerpo.mensaje || 'No pudimos analizar la grabación. Inténtalo de nuevo.')
  }
  return cuerpo
}
