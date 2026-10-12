"""
Extrae características acústicas de una vocal sostenida /a/.

Este módulo es el único lugar donde se calculan las características.
Se usa tanto el entrenamiento como el servicio de análisis del prototipo para garantizar que el
modelo reciba en producción exactamente el mismo tipo de datos con el que fue entrenado.
"""

from dataclasses import dataclass

import numpy as np
import parselmouth
from parselmouth.praat import call

from sinapsis.dominio.errores import AudioInvalidoError

# Rango de frecuencia usado en la literatura para voz adulta (Hz).
F0_MIN = 75
F0_MAX = 500

# Requisitos mínimos para aceptar una grabación.
DURACION_MINIMA_S = 2.0
FRACCION_SONORA_MINIMA = 0.5
INTENSIDAD_MINIMA_DB = 45.0

# Orden fijo de las características donde el modelo depende de este orden.
NOMBRES_CARACTERISTICAS = [
    "MDVP:Fo(Hz)",
    "MDVP:Fhi(Hz)",
    "MDVP:Flo(Hz)",
    "MDVP:Jitter(%)",
    "MDVP:Jitter(Abs)",
    "MDVP:RAP",
    "MDVP:PPQ",
    "Jitter:DDP",
    "MDVP:Shimmer",
    "MDVP:Shimmer(dB)",
    "Shimmer:APQ3",
    "Shimmer:APQ5",
    "MDVP:APQ",
    "Shimmer:DDA",
    "NHR",
    "HNR",
]


@dataclass(frozen=True)
class ResultadoExtraccion:
    caracteristicas: dict[str, float]
    duracion_s: float
    fraccion_sonora: float


def _preparar(sonido: parselmouth.Sound) -> parselmouth.Sound:
    """Convierte a mono y recorta silencios al inicio y al final."""
    if sonido.n_channels > 1:
        sonido = sonido.convert_to_mono()
    intensidad = sonido.to_intensity(minimum_pitch=F0_MIN)
    valores = intensidad.values[0]
    if valores.size == 0:
        return sonido
    umbral = np.max(valores) - 25  # 25 dB por debajo del pico = silencio
    sonoros = np.where(valores > umbral)[0]
    if sonoros.size == 0:
        return sonido
    t_ini = intensidad.xs()[sonoros[0]]
    t_fin = intensidad.xs()[sonoros[-1]]
    if t_fin - t_ini < 0.1:
        return sonido
    return sonido.extract_part(from_time=t_ini, to_time=t_fin, preserve_times=False)


def validar(sonido: parselmouth.Sound) -> float:
    """Verifica la duración, intensidad y presencia de voz.
    Devuelve la fracción sonora."""
    if sonido.duration < DURACION_MINIMA_S:
        raise AudioInvalidoError(
            codigo="muy_corto",
            mensaje='La grabación fue muy corta. Intenta sostener el "aaa" durante al menos 3 segundos.',
        )
    intensidad_media = call(sonido.to_intensity(minimum_pitch=F0_MIN), "Get mean", 0, 0, "energy")
    if not np.isfinite(intensidad_media) or intensidad_media < INTENSIDAD_MINIMA_DB:
        raise AudioInvalidoError(
            codigo="sin_voz",
            mensaje="No detectamos tu voz. Acércate un poco al micrófono e inténtalo de nuevo.",
        )
    pitch = sonido.to_pitch(pitch_floor=F0_MIN, pitch_ceiling=F0_MAX)
    f0 = pitch.selected_array["frequency"]
    fraccion_sonora = float(np.mean(f0 > 0)) if f0.size else 0.0
    if fraccion_sonora < FRACCION_SONORA_MINIMA:
        raise AudioInvalidoError(
            codigo="sin_voz",
            mensaje='No detectamos un "aaa" sostenido. Intenta mantener el sonido de forma continua.',
        )
    return fraccion_sonora


def extraer(sonido: parselmouth.Sound) -> ResultadoExtraccion:
    """Valida la grabación y calcula las 16 características acústicas."""
    sonido = _preparar(sonido)
    fraccion_sonora = validar(sonido)

    pitch = sonido.to_pitch(pitch_floor=F0_MIN, pitch_ceiling=F0_MAX)
    puntos = call(sonido, "To PointProcess (periodic, cc)", F0_MIN, F0_MAX)
    armonicidad = call(sonido, "To Harmonicity (cc)", 0.01, F0_MIN, 0.1, 1.0)

    rango = (0, 0, 0.0001, 0.02, 1.3)  # parámetros estándar de Praat para jitter
    rango_shimmer = (0, 0, 0.0001, 0.02, 1.3, 1.6)

    jitter_local = call(puntos, "Get jitter (local)", *rango)
    jitter_abs = call(puntos, "Get jitter (local, absolute)", *rango)
    jitter_rap = call(puntos, "Get jitter (rap)", *rango)
    jitter_ppq5 = call(puntos, "Get jitter (ppq5)", *rango)
    jitter_ddp = call(puntos, "Get jitter (ddp)", *rango)

    sp = [sonido, puntos]
    shimmer_local = call(sp, "Get shimmer (local)", *rango_shimmer)
    shimmer_db = call(sp, "Get shimmer (local_dB)", *rango_shimmer)
    shimmer_apq3 = call(sp, "Get shimmer (apq3)", *rango_shimmer)
    shimmer_apq5 = call(sp, "Get shimmer (apq5)", *rango_shimmer)
    shimmer_apq11 = call(sp, "Get shimmer (apq11)", *rango_shimmer)
    shimmer_dda = call(sp, "Get shimmer (dda)", *rango_shimmer)

    hnr = call(armonicidad, "Get mean", 0, 0)
    nhr = 1.0 / (10 ** (hnr / 10.0)) if np.isfinite(hnr) else np.nan

    valores = [
        call(pitch, "Get mean", 0, 0, "Hertz"),
        call(pitch, "Get maximum", 0, 0, "Hertz", "Parabolic"),
        call(pitch, "Get minimum", 0, 0, "Hertz", "Parabolic"),
        jitter_local * 100,  # Praat lo devuelve como fracción; UCI lo reporta en %
        jitter_abs,
        jitter_rap,
        jitter_ppq5,
        jitter_ddp,
        shimmer_local,
        shimmer_db,
        shimmer_apq3,
        shimmer_apq5,
        shimmer_apq11,
        shimmer_dda,
        nhr,
        hnr,
    ]
    caracteristicas = {n: float(v) for n, v in zip(NOMBRES_CARACTERISTICAS, valores, strict=True)}

    if any(not np.isfinite(v) for v in caracteristicas.values()):
        raise AudioInvalidoError(
            codigo="no_analizable",
            mensaje="No pudimos analizar la grabación. Busca un lugar más tranquilo y repite la prueba.",
        )
    return ResultadoExtraccion(caracteristicas, float(sonido.duration), fraccion_sonora)


def extraer_de_archivo(ruta: str) -> ResultadoExtraccion:
    """Extrae las características de un archivo .wav"""
    return extraer(parselmouth.Sound(ruta))
