import { useState } from 'react'
import CampoFormulario from '../componentes/CampoFormulario.jsx'
import PanelMarca from '../componentes/PanelMarca.jsx'

const LONGITUD_MINIMA = 8

/**
 * Pantalla de registro.
 *
 * Como el inicio de sesión, es una versión de demostración: revisa que los
 * datos estén completos y que las contraseñas coincidan, pero no crea la
 * cuenta en un servidor.
 *
 * Recibe:
 *   - onCrearCuenta: función que recibe { nombre, correo } cuando los datos son válidos.
 *   - onIrAInicioSesion: función para volver a la pantalla de inicio de sesión.
 */
export default function Registro({ onCrearCuenta, onIrAInicioSesion }) {
  const [datos, setDatos] = useState({ nombre: '', correo: '', contrasena: '', confirmacion: '' })
  const [error, setError] = useState(null)

  // Actualiza un solo campo del formulario
  const cambiar = (campo) => (evento) => setDatos({ ...datos, [campo]: evento.target.value })

  const enviar = (evento) => {
    evento.preventDefault()
    if (datos.contrasena.length < LONGITUD_MINIMA) {
      setError(`La contraseña debe tener al menos ${LONGITUD_MINIMA} caracteres.`)
    } else if (datos.contrasena !== datos.confirmacion) {
      setError('Las contraseñas no coinciden.')
    } else {
      onCrearCuenta({ nombre: datos.nombre.trim().split(' ')[0], correo: datos.correo })
    }
  }

  return (
    <div className="autenticacion">
      <PanelMarca />
      <main className="autenticacion-formulario">
        <div className="pila">
          <header className="pila pila-corta">
            <p className="sobretitulo">CREA TU CUENTA</p>
            <h1>Comienza tu seguimiento</h1>
          </header>

          <form className="pila" onSubmit={enviar}>
            <CampoFormulario etiqueta="Nombre" placeholder="Tu nombre" autoComplete="name" required
              value={datos.nombre} onChange={cambiar('nombre')} />
            <CampoFormulario etiqueta="Correo electrónico" type="email" placeholder="nombre@correo.com"
              autoComplete="email" required value={datos.correo} onChange={cambiar('correo')} />
            <div className="campos-pareja">
              <CampoFormulario etiqueta="Contraseña" type="password" placeholder={`Mínimo ${LONGITUD_MINIMA} caracteres`}
                autoComplete="new-password" required value={datos.contrasena} onChange={cambiar('contrasena')} />
              <CampoFormulario etiqueta="Confirmar contraseña" type="password" placeholder="Repite tu contraseña"
                autoComplete="new-password" required value={datos.confirmacion} onChange={cambiar('confirmacion')} />
            </div>
            <label className="casilla">
              <input type="checkbox" required />
              <span>Acepto los Términos y la Política de privacidad</span>
            </label>

            {error && <p className="error" role="alert">{error}</p>}
            <button type="submit" className="boton-primario">Crear cuenta</button>
          </form>

          <p className="centrado secundario">
            ¿Ya tienes cuenta?{' '}
            <button type="button" className="enlace" onClick={onIrAInicioSesion}>Inicia sesión</button>
          </p>
        </div>
      </main>
    </div>
  )
}
