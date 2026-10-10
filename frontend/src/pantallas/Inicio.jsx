import AvisoMedico from '../componentes/AvisoMedico.jsx'
import FilaAnalisis from '../componentes/FilaAnalisis.jsx'
import { Microfono } from '../componentes/Iconos.jsx'
import { NIVELES, fechaConHora, fechaLargaHoy, porcentaje } from '../utilidades/formato.js'

/**
 * Pantalla de inicio del usuario con sesión iniciada.
 *
 * Muestra el saludo, el último análisis, el acceso a la prueba de voz y los
 * análisis más recientes. Todo sale del historial real de la sesión: si el
 * usuario aún no ha hecho pruebas, se le invita a hacer la primera.
 *
 * Recibe:
 *   - usuario: { nombre, correo } del usuario.
 *   - historial: lista de análisis, del más reciente al más antiguo.
 *   - onIniciarPrueba: función para ir a la prueba de voz.
 *   - onVerHistorial: función para ir al historial completo.
 *   - onCerrarSesion: función para salir.
 */
export default function Inicio({ usuario, historial, onIniciarPrueba, onVerHistorial, onCerrarSesion }) {
  const ultimo = historial[0]
  // Las barras muestran la probabilidad de los últimos análisis, del más antiguo al más reciente
  const recientes = historial.slice(0, 10).reverse()

  return (
    <div className="pila inicio-ajustado">
      <header className="fila fila-separada">
        <div className="pila pila-corta">
          <h1>Hola, {usuario.nombre}</h1>
          <p className="secundario primera-mayuscula">{fechaLargaHoy()}</p>
        </div>
        <div className="fila">
          <button className="enlace" onClick={onCerrarSesion}>Cerrar sesión</button>
          <span className="avatar avatar-encabezado" aria-hidden="true">{usuario.nombre[0]}</span>
        </div>
      </header>

      <div className="columnas columnas-iguales">
        <section className="tarjeta-oscura">
          <div className="fila fila-separada">
            <div>
              <p className="sobretitulo claro">ÚLTIMO ANÁLISIS</p>
              {ultimo && <p className="probabilidad">{fechaConHora(ultimo.fecha)}</p>}
            </div>
            {ultimo && <span className={`chip chip-${ultimo.nivel}`}>Riesgo {NIVELES[ultimo.nivel].toLowerCase()}</span>}
          </div>

          {ultimo ? (
            <>
              <div className="barras" aria-hidden="true">
                {recientes.map((a, i) => (
                  <span key={a.fecha.getTime()} style={{ height: `${Math.max(8, a.probabilidad * 100)}%` }}
                    className={i === recientes.length - 1 ? 'actual' : ''} />
                ))}
              </div>
              <p className="probabilidad">Probabilidad estimada: <strong>{porcentaje(ultimo.probabilidad)}</strong></p>
            </>
          ) : (
            <p className="probabilidad">Aún no tienes análisis. Haz tu primera prueba de voz para ver aquí tu resultado.</p>
          )}
        </section>

        <button className="tarjeta-accion" onClick={onIniciarPrueba}>
          <span className="icono-circulo"><Microfono tamano={26} /></span>
          <span className="titulo-accion">Prueba de voz</span>
          <span className="secundario">Realiza un nuevo análisis en 5 segundos</span>
          <span className="boton-falso">Comenzar prueba</span>
        </button>
      </div>

      <section className="tarjeta-blanca pila">
        <div className="fila fila-separada">
          <h2>Historial reciente</h2>
          {historial.length > 0 && <button className="enlace" onClick={onVerHistorial}>Ver todo</button>}
        </div>
        {historial.length > 0 ? (
          <ul className="lista-analisis">
            {historial.slice(0, 3).map((a) => <FilaAnalisis key={a.fecha.getTime()} analisis={a} />)}
          </ul>
        ) : (
          <p className="secundario">Aquí aparecerán tus análisis.</p>
        )}
        <p className="pie izquierda">Tus grabaciones no se guardan; solo el resultado.</p>
      </section>

      <AvisoMedico />
    </div>
  )
}
