"""
Capa de DOMINIO: convierte la probabilidad del modelo en un nivel de riesgo y una
recomendación comprensible para una persona sin formación médica.

Los umbrales son provisionales. Deben ajustarse con la curva ROC obtenida en la
validación por persona, priorizando la sensibilidad (sección 7 del documento).
"""

from dataclasses import dataclass
from typing import Literal

NivelRiesgo = Literal["bajo", "medio", "alto"]

UMBRAL_MEDIO = 0.40
UMBRAL_ALTO = 0.70

AVISO = (
    "Este resultado es orientativo y no constituye un diagnóstico médico. "
    "Solo un especialista puede diagnosticar la enfermedad de Parkinson."
)

RECOMENDACIONES: dict[NivelRiesgo, str] = {
    "alto": (
        "Tu voz presenta patrones que se han asociado con la enfermedad de Parkinson. "
        "Te recomendamos consultar con un especialista en neurología."
    ),
    "medio": (
        "Tu voz presenta algunos patrones que se han asociado con la enfermedad de "
        "Parkinson. Considera repetir la prueba en otro momento y, si notas cambios "
        "en tu voz o en tus movimientos, consultar con un especialista."
    ),
    "bajo": (
        "No se detectaron patrones vocales asociados a la enfermedad de Parkinson. "
        "Si tienes síntomas o dudas, consulta con un profesional de la salud."
    ),
}


@dataclass(frozen=True)
class InterpretacionRiesgo:
    nivel: NivelRiesgo
    probabilidad: float
    recomendacion: str
    aviso: str = AVISO


def nivel_para(probabilidad: float) -> NivelRiesgo:
    if not 0.0 <= probabilidad <= 1.0:
        raise ValueError(f"La probabilidad debe estar entre 0 y 1, se recibió {probabilidad}")
    if probabilidad >= UMBRAL_ALTO:
        return "alto"
    if probabilidad >= UMBRAL_MEDIO:
        return "medio"
    return "bajo"


def interpretar(probabilidad: float) -> InterpretacionRiesgo:
    nivel = nivel_para(probabilidad)
    return InterpretacionRiesgo(
        nivel=nivel,
        probabilidad=round(float(probabilidad), 3),
        recomendacion=RECOMENDACIONES[nivel],
    )
