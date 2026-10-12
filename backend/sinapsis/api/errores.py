"""Convierte los errores de la aplicación en respuestas HTTP."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sinapsis.dominio.errores import (
    ArchivoDemasiadoGrandeError,
    AudioIlegibleError,
    AudioInvalidoError,
    ModeloNoDisponibleError,
    SinapsisError,
)

CODIGOS_HTTP: dict[type[SinapsisError], int] = {
    AudioIlegibleError: 400,
    ArchivoDemasiadoGrandeError: 413,
    AudioInvalidoError: 422,
    ModeloNoDisponibleError: 503,
}


def registrar_manejadores(app: FastAPI) -> None:
    """Enseña a la aplicación cómo responder cuando ocurre un error en SINAPSIS.

    Parámetros:
        app: la aplicación FastAPI a la que se le agregan los manejadores.
    """

    @app.exception_handler(SinapsisError)
    async def manejar_error_sinapsis(_: Request, error: SinapsisError) -> JSONResponse:
        estado = CODIGOS_HTTP.get(type(error), 500)
        return JSONResponse(status_code=estado, content={"codigo": error.codigo, "mensaje": error.mensaje})
