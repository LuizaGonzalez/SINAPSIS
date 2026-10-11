"""Voces sintéticas para probar sin depender de datasets reales."""

import numpy as np
import parselmouth
import pytest

FRECUENCIA_MUESTREO = 44100


def voz_sintetica(
    f0: float = 150.0,
    jitter: float = 0.004,
    shimmer: float = 0.03,
    ruido: float = 0.01,
    duracion: float = 4.0,
    semilla: int = 0,
) -> np.ndarray:
    """Genera una vocal sostenida para usar en los tests.
    Parámetros:
    - f0: tono en Hz
    - jitter: varación entre ciclos
    - shimmer: varación de volumen
    - ruido: ruido de fondo
    - duración: segundos que dura el audio
    - semilla: resultado repetible

    Retorna:
    Devuelve la señal normalizada
    """
    rng = np.random.default_rng(semilla)
    ciclos, t = [], 0.0
    while t < duracion:
        periodo = 1 / (f0 * (1 + rng.normal(0, jitter)))
        tiempos = np.arange(int(periodo * FRECUENCIA_MUESTREO)) / FRECUENCIA_MUESTREO
        amplitud = 1 + rng.normal(0, shimmer)
        ciclos.append(amplitud * sum(np.sin(2 * np.pi * k * tiempos / periodo) / k for k in range(1, 8)))
        t += periodo
    senal = np.concatenate(ciclos)
    senal += ruido * rng.normal(size=senal.size)
    return 0.3 * senal / np.max(np.abs(senal))


def a_sonido(senal: np.ndarray) -> parselmouth.Sound:
    """Convierte una señal en un objeto Sound"""
    return parselmouth.Sound(senal, sampling_frequency=FRECUENCIA_MUESTREO)


@pytest.fixture
def voz_valida() -> parselmouth.Sound:
    """Voz sintética normal de 4s"""
    return a_sonido(voz_sintetica())


@pytest.fixture
def voz_corta() -> parselmouth.Sound:
    """Voz sintética corta de solo 1s"""
    return a_sonido(voz_sintetica(duracion=1.0))


@pytest.fixture
def silencio() -> parselmouth.Sound:
    """4 segundos de ruido inaudible sin voz"""
    return a_sonido(0.0005 * np.random.default_rng(1).normal(size=FRECUENCIA_MUESTREO * 4))
