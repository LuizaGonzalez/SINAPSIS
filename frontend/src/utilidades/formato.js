/**
 * Funciones pequeñas para mostrar datos de forma legible.
 * Se usan en varias pantallas, por eso están en un solo lugar.
 */

// Texto de cada nivel de riesgo que devuelve el servidor
export const NIVELES = {
  bajo: 'Bajo',
  medio: 'Medio',
  alto: 'Alto',
}

/**
 * Convierte una probabilidad (0 a 1) en porcentaje.
 *
 * Recibe: probabilidad, un número entre 0 y 1.
 * Retorna: texto como "56 %".
 */
export function porcentaje(probabilidad) {
  return `${Math.round(probabilidad * 100)} %`
}

// Abreviaturas de los meses, para escribir fechas cortas
const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

/**
 * Muestra una fecha corta, por ejemplo "10 oct 2026".
 *
 * Recibe: fecha, un objeto Date.
 * Retorna: el texto de la fecha.
 */
export function fechaCorta(fecha) {
  return `${fecha.getDate()} ${MESES[fecha.getMonth()]} ${fecha.getFullYear()}`
}

/**
 * Muestra la fecha con la hora, por ejemplo "10 oct 2026 · 2:30 p. m.".
 *
 * Recibe: fecha, un objeto Date.
 * Retorna: el texto de la fecha y la hora.
 */
export function fechaConHora(fecha) {
  const hora = fecha.toLocaleTimeString('es-CO', { hour: 'numeric', minute: '2-digit' })
  return `${fechaCorta(fecha)} · ${hora}`
}

/**
 * Muestra la fecha larga de hoy, por ejemplo "sábado, 10 de octubre de 2026".
 *
 * Retorna: el texto de la fecha.
 */
export function fechaLargaHoy() {
  return new Date().toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
}
