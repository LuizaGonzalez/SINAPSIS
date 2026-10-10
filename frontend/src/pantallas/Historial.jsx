import FilaAnalisis from '../componentes/FilaAnalisis.jsx'
import { Grafica } from '../componentes/Iconos.jsx'

/**
 * Pantalla del historial: todos los análisis de la sesión.
 *
 * Solo se guardan los resultados (fecha, nivel y probabilidad), nunca las
 * grabaciones. En este hito el historial vive en la memoria del navegador y se
 * borra al cerrar sesión o recargar la página.
 *
 * Recibe:
 *   - historial: lista de análisis, del más reciente al más antiguo.
 *   - onIniciarPrueba: función para ir a la prueba de voz.
 */
export default function Historial({ historial, onIniciarPrueba }) {
  return (
    <div className="pila">
      <header className="pila pila-corta">
        <h1>Historial</h1>
        <p className="secundario">
          {historial.length === 1 ? '1 análisis registrado' : `${historial.length} análisis registrados`}
        </p>
      </header>

      {historial.length > 0 ? (
        <section className="tarjeta-blanca">
          <ul className="lista-analisis">
            {historial.map((a) => <FilaAnalisis key={a.fecha.getTime()} analisis={a} />)}
          </ul>
        </section>
      ) : (
        <section className="tarjeta-blanca vacio">
          <span className="icono-circulo"><Grafica /></span>
          <p>Todavía no tienes análisis.</p>
          <button className="boton-primario" onClick={onIniciarPrueba}>Hacer mi primera prueba</button>
        </section>
      )}

      <p className="pie">Tus grabaciones no se guardan; solo el resultado. El historial se borra al cerrar sesión.</p>
    </div>
  )
}
