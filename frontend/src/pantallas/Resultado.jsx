import AvisoMedico from '../componentes/AvisoMedico.jsx'
import { Check, Volver } from '../componentes/Iconos.jsx'
import { NIVELES, fechaConHora, porcentaje } from '../utilidades/formato.js'

// Nombres comprensibles para las medidas de voz que devuelve el servidor
const NOMBRES = {
  'MDVP:Fo(Hz)': 'Frecuencia fundamental media',
  'MDVP:Fhi(Hz)': 'Frecuencia fundamental máxima',
  'MDVP:Flo(Hz)': 'Frecuencia fundamental mínima',
  'MDVP:Jitter(%)': 'Variación de la frecuencia (jitter)',
  'MDVP:Jitter(Abs)': 'Jitter absoluto',
  'MDVP:RAP': 'Jitter (RAP)',
  'MDVP:PPQ': 'Jitter (PPQ5)',
  'Jitter:DDP': 'Jitter (DDP)',
  'MDVP:Shimmer': 'Variación de la amplitud (shimmer)',
  'MDVP:Shimmer(dB)': 'Shimmer en dB',
  'Shimmer:APQ3': 'Shimmer (APQ3)',
  'Shimmer:APQ5': 'Shimmer (APQ5)',
  'MDVP:APQ': 'Shimmer (APQ11)',
  'Shimmer:DDA': 'Shimmer (DDA)',
  NHR: 'Relación ruido-armónicos',
  HNR: 'Relación armónicos-ruido',
}

/**
 * Pantalla de resultado: muestra el nivel de riesgo y qué hacer después.
 *
 * Siempre incluye el aviso de que no es un diagnóstico médico.
 *
 * Recibe:
 *   - resultado: la respuesta del servidor (nivel, probabilidad, recomendación,
 *     aviso y medidas de voz más inusuales), más la fecha del análisis.
 *   - onVolver: función para regresar al inicio.
 *   - onRepetir: función para hacer la prueba otra vez.
 */
export default function Resultado({ resultado, onVolver, onRepetir }) {
  const orden = ['bajo', 'medio', 'alto']

  return (
    <div className="pila">
      <div className="fila">
        <button className="boton-redondo" aria-label="Volver al inicio" onClick={onVolver}><Volver /></button>
        <span className="etiqueta-volver">Resultado</span>
      </div>

      <header className="pila pila-corta">
        <h1>Tu análisis está listo</h1>
        <p className="secundario">Prueba de voz · {fechaConHora(resultado.fecha)}</p>
      </header>

      <div className="columnas">
        <section className="tarjeta-oscura">
          <div className="sobretitulo claro">NIVEL DE RIESGO ESTIMADO</div>
          <div className={`nivel nivel-${resultado.nivel}`}>{NIVELES[resultado.nivel]}</div>
          <div className="escala" aria-hidden="true">
            {orden.map((n) => <span key={n} className={n === resultado.nivel ? 'marcado' : ''} />)}
          </div>
          <div className="escala-etiquetas" aria-hidden="true"><span>Bajo</span><span>Medio</span><span>Alto</span></div>
          <p className="probabilidad">Probabilidad estimada: {porcentaje(resultado.probabilidad)}</p>
        </section>

        <div className="pila">
          <p className="recomendacion">{resultado.recomendacion}</p>

          <AvisoMedico texto={resultado.aviso} />

          {resultado.caracteristicas_destacadas?.length > 0 && (
            <details className="detalles">
              <summary>¿Qué valores de tu voz fueron más inusuales?</summary>
              <ul>
                {resultado.caracteristicas_destacadas.map((c) => (
                  <li key={c.nombre}>
                    {NOMBRES[c.nombre] ?? c.nombre}: {c.desviaciones > 0 ? 'por encima' : 'por debajo'} del
                    promedio ({Math.abs(c.desviaciones).toFixed(1)} desviaciones)
                  </li>
                ))}
              </ul>
            </details>
          )}

          <button className="boton-primario" onClick={onRepetir}>Repetir la prueba</button>
          <p className="guardado"><span className="icono-check"><Check /></span>Guardado en tu historial</p>
        </div>
      </div>
    </div>
  )
}
