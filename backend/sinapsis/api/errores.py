"""Capa de API: convierte los errores de la aplicación en respuestas HTTP.

Las demás capas solo dicen QUÉ salió mal (por ejemplo, "el audio no tiene voz").
Este archivo es el único que decide qué código HTTP se responde en cada caso.
Así el dominio no depende de FastAPI.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sinapsis.dominio.errores import (
    ArchivoDemasiadoGrandeError,
    AudioIlegibleError,
    AudioInvalidoError,
    ModeloNoDisponibleError,
    SinapsisError,
)

# Qué código HTTP corresponde a cada error. Si aparece uno que no está aquí, se responde 500.
CODIGOS_HTTP: dict[type[SinapsisError], int] = {
    AudioIlegibleError: 400,
    ArchivoDemasiadoGrandeError: 413,
    AudioInvalidoError: 422,
    ModeloNoDisponibleError: 503,
}


def registrar_manejadores(app: FastAPI) -> None:
    """Le enseña a la aplicación cómo responder cuando ocurre un error de SINAPSIS.

    Todas las respuestas de error tienen la misma forma: {codigo, mensaje}.

    Parámetros:
        app: la aplicación FastAPI a la que se le agregan los manejadores.
    """

    @app.exception_handler(SinapsisError)
    async def manejar_error_sinapsis(_: Request, error: SinapsisError) -> JSONResponse:
        estado = CODIGOS_HTTP.get(type(error), 500)
        return JSONResponse(status_code=estado, content={"codigo": error.codigo, "mensaje": error.mensaje})
