"""Errores del dominio.

Las capas internas lanzan estos errores; solo la capa de API los traduce a
códigos HTTP. Así el dominio no depende de FastAPI.
"""


class SinapsisError(Exception):
    """Error base de la aplicación, con un código estable y un mensaje para el usuario."""

    codigo = "error"

    def __init__(self, mensaje: str, codigo: str | None = None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        if codigo:
            self.codigo = codigo


class AudioInvalidoError(SinapsisError):
    """La grabación se pudo leer, pero no cumple las condiciones para analizarse."""

    codigo = "audio_invalido"


class AudioIlegibleError(SinapsisError):
    """El archivo recibido no es un audio WAV legible."""

    codigo = "audio_ilegible"


class ArchivoDemasiadoGrandeError(SinapsisError):
    codigo = "archivo_grande"


class ModeloNoDisponibleError(SinapsisError):
    """Todavía no hay un modelo entrenado para hacer predicciones."""

    codigo = "modelo_no_disponible"
