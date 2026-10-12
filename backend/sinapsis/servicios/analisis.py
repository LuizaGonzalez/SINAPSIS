"""Capa de SERVICIOS: el caso de uso "analizar una grabación de voz".

Orquesta las demás capas en orden: lee el audio (infraestructura), extrae las
características (dominio), obtiene la probabilidad (infraestructura) y la
interpreta (dominio). No sabe nada de HTTP.
"""

import logging
from dataclasses import dataclass

from sinapsis.dominio.caracteristicas import extraer
from sinapsis.dominio.errores import ArchivoDemasiadoGrandeError, ModeloNoDisponibleError
from sinapsis.dominio.riesgo import InterpretacionRiesgo, interpretar
from sinapsis.infraestructura.audio import leer_wav
from sinapsis.infraestructura.repositorio_modelo import RepositorioModelo

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CaracteristicaDestacada:
    nombre: str
    valor: float
    desviaciones: float


@dataclass(frozen=True)
class ResultadoAnalisis:
    riesgo: InterpretacionRiesgo
    duracion_s: float
    caracteristicas_destacadas: list[CaracteristicaDestacada]
    modelo: str


class ServicioAnalisis:
    def __init__(self, repositorio: RepositorioModelo, tamano_maximo_bytes: int, n_destacadas: int = 3):
        self._repositorio = repositorio
        self._tamano_maximo = tamano_maximo_bytes
        self._n_destacadas = n_destacadas

    def analizar(self, contenido: bytes) -> ResultadoAnalisis:
        if not self._repositorio.disponible:
            raise ModeloNoDisponibleError(
                "El modelo todavía no está entrenado. Ejecuta entrenamiento/entrenar_audio.py."
            )
        if len(contenido) > self._tamano_maximo:
            raise ArchivoDemasiadoGrandeError("El archivo es demasiado grande.")

        sonido = leer_wav(contenido)
        extraccion = extraer(sonido)
        probabilidad = self._repositorio.probabilidad_parkinson(extraccion.caracteristicas)
        logger.info("Análisis completado (duración %.1f s)", extraccion.duracion_s)

        return ResultadoAnalisis(
            riesgo=interpretar(probabilidad),
            duracion_s=round(extraccion.duracion_s, 2),
            caracteristicas_destacadas=self._destacadas(extraccion.caracteristicas),
            modelo=self._repositorio.metadatos["modelo"],
        )

    def _destacadas(self, caracteristicas: dict[str, float]) -> list[CaracteristicaDestacada]:
        """Valores más alejados del promedio de entrenamiento (no es importancia del modelo)."""
        desviaciones = self._repositorio.desviaciones(caracteristicas)
        orden = sorted(desviaciones, key=lambda n: abs(desviaciones[n]), reverse=True)
        return [
            CaracteristicaDestacada(nombre=n, valor=caracteristicas[n], desviaciones=float(desviaciones[n]))
            for n in orden[: self._n_destacadas]
        ]
