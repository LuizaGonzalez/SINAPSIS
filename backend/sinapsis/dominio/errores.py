"""Son los errores del dominio de modo que las capas internas
lanzan estos errores pero solo la capa de API los traduce a códigos HTTP.
"""


class SinapsisError(Exception):
    """Error base de la aplicación, con un código y un mensaje para el usuario."""

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
    """El archivo recibido es un audio WAV demasiado grande."""

    codigo = "archivo_grande"


class ModeloNoDisponibleError(SinapsisError):
    """Todavía no hay un modelo entrenado para hacer predicciones."""

    codigo = "modelo_no_disponible"
