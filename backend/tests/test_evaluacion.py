"""Pruebas para evaluar los resultados del modelo"""

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from entrenamiento.evaluacion import PARTICIONES_EXTERNAS, SEMILLA, _metricas, elegir_umbral


def test_ninguna_persona_queda_en_entrenamiento_y_prueba():
    """Valida que el entrenamiento y la prueba se haga por persona"""
    grupos = np.repeat([f"S{i}" for i in range(20)], 3)
    y = np.repeat([1, 0] * 10, 3)
    X = pd.DataFrame({"x": np.arange(len(y))})
    cv = StratifiedGroupKFold(n_splits=PARTICIONES_EXTERNAS, shuffle=True, random_state=SEMILLA)
    for tr, te in cv.split(X, y, grupos):
        assert not set(grupos[tr]) & set(grupos[te])


def test_metricas_de_clasificador_que_siempre_dice_parkinson():
    """Un modelo que siempre retorna 'Parkinson',
    detecta a enfermos pero no a sanos"""
    y = np.array([1, 1, 1, 0])
    m = _metricas(y, np.ones(4))
    assert m["sensibilidad"] == 1.0
    assert m["especificidad"] == 0.0
    assert m["exactitud_balanceada"] == 0.5


def test_umbral_se_ajusta_cuando_todas_las_probabilidades_superan_0_5():
    """Si las probabilidades pasan de 0.5 (sanos < Parkinson)
    entonces el umbral falla y el ajuste es correcto (modelo ordena correctamente)"""
    y = np.array([0, 0, 0, 1, 1, 1, 1, 1, 1])
    prob = np.array([0.55, 0.60, 0.62, 0.80, 0.82, 0.85, 0.88, 0.90, 0.95])
    assert _metricas(y, prob)["exactitud_balanceada"] == 0.5
    umbral = elegir_umbral(y, prob)
    assert 0.62 < umbral < 0.80
    assert _metricas(y, prob, umbral)["exactitud_balanceada"] == 1.0


def test_umbral_por_defecto_si_el_modelo_no_distingue():
    """Si el modelo muestra la misma probabilidad a todos,
    se usa el umbral estándar de 0.5"""
    y = np.array([0, 1, 1, 1])
    assert elegir_umbral(y, np.full(4, 0.75)) == 0.5
