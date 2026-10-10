import { useState } from 'react'
import CampoFormulario from '../componentes/CampoFormulario.jsx'
import PanelMarca from '../componentes/PanelMarca.jsx'

/**
 * Pantalla de inicio de sesión.
 *
 * En este hito es una versión de demostración: el backend todavía no tiene
 * cuentas de usuario, así que no se verifica la contraseña ni se envía a
 * ningún lado. Solo se usa el correo para saludar al usuario.
 *
 * Recibe:
 *   - onIngresar: función que recibe { nombre, correo } al enviar el formulario.
 *   - onIrARegistro: función para pasar a la pantalla de registro.
 */
export default function InicioSesion({ onIngresar, onIrARegistro }) {
  const [correo, setCorreo] = useState('')
  const [contrasena, setContrasena] = useState('')

  // El navegador ya valida que los campos estén llenos y que el correo sea válido (required, type="email")
  const enviar = (evento) => {
    evento.preventDefault()
    const nombre = correo.split('@')[0]
    onIngresar({ nombre: nombre.charAt(0).toUpperCase() + nombre.slice(1), correo })
  }

  return (
    <div className="autenticacion">
      <PanelMarca />
      <main className="autenticacion-formulario">
        <div className="pila">
          <header className="pila pila-corta">
            <p className="sobretitulo">BIENVENIDA</p>
            <h1>Inicia sesión</h1>
            <p className="secundario">Continúa con tu seguimiento de salud.</p>
          </header>

          <form className="pila" onSubmit={enviar}>
            <CampoFormulario etiqueta="Correo electrónico" type="email" placeholder="nombre@correo.com"
              autoComplete="email" required value={correo} onChange={(e) => setCorreo(e.target.value)} />
            <CampoFormulario etiqueta="Contraseña" type="password" placeholder="Ingresa tu contraseña"
              autoComplete="current-password" required value={contrasena} onChange={(e) => setContrasena(e.target.value)} />
            <button type="submit" className="boton-primario">Ingresar</button>
          </form>

          <p className="centrado secundario">
            ¿No tienes cuenta?{' '}
            <button type="button" className="enlace" onClick={onIrARegistro}>Regístrate</button>
          </p>
          <p className="pie">Versión de demostración: las cuentas todavía no se guardan en un servidor.</p>
        </div>
      </main>
    </div>
  )
}
