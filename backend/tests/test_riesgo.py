"""Pruebas de la interpretación del nivel de riesgo."""

import pytest

from sinapsis.dominio.riesgo import UMBRAL_ALTO, UMBRAL_MEDIO, interpretar, nivel_para


@pytest.mark.parametrize(
    ("probabilidad", "nivel"),
    [
        (0.0, "bajo"),
        (UMBRAL_MEDIO - 0.01, "bajo"),
        (UMBRAL_MEDIO, "medio"),
        (UMBRAL_ALTO, "alto"),
        (1.0, "alto"),
    ],
)
def test_niveles_segun_umbral(probabilidad, nivel):
    """La probabilidad va de acuerdo al nivel (bajo, medio, alto) incluye los límites exactos."""
    assert interpretar(probabilidad).nivel == nivel


def test_siempre_incluye_aviso_de_no_diagnostico():
    """Los resultados deben mostrar un aviso de que no es un diagnóstico."""
    for p in (0.1, 0.5, 0.9):
        assert "no constituye un diagnóstico" in interpretar(p).aviso


@pytest.mark.parametrize("invalida", [-0.1, 1.5])
def test_rechaza_probabilidades_fuera_de_rango(invalida):
    """Si se obtiene una probabilidad menor a 0 o mayor a 1, lanza un error"""
    with pytest.raises(ValueError):
        nivel_para(invalida)
