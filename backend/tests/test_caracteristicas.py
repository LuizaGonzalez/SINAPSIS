"""Pruebas de la extracción de medidas de voz"""
import numpy as np
import pytest

from sinapsis.dominio.caracteristicas import NOMBRES_CARACTERISTICAS, extraer
from sinapsis.dominio.errores import AudioInvalidoError
from tests.conftest import a_sonido, voz_sintetica


def test_extrae_todas_las_caracteristicas_en_orden(voz_valida):
    """Se obtienen 16 medidas en un orden esperado y con valores numéricos correctos."""
    resultado = extraer(voz_valida)
    assert list(resultado.caracteristicas) == NOMBRES_CARACTERISTICAS
    assert all(np.isfinite(v) for v in resultado.caracteristicas.values())


def test_frecuencia_fundamental_coincide_con_la_senal():
    """Una voz de 200 Hz se mide con un tono de la misma frecuencia."""
    resultado = extraer(a_sonido(voz_sintetica(f0=200)))
    assert resultado.caracteristicas["MDVP:Fo(Hz)"] == pytest.approx(200, rel=0.05)


def test_mas_jitter_en_la_senal_aumenta_el_jitter_medido():
    """Una señal más inestable produce un hitter medido mayor."""
    estable = extraer(a_sonido(voz_sintetica(jitter=0.002, semilla=3)))
    inestable = extraer(a_sonido(voz_sintetica(jitter=0.02, semilla=3)))
    assert inestable.caracteristicas["MDVP:Jitter(%)"] > estable.caracteristicas["MDVP:Jitter(%)"]


def test_rechaza_grabacion_corta(voz_corta):
    """Rechaza una grabación corta, lanzando un error"""
    with pytest.raises(AudioInvalidoError) as error:
        extraer(voz_corta)
    assert error.value.codigo == "muy_corto"


def test_rechaza_grabacion_sin_voz(silencio):
    """Rechaza una grabación sin voz, lanzando un error"""
    with pytest.raises(AudioInvalidoError) as error:
        extraer(silencio)
    assert error.value.codigo == "sin_voz"
