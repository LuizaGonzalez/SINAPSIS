import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from entrenamiento.evaluacion import PARTICIONES_EXTERNAS, SEMILLA, _metricas


def test_ninguna_persona_queda_en_entrenamiento_y_prueba():
    grupos = np.repeat([f"S{i}" for i in range(20)], 3)
    y = np.repeat([1, 0] * 10, 3)
    X = pd.DataFrame({"x": np.arange(len(y))})
    cv = StratifiedGroupKFold(n_splits=PARTICIONES_EXTERNAS, shuffle=True, random_state=SEMILLA)
    for tr, te in cv.split(X, y, grupos):
        assert not set(grupos[tr]) & set(grupos[te])


def test_metricas_de_clasificador_que_siempre_dice_parkinson():
    y = np.array([1, 1, 1, 0])
    m = _metricas(y, np.ones(4))
    assert m["sensibilidad"] == 1.0
    assert m["especificidad"] == 0.0
    assert m["exactitud_balanceada"] == 0.5
