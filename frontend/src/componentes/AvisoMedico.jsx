import { Info } from './Iconos.jsx'

/**
 * Aviso de que SINAPSIS no hace diagnósticos médicos.
 *
 * Aparece en Inicio y en Resultado, para que el usuario no lo pierda de vista.
 *
 * Recibe:
 *   - texto (opcional): un aviso distinto al de siempre, por ejemplo el que
 *     envía el servidor junto con el resultado.
 */
export default function AvisoMedico({ texto }) {
  return (
    <section className="nota fila-inicio">
      <Info />
      <span>
        {texto ?? (
          <>
            <strong>Importante:</strong> SINAPSIS es un prototipo académico. Su resultado es orientativo y{' '}
            <strong>no constituye un diagnóstico médico</strong>.
          </>
        )}
      </span>
    </section>
  )
}
