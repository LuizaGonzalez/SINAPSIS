"""Forma exacta de cada respuesta que devuelve el servidor."""

from typing import Literal

from pydantic import BaseModel, Field

from sinapsis.servicios.analisis import ResultadoAnalisis


class SaludRespuesta(BaseModel):
    """Respuesta de GET /api/salud: estado del servidor y del modelo."""

    estado: Literal["ok"]
    modelo_cargado: bool
    modelo: str | None = None
    dataset: str | None = None
    fecha_entrenamiento: str | None = None


class CaracteristicaDestacadaRespuesta(BaseModel):
    """Una medida de voz que salió más alejada de lo normal en la grabación."""

    nombre: str
    valor: float
    desviaciones: float = Field(description="Desviaciones estándar respecto al promedio de entrenamiento")


class AnalisisRespuesta(BaseModel):
    """Respuesta de POST /api/analizar: el resultado que ve el usuario."""

    nivel: Literal["bajo", "medio", "alto"]
    probabilidad: float = Field(ge=0, le=1)
    recomendacion: str
    aviso: str
    duracion_s: float
    caracteristicas_destacadas: list[CaracteristicaDestacadaRespuesta]
    modelo: str

    @classmethod
    def desde_resultado(cls, r: ResultadoAnalisis) -> "AnalisisRespuesta":
        """Convierte el resultado del servicio en la respuesta que se envía al navegador.

        Parámetros:
            r: el resultado que devuelve el servicio de análisis.

        Retorna:
            La misma información como la espera el frontend.
        """
        return cls(
            nivel=r.riesgo.nivel,
            probabilidad=r.riesgo.probabilidad,
            recomendacion=r.riesgo.recomendacion,
            aviso=r.riesgo.aviso,
            duracion_s=r.duracion_s,
            caracteristicas_destacadas=[
                CaracteristicaDestacadaRespuesta(nombre=c.nombre, valor=c.valor, desviaciones=c.desviaciones)
                for c in r.caracteristicas_destacadas
            ],
            modelo=r.modelo,
        )


class ErrorRespuesta(BaseModel):
    """Respuesta cuando algo sale mal: un código y mensaje para el usuario."""

    codigo: str
    mensaje: str
