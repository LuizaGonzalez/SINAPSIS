"""Capa de API: las direcciones (endpoints) que el frontend puede llamar.

Aquí no hay lógica de IA: cada endpoint solo recibe la petición, le pasa el
trabajo al servicio y devuelve la respuesta.

Endpoints:
    GET  /api/salud      indica si el servidor está activo y si hay modelo cargado.
    POST /api/analizar   recibe una grabación y devuelve el nivel de riesgo.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Request, UploadFile

from sinapsis.api.esquemas import AnalisisRespuesta, ErrorRespuesta, SaludRespuesta
from sinapsis.infraestructura.repositorio_modelo import RepositorioModelo
from sinapsis.servicios.analisis import ServicioAnalisis

router = APIRouter(prefix="/api")

# Errores que puede devolver /api/analizar; aparecen explicados en la página /docs
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

    FastAPI llama a esta función por su cuenta (con Depends) cada vez que un
    endpoint necesita el modelo.

    Parámetros:
        request: la petición que está llegando.

    Retorna:
        El repositorio del modelo, creado en main.py al arrancar.
    """
    return request.app.state.repositorio


def obtener_servicio(request: Request) -> ServicioAnalisis:
    """Entrega el servicio de análisis creado al iniciar la aplicación.

    Parámetros:
        request: la petición que está llegando.

    Retorna:
        El servicio que analiza las grabaciones, creado en main.py al arrancar.
    """
    return request.app.state.servicio


@router.get("/salud", response_model=SaludRespuesta)
def salud(repositorio: Annotated[RepositorioModelo, Depends(obtener_repositorio)]) -> SaludRespuesta:
    """Revisa que el servidor esté funcionando y qué modelo tiene cargado.

    Sirve para comprobar rápido que todo está bien antes de usar el prototipo.

    Parámetros:
        repositorio: el modelo cargado (lo entrega FastAPI automáticamente).

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
        servicio: el servicio de análisis (lo entrega FastAPI automáticamente).

    Retorna:
        El nivel de riesgo (bajo, medio o alto), la probabilidad, la
        recomendación, el aviso de que no es un diagnóstico y las medidas de
        voz más inusuales.

    Errores:
        Si algo falla (audio ilegible, muy corto, sin voz, sin modelo...), el
        servicio lanza un error que api/errores.py convierte en la respuesta
        HTTP adecuada.
    """
    # Se declara con "def" (no "async def") porque el análisis con Parselmouth es
    # cálculo pesado y síncrono: así FastAPI lo ejecuta en un hilo aparte y el
    # servidor puede seguir atendiendo otras peticiones mientras tanto.
    resultado = servicio.analizar(audio.file.read())
    return AnalisisRespuesta.desde_resultado(resultado)
