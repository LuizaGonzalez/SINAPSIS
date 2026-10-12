"""Pruebas de la API: se llama a los endpoints como lo haría el navegador."""

import io

import numpy as np
import pandas as pd
import pytest
import soundfile as sf
from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from sinapsis.dominio.caracteristicas import NOMBRES_CARACTERISTICAS
from sinapsis.infraestructura.repositorio_modelo import RepositorioModelo
from sinapsis.main import crear_app
from tests.conftest import FRECUENCIA_MUESTREO, voz_sintetica


def wav(senal: np.ndarray) -> bytes:
    """Convierte una señal de audio en un archivo WAV en memoria, como el que envía el navegador."""
    buffer = io.BytesIO()
    sf.write(buffer, senal, FRECUENCIA_MUESTREO, format="WAV")
    return buffer.getvalue()


def enviar(cliente: TestClient, datos: bytes):
    """Envía un archivo a /api/analizar, igual que el frontend."""
    return cliente.post("/api/analizar", files={"audio": ("a.wav", datos, "audio/wav")})


@pytest.fixture
def repositorio_de_prueba() -> RepositorioModelo:
    """Modelo pequeño entrenado con datos inventados, para probar sin el modelo real."""
    rng = np.random.default_rng(0)
    X = pd.DataFrame(rng.normal(size=(40, len(NOMBRES_CARACTERISTICAS))), columns=NOMBRES_CARACTERISTICAS)
    y = np.array([0, 1] * 20)
    pipeline = Pipeline([("escalar", StandardScaler()), ("clf", LogisticRegression())]).fit(X, y)
    return RepositorioModelo(
        {
            "pipeline": pipeline,
            "caracteristicas": NOMBRES_CARACTERISTICAS,
            "modelo": "prueba",
            "dataset": "sintetico",
            "fecha": "2026-01-01T00:00:00",
        }
    )


@pytest.fixture
def cliente(repositorio_de_prueba):
    """Aplicación de prueba con modelo cargado."""
    with TestClient(crear_app(repositorio=repositorio_de_prueba)) as c:
        yield c


@pytest.fixture
def cliente_sin_modelo():
    """Aplicación de prueba sin modelo, como cuando todavía no se ha entrenado."""
    with TestClient(crear_app(repositorio=RepositorioModelo(None))) as c:
        yield c


def test_salud(cliente):
    """/api/salud responde y dice que hay modelo cargado."""
    respuesta = cliente.get("/api/salud")
    assert respuesta.status_code == 200
    assert respuesta.json()["modelo_cargado"] is True


def test_analiza_voz_valida(cliente):
    """Una voz válida devuelve un nivel de riesgo, una probabilidad y 3 medidas destacadas."""
    respuesta = enviar(cliente, wav(voz_sintetica()))
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["nivel"] in {"bajo", "medio", "alto"}
    assert 0 <= cuerpo["probabilidad"] <= 1
    assert len(cuerpo["caracteristicas_destacadas"]) == 3


def test_rechaza_audio_corto_con_422(cliente):
    """Una grabación de 1 segundo se rechaza por ser muy corta."""
    respuesta = enviar(cliente, wav(voz_sintetica(duracion=1.0)))
    assert respuesta.status_code == 422
    assert respuesta.json()["codigo"] == "muy_corto"


def test_rechaza_archivo_que_no_es_audio(cliente):
    """Un archivo que no es audio se rechaza con 400."""
    respuesta = enviar(cliente, b"no es audio")
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "audio_ilegible"


def test_sin_modelo_responde_503(cliente_sin_modelo):
    """Sin modelo entrenado, el análisis responde 503 en vez de fallar."""
    assert cliente_sin_modelo.get("/api/salud").json()["modelo_cargado"] is False
    respuesta = enviar(cliente_sin_modelo, wav(voz_sintetica()))
    assert respuesta.status_code == 503
    assert respuesta.json()["codigo"] == "modelo_no_disponible"
