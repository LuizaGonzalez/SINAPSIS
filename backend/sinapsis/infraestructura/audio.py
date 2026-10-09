"""Capa de INFRAESTRUCTURA: convierte el audio recibido en un sonido que Praat puede analizar.

Praat (a través de Parselmouth) solo sabe abrir archivos, no datos en memoria.
Por eso la grabación se escribe un momento en un archivo temporal, se lee y se
borra enseguida. La grabación nunca se guarda de forma permanente.
"""

import os
import tempfile

import parselmouth

from sinapsis.dominio.errores import AudioIlegibleError


def leer_wav(contenido: bytes) -> parselmouth.Sound:
    """Convierte una grabación WAV en un sonido listo para analizar.

    El archivo temporal se borra siempre, tanto si la lectura sale bien como
    si falla.

    Parámetros:
        contenido: la grabación tal como llega del navegador (archivo WAV).

    Retorna:
        El sonido en el formato de Praat, del que luego se extraen las medidas de voz.

    Errores:
        AudioIlegibleError: si lo recibido no es un WAV que se pueda abrir.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(contenido)
        ruta = tmp.name
    try:
        return parselmouth.Sound(ruta)
    except Exception as error:
        raise AudioIlegibleError("No se pudo leer el audio. Envía un archivo WAV.") from error
    finally:
        os.remove(ruta)
