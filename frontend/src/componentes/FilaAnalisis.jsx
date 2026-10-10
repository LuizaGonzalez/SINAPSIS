import { NIVELES, fechaConHora, porcentaje } from '../utilidades/formato.js'

/**
 * Un análisis dentro de una lista del historial.
 *
 * Muestra la fecha, la probabilidad y el nivel de riesgo. El nivel va escrito
 * con texto (no solo con color) para que se entienda sin distinguir colores.
 *
 * Recibe:
 *   - analisis: { fecha, nivel, probabilidad } de un análisis guardado.
 */
export default function FilaAnalisis({ analisis }) {
  return (
    <li className="fila-analisis">
      <div>
        <p className="fila-analisis-fecha">{fechaConHora(analisis.fecha)}</p>
        <p className="secundario">Probabilidad: {porcentaje(analisis.probabilidad)}</p>
      </div>
      <span className={`chip chip-${analisis.nivel}`}>{NIVELES[analisis.nivel]}</span>
    </li>
  )
}
