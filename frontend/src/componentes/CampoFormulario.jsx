/**
 * Campo de formulario con su etiqueta visible encima.
 *
 * Se usa en inicio de sesión y registro. La etiqueta siempre se ve (no solo el
 * texto de ayuda dentro del campo), porque así lo recomiendan las pautas de
 * accesibilidad.
 *
 * Recibe:
 *   - etiqueta: el texto que va encima del campo.
 *   - el resto de propiedades (type, value, onChange, required...) pasan
 *     directamente al <input>.
 */
export default function CampoFormulario({ etiqueta, ...propiedades }) {
  return (
    <label className="campo">
      <span>{etiqueta}</span>
      <input {...propiedades} />
    </label>
  )
}
