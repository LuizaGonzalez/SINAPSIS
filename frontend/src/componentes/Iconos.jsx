/**
 * Íconos de la interfaz, dibujados en SVG.
 *
 * Están hechos a mano para no depender de librerías externas. Toman el color
 * del texto que los rodea (currentColor).
 */

// Estilo común de las líneas de los íconos
const base = { fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round' }

export const Volver = () => (<svg width="18" height="18" viewBox="0 0 24 24" {...base} strokeWidth={2.4}><path d="M15 18l-6-6 6-6" /></svg>)
export const Siguiente = () => (<svg width="16" height="16" viewBox="0 0 24 24" {...base}><path d="M9 18l6-6-6-6" /></svg>)
export const Microfono = ({ tamano = 20 }) => (<svg width={tamano} height={tamano} viewBox="0 0 24 24" {...base}><rect x="9" y="3" width="6" height="11" rx="3" /><path d="M5 11a7 7 0 0 0 14 0" /><path d="M12 18v3" /></svg>)
export const Detener = () => (<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><rect x="5" y="5" width="14" height="14" rx="2" /></svg>)
export const Info = () => (<svg width="18" height="18" viewBox="0 0 24 24" {...base}><circle cx="12" cy="12" r="9" /><path d="M12 11v5" /><path d="M12 8h.01" /></svg>)
export const Alerta = () => (<svg width="20" height="20" viewBox="0 0 24 24" {...base}><path d="M12 3l10 18H2L12 3z" /><path d="M12 10v4" /><path d="M12 17h.01" /></svg>)
export const Check = () => (<svg width="14" height="14" viewBox="0 0 24 24" {...base} strokeWidth={2.6}><path d="M20 6L9 17l-5-5" /></svg>)
export const Casa = () => (<svg width="20" height="20" viewBox="0 0 24 24" {...base}><path d="M3 11l9-7 9 7" /><path d="M5 10v10h14V10" /></svg>)
export const Pulso = ({ tamano = 20 }) => (<svg width={tamano} height={tamano} viewBox="0 0 24 24" {...base}><path d="M3 12h4l3-7 4 14 3-7h4" /></svg>)
export const Reloj = () => (<svg width="20" height="20" viewBox="0 0 24 24" {...base}><path d="M3.05 11A9 9 0 1 0 4 7" /><path d="M1 4l3 3 3-3" /><path d="M12 8v4l2 2" /></svg>)
export const Grafica = () => (<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="12" width="4" height="9" rx="1" /><rect x="10" y="7" width="4" height="14" rx="1" /><rect x="17" y="3" width="4" height="18" rx="1" /></svg>)
