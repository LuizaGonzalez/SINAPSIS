"""Endpoints que el frontend puede llamar."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Request, UploadFile

from sinapsis.api.esquemas import AnalisisRespuesta, ErrorRespuesta, SaludRespuesta
from sinapsis.infraestructura.repositorio_modelo import RepositorioModelo
from sinapsis.servicios.analisis import ServicioAnalisis

router = APIRouter(prefix="/api")

# Errores que puede devolver /api/analizar
ERRORES_DOCUMENTADOS = {
    400: {"model": ErrorRespuesta, "description": "El archivo no es un WAV legible"},
    413: {"model": ErrorRespuesta, "description": "El archivo es demasiado grande"},
    422: {
        "model": ErrorRespuesta,
        "description": "Grabación muy corta, sin voz o no analizable",
    },
    503: {"model": ErrorRespuesta, "description": "El modelo todavía no está entrenado"},
}


def obtener_repositorio(request: Request) -> RepositorioModelo:
    """Entrega el modelo cargado al iniciar la aplicación.

    Parámetros:
        request: la petición que está llegando.

    Retorna:
        El repositorio del modelo.
    """
    return request.app.state.repositorio


def obtener_servicio(request: Request) -> ServicioAnalisis:
    """Entrega el servicio de análisis creado al iniciar la aplicación.

    Parámetros:
        request: la petición que está llegando.

    Retorna:
        El servicio que analiza las grabaciones.
    """
    return request.app.state.servicio


@router.get("/salud", response_model=SaludRespuesta)
def salud(repositorio: Annotated[RepositorioModelo, Depends(obtener_repositorio)]) -> SaludRespuesta:
    """Revisa que el servidor esté funcionando y qué modelo tiene cargado antes
    de usar el prototipo.

    Parámetros:
        repositorio: el modelo cargado.

    Retorna:
        El estado del servidor, si hay modelo cargado y, si lo hay, su nombre,
        el dataset con el que se entrenó y la fecha.
    """
    meta = repositorio.metadatos
    return SaludRespuesta(
        estado="ok",
        modelo_cargado=repositorio.disponible,
        modelo=meta["modelo"],
        dataset=meta["dataset"],
        fecha_entrenamiento=meta["fecha"],
    )


@router.post("/analizar", response_model=AnalisisRespuesta, responses=ERRORES_DOCUMENTADOS)
def analizar(
    audio: Annotated[UploadFile, File(description="Grabación WAV de la vocal /a/")],
    servicio: Annotated[ServicioAnalisis, Depends(obtener_servicio)],
) -> AnalisisRespuesta:
    """Analiza una grabación de la vocal /a/ y devuelve el nivel de riesgo.

    Parámetros:
        audio: el archivo WAV que envía el navegador.
        servicio: el servicio de análisis.

    Retorna:
        El nivel de riesgo (bajo, medio o alto), la probabilidad, la
        recomendación, el aviso de que no es un diagnóstico y las medidas de
        voz más inusuales.

    Errores:
        Si algo falla (audio ilegible, muy corto, sin voz, sin modelo...), el
        servicio lanza un error que se convierte en la respuesta
        HTTP.
    """
    resultado = servicio.analizar(audio.file.read())
    return AnalisisRespuesta.desde_resultado(resultado)
