import { Casa, Pulso, Reloj } from './Iconos.jsx'

const DESTINOS = [
  { id: 'inicio', texto: 'Inicio', icono: <Casa /> },
  { id: 'prueba', texto: 'Pruebas', icono: <Pulso /> },
  { id: 'historial', texto: 'Historial', icono: <Reloj /> },
]

/**
 * Barra de navegación principal (solo se muestra cuando hay sesión iniciada).
 *
 * En celular va abajo; en computador va arriba, con el nombre de SINAPSIS a la
 * izquierda y la inicial del usuario a la derecha.
 *
 * Recibe:
 *   - activa: el destino seleccionado ('inicio', 'prueba' o 'historial').
 *   - onIr: función que recibe el destino elegido.
 *   - usuario: { nombre } del usuario, para mostrar su inicial.
 */
export default function BarraNavegacion({ activa, onIr, usuario }) {
  return (
    <nav className="barra" aria-label="Navegación principal">
      <span className="marca">SINAPSIS</span>
      {DESTINOS.map(({ id, texto, icono }) => (
        <button
          key={id}
          className={activa === id ? 'activa' : ''}
          aria-current={activa === id ? 'page' : undefined}
          onClick={() => onIr(id)}
        >
          {icono}{texto}
        </button>
      ))}
      <span className="avatar avatar-barra" aria-hidden="true">{usuario.nombre[0]}</span>
    </nav>
  )
}
