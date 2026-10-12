// Convierte un AudioBuffer en un archivo WAV mono de 16 bits.
// El navegador graba normalmente en WebM/Opus; el backend (Parselmouth) trabaja
// con WAV, así que la conversión se hace aquí, sin depender de ffmpeg.

export function audioBufferAWav(buffer) {
  const canales = buffer.numberOfChannels
  const n = buffer.length
  const mono = new Float32Array(n)
  for (let c = 0; c < canales; c++) {
    const datos = buffer.getChannelData(c)
    for (let i = 0; i < n; i++) mono[i] += datos[i] / canales
  }

  const frecuencia = buffer.sampleRate
  const bytesDatos = n * 2
  const vista = new DataView(new ArrayBuffer(44 + bytesDatos))
  const texto = (pos, s) => { for (let i = 0; i < s.length; i++) vista.setUint8(pos + i, s.charCodeAt(i)) }

  texto(0, 'RIFF')
  vista.setUint32(4, 36 + bytesDatos, true)
  texto(8, 'WAVE')
  texto(12, 'fmt ')
  vista.setUint32(16, 16, true)            // tamaño del bloque fmt
  vista.setUint16(20, 1, true)             // PCM
  vista.setUint16(22, 1, true)             // mono
  vista.setUint32(24, frecuencia, true)
  vista.setUint32(28, frecuencia * 2, true)
  vista.setUint16(32, 2, true)
  vista.setUint16(34, 16, true)            // 16 bits
  texto(36, 'data')
  vista.setUint32(40, bytesDatos, true)

  let pos = 44
  for (let i = 0; i < n; i++, pos += 2) {
    const m = Math.max(-1, Math.min(1, mono[i]))
    vista.setInt16(pos, m < 0 ? m * 0x8000 : m * 0x7fff, true)
  }
  return new Blob([vista], { type: 'audio/wav' })
}

export async function blobAWav(blob) {
  const contexto = new (window.AudioContext || window.webkitAudioContext)()
  try {
    const buffer = await contexto.decodeAudioData(await blob.arrayBuffer())
    return { wav: audioBufferAWav(buffer), duracion: buffer.duration }
  } finally {
    contexto.close()
  }
}
