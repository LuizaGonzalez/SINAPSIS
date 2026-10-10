import { useState } from 'react'
import { DURACION_MAXIMA_S, useGrabadora } from '../audio/useGrabadora.js'
import { analizarVoz } from '../servicios/api.js'
import { Detener, Microfono, Volver } from '../componentes/Iconos.jsx'

// Convierte segundos en texto de reloj, por ejemplo 3 -> "0:03"
const formato = (s) => `0:${String(Math.floor(s)).padStart(2, '0')}`

/**
 * Pantalla de la prueba de voz: graba la vocal "aaa" y la envía a analizar.
 *
 * La grabación la maneja useGrabadora (audio/useGrabadora.js). Esta pantalla
 * solo muestra el estado en cada momento: listo, grabando, grabación lista,
 * analizando o error.
 *
 * Recibe:
 *   - onVolver: función para regresar al inicio.
 *   - onResultado: función que recibe la respuesta del servidor cuando el análisis termina.
 */
export default function PruebaVoz({ onVolver, onResultado }) {
  const g = useGrabadora()
  const [analizando, setAnalizando] = useState(false)
  const [errorServidor, setErrorServidor] = useState(null)

  // Envía la grabación al servidor y, si todo sale bien, pasa a la pantalla de resultado
  const analizar = async () => {
    setAnalizando(true)
    setErrorServidor(null)
    try {
      onResultado(await analizarVoz(g.grabacion.wav))
    } catch (e) {
      setErrorServidor(e.message)
    } finally {
      setAnalizando(false)
    }
  }

  // Se muestra el error del servidor o, si no hay, el de la grabación (por ejemplo, micrófono bloqueado)
  const error = errorServidor ?? g.error
  const grabando = g.estado === 'grabando'

  return (
    <div className="pila">
      <div className="fila">
        <button className="boton-redondo" aria-label="Volver" onClick={onVolver}><Volver /></button>
        <span className="etiqueta-volver">Volver</span>
      </div>

      <header className="pila pila-corta">
        <h1>Prueba de voz</h1>
        <p className="secundario">Sostén el sonido "aaa" durante unos segundos. Solo toma un momento.</p>
      </header>

      <div className="columnas">
        <section className="tarjeta-verde">
          <div className="sobretitulo">CÓMO HACER LA PRUEBA</div>
          <ol>
            <li>Busca un lugar tranquilo, sin ruido de fondo.</li>
            <li>Respira profundo.</li>
            <li>Di <strong>"aaaaa"</strong> de forma continua, con un tono y un volumen cómodos.</li>
            <li>Mantén el sonido hasta que el contador llegue a 5 segundos.</li>
          </ol>
        </section>

        <div className="pila">
          <section className={`grabador ${grabando ? 'activo' : ''}`} aria-live="polite">
            <div className="estado-grabador">
              {grabando && <span className="punto-rojo" />}
              {g.estado === 'listo' && 'Listo para grabar'}
              {grabando && 'Grabando… sostén el "aaa"'}
              {g.estado === 'lista' && !analizando && 'Grabación lista'}
              {analizando && 'Analizando tu voz…'}
              {g.estado === 'error' && 'No se pudo completar la grabación'}
            </div>

            <div className="onda" aria-hidden="true">
              {g.niveles.map((n, i) => (
                <span key={i} style={{ height: `${Math.max(4, n * 44)}px` }} className={grabando ? 'viva' : ''} />
              ))}
            </div>

            <div className="progreso"><div style={{ width: `${(g.segundos / DURACION_MAXIMA_S) * 100}%` }} /></div>
            <div className={`contador ${grabando ? 'oscuro' : ''}`}>{formato(g.segundos)} / {formato(DURACION_MAXIMA_S)}</div>

            {error && <p className="error" role="alert">{error}</p>}

            {(g.estado === 'listo' || g.estado === 'error') && (
              <button className="boton-primario" onClick={g.iniciar}><Microfono />Iniciar grabación</button>
            )}
            {grabando && (
              <button className="boton-secundario" onClick={g.detener}><Detener />Detener</button>
            )}
            {g.estado === 'lista' && (
              <>
                <audio controls src={g.grabacion.url} className="reproductor" />
                <div className="fila fila-botones">
                  <button className="boton-secundario" onClick={g.reiniciar} disabled={analizando}>Repetir</button>
                  <button className="boton-primario" onClick={analizar} disabled={analizando}>
                    {analizando ? 'Analizando…' : 'Analizar'}
                  </button>
                </div>
              </>
            )}
          </section>

          <p className="pie">
            {grabando ? 'La grabación se detiene sola al llegar a 5 segundos.' : 'Tu grabación se usa solo para este análisis y no se guarda.'}
          </p>
        </div>
      </div>
    </div>
  )
}
