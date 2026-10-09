import { useCallback, useEffect, useRef, useState } from 'react'
import { blobAWav } from './wav.js'

export const DURACION_MAXIMA_S = 5
export const DURACION_MINIMA_S = 3
const BARRAS = 28

// Estados: 'listo' | 'grabando' | 'lista' | 'error'
export function useGrabadora() {
  const [estado, setEstado] = useState('listo')
  const [segundos, setSegundos] = useState(0)
  const [niveles, setNiveles] = useState(() => Array(BARRAS).fill(0))
  const [grabacion, setGrabacion] = useState(null) // { wav, url, duracion }
  const [error, setError] = useState(null)

  const recursos = useRef({})

  const liberar = useCallback(() => {
    const r = recursos.current
    cancelAnimationFrame(r.animacion)
    clearInterval(r.reloj)
    clearTimeout(r.limite)
    r.stream?.getTracks().forEach((t) => t.stop())
    r.contexto?.close().catch(() => {})
    recursos.current = {}
  }, [])

  useEffect(() => liberar, [liberar])

  const detener = useCallback(() => {
    const r = recursos.current.grabador
    if (r && r.state === 'recording') r.stop()
  }, [])

  const iniciar = useCallback(async () => {
    setError(null)
    setGrabacion((g) => { if (g?.url) URL.revokeObjectURL(g.url); return null })
    let stream
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        // Se desactivan los filtros del navegador: alteran jitter, shimmer y HNR.
        audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false },
      })
    } catch {
      setError('Necesitamos acceso a tu micrófono para hacer la prueba. Actívalo en la configuración del navegador.')
      setEstado('error')
      return
    }

    const contexto = new (window.AudioContext || window.webkitAudioContext)()
    const analizador = contexto.createAnalyser()
    analizador.fftSize = 1024
    contexto.createMediaStreamSource(stream).connect(analizador)
    const muestras = new Float32Array(analizador.fftSize)
    const historial = Array(BARRAS).fill(0)

    const grabador = new MediaRecorder(stream)
    const partes = []
    grabador.ondataavailable = (e) => e.data.size && partes.push(e.data)
    grabador.onstop = async () => {
      liberar()
      try {
        const { wav, duracion } = await blobAWav(new Blob(partes, { type: grabador.mimeType }))
        if (duracion < DURACION_MINIMA_S) {
          setError('La grabación fue muy corta. Intenta sostener el "aaa" durante al menos 3 segundos.')
          setEstado('error')
          return
        }
        setGrabacion({ wav, url: URL.createObjectURL(wav), duracion })
        setEstado('lista')
      } catch {
        setError('No pudimos procesar la grabación. Inténtalo de nuevo.')
        setEstado('error')
      }
    }

    const inicio = performance.now()
    const animar = () => {
      analizador.getFloatTimeDomainData(muestras)
      let suma = 0
      for (const m of muestras) suma += m * m
      historial.push(Math.min(1, Math.sqrt(suma / muestras.length) * 6))
      historial.shift()
      setNiveles([...historial])
      recursos.current.animacion = requestAnimationFrame(animar)
    }

    recursos.current = {
      stream, contexto, grabador,
      reloj: setInterval(() => setSegundos(Math.min(DURACION_MAXIMA_S, (performance.now() - inicio) / 1000)), 100),
      limite: setTimeout(() => grabador.state === 'recording' && grabador.stop(), DURACION_MAXIMA_S * 1000),
    }
    setSegundos(0)
    setEstado('grabando')
    grabador.start()
    animar()
  }, [liberar])

  const reiniciar = useCallback(() => {
    liberar()
    setGrabacion((g) => { if (g?.url) URL.revokeObjectURL(g.url); return null })
    setSegundos(0)
    setNiveles(Array(BARRAS).fill(0))
    setError(null)
    setEstado('listo')
  }, [liberar])

  return { estado, segundos, niveles, grabacion, error, iniciar, detener, reiniciar }
}
