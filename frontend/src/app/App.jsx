import { useState } from 'react'
import BarraNavegacion from '../componentes/BarraNavegacion.jsx'
import Historial from '../pantallas/Historial.jsx'
import Inicio from '../pantallas/Inicio.jsx'
import InicioSesion from '../pantallas/InicioSesion.jsx'
import PruebaVoz from '../pantallas/PruebaVoz.jsx'
import Registro from '../pantallas/Registro.jsx'
import Resultado from '../pantallas/Resultado.jsx'

/**
 * Componente principal: decide qué pantalla se muestra.
 *
 * Sin sesión:  inicio de sesión <-> registro
 * Con sesión:  inicio -> prueba de voz -> resultado, e historial
 *
 * Guarda:
 *   - usuario: { nombre, correo } o null si no hay sesión.
 *   - pantalla: la pantalla actual.
 *   - historial: los resultados de esta sesión, del más reciente al más antiguo.
 *     Solo resultados (fecha, nivel, probabilidad), nunca grabaciones. Vive en
 *     memoria: se borra al cerrar sesión o recargar la página.
 *   - resultado: el último análisis, para mostrarlo en la pantalla de resultado.
 */
export default function App() {
  const [usuario, setUsuario] = useState(null)
  const [pantalla, setPantalla] = useState('inicio-sesion')
  const [historial, setHistorial] = useState([])
  const [resultado, setResultado] = useState(null)

  const entrar = (datosUsuario) => {
    setUsuario(datosUsuario)
    setPantalla('inicio')
  }

  const salir = () => {
    setUsuario(null)
    setHistorial([])
    setResultado(null)
    setPantalla('inicio-sesion')
  }

  // Guarda el análisis en el historial y muestra el resultado
  const recibirResultado = (respuesta) => {
    const analisis = { ...respuesta, fecha: new Date() }
    setHistorial((anteriores) => [analisis, ...anteriores])
    setResultado(analisis)
    setPantalla('resultado')
  }

  if (!usuario) {
    return (
      <div className="marco marco-autenticacion">
        {pantalla === 'registro' ? (
          <Registro onCrearCuenta={entrar} onIrAInicioSesion={() => setPantalla('inicio-sesion')} />
        ) : (
          <InicioSesion onIngresar={entrar} onIrARegistro={() => setPantalla('registro')} />
        )}
      </div>
    )
  }

  // La prueba y el resultado se marcan como "Pruebas" en la barra de navegación
  const activa = pantalla === 'resultado' ? 'prueba' : pantalla

  return (
    <div className="marco">
      <main className="contenido">
        {pantalla === 'inicio' && (
          <Inicio
            usuario={usuario}
            historial={historial}
            onIniciarPrueba={() => setPantalla('prueba')}
            onVerHistorial={() => setPantalla('historial')}
            onCerrarSesion={salir}
          />
        )}
        {pantalla === 'prueba' && (
          <PruebaVoz onVolver={() => setPantalla('inicio')} onResultado={recibirResultado} />
        )}
        {pantalla === 'resultado' && resultado && (
          <Resultado
            resultado={resultado}
            onVolver={() => setPantalla('inicio')}
            onRepetir={() => setPantalla('prueba')}
          />
        )}
        {pantalla === 'historial' && (
          <Historial historial={historial} onIniciarPrueba={() => setPantalla('prueba')} />
        )}
      </main>
      <BarraNavegacion activa={activa} onIr={setPantalla} usuario={usuario} />
    </div>
  )
}
