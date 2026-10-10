import { Microfono, Pulso } from './Iconos.jsx'

/**
 * Presentación de SINAPSIS en las pantallas de inicio de sesión y registro.
 *
 * En computador es el panel verde de la izquierda. En celular solo se ve el
 * logo y el lema encima del formulario (el resto se oculta con CSS).
 */
export default function PanelMarca() {
  return (
    <aside className="panel-marca">
      <div className="logo">
        <span className="logo-icono"><Pulso tamano={26} /></span>
        <span className="logo-texto">SINAPSIS</span>
      </div>
      <div className="panel-marca-mensaje">
        <p className="sobretitulo">SALUD DESDE TU VOZ</p>
        <h2>Cuida tu salud desde tu voz</h2>
        <p className="secundario">
          Una prueba breve y tranquila puede ayudarte a reconocer cambios en tu voz asociados a la
          enfermedad de Parkinson.
        </p>
      </div>
      <p className="panel-marca-pie"><Microfono /> Solo necesitas 5 segundos</p>
    </aside>
  )
}
