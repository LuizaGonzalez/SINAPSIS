"""
Evalua los modelos con validación cruzada por persona.
"""

import json
import os
from datetime import datetime
from typing import Any

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold, cross_val_predict
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

SEMILLA = 42
PARTICIONES_EXTERNAS = 5
PARTICIONES_INTERNAS = 3
UMBRAL_POR_DEFECTO = 0.5


def modelos() -> dict[str, tuple[Any, dict[str, list]]]:
    """Modelos a comparar y sus hiperparámetros (búsqueda interna)."""
    return {
        "Base (clase mayoritaria)": (DummyClassifier(strategy="most_frequent"), {}),
        "Árbol de decisión": (
            DecisionTreeClassifier(class_weight="balanced", random_state=SEMILLA),
            {"clf__max_depth": [2, 3, 4, 6], "clf__min_samples_leaf": [2, 5, 10]},
        ),
        "Random Forest": (
            RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=SEMILLA),
            {"clf__max_depth": [3, 5, None], "clf__min_samples_leaf": [1, 3, 5]},
        ),
        "SVM (RBF)": (
            CalibratedClassifierCV(
                SVC(kernel="rbf", class_weight="balanced", random_state=SEMILLA),
                method="sigmoid",
                cv=3,
                ensemble=False,
            ),
            {"clf__estimator__C": [0.1, 1, 10, 100], "clf__estimator__gamma": ["scale", 0.01, 0.1]},
        ),
        "MLP": (
            MLPClassifier(max_iter=2000, early_stopping=False, random_state=SEMILLA),
            {"clf__hidden_layer_sizes": [(16,), (32,), (16, 8)], "clf__alpha": [1e-3, 1e-2, 1e-1]},
        ),
    }


def _pipeline(clf) -> Pipeline:
    """Conecta los datos iniciales con el modelo final"""
    return Pipeline([("escalar", StandardScaler()), ("clf", clf)])


def _validacion_interna() -> StratifiedGroupKFold:
    """Mantiene la grabación de una misma persona en una misma partición"""
    return StratifiedGroupKFold(n_splits=PARTICIONES_INTERNAS, shuffle=True, random_state=SEMILLA)


def _ajustar(
    clf, rejilla: dict, X: pd.DataFrame, y: np.ndarray, grupos: np.ndarray
) -> tuple[Pipeline, float]:
    """Ajusta el modelo y elige su umbral de decisión usando solo los datos validados.

    Pasos:
    1. Busca los mejores hiperparámetros con todas las combinaciones que prueba GridSearchCV usando AUC
    para ver como el modelo ordena a las personas sin depender de un umbral
    2. Con la mejor configuración, obtiene probabilidades con los mismos datos por GridSearchCV
    y elige el umbral que maximiza la exactitud balanceada.
    3. Reentrena el modelo con los datos recibidos.
    """
    pipe = _pipeline(clone(clf))
    interna = _validacion_interna()
    if rejilla:
        busqueda = GridSearchCV(pipe, rejilla, cv=interna, scoring="roc_auc", n_jobs=-1)
        busqueda.fit(X, y, groups=grupos)
        pipe = clone(busqueda.best_estimator_)
    prob_oof = cross_val_predict(pipe, X, y, groups=grupos, cv=interna, method="predict_proba", n_jobs=-1)
    umbral = elegir_umbral(y, prob_oof[:, 1])
    return pipe.fit(X, y), umbral


def elegir_umbral(y: np.ndarray, prob: np.ndarray) -> float:
    """Umbral que maximiza la exactitud balanceada.

    Se prueban los puntos medios entre probabilidades consecutivas. En caso de
    empate se elige el más cercano a 0.5. Si todas las probabilidades son
    iguales, se usa 0.5.
    """
    valores = np.unique(prob)
    if len(valores) < 2 or len(np.unique(y)) < 2:
        return UMBRAL_POR_DEFECTO
    candidatos = (valores[:-1] + valores[1:]) / 2
    puntajes = np.array([balanced_accuracy_score(y, (prob >= u).astype(int)) for u in candidatos])
    mejores = candidatos[np.isclose(puntajes, puntajes.max())]
    return float(mejores[np.argmin(np.abs(mejores - UMBRAL_POR_DEFECTO))])


def _metricas(y: np.ndarray, prob: np.ndarray, umbral: float = UMBRAL_POR_DEFECTO) -> dict[str, float]:
    """Calcula las medidas del modelo y lo compara con la predicción real

    Parámetros:
    - y: si es persona sana 0, de lo contrario si tiene Parkinson es 1
    - prob: probabilidad que el modelo le asignó a cada persona de tener Parkinson
    - umbral: Si la probabilidad lo supera, lo anota como Parkinson, si no, entonces es sano
    """
    pred = (prob >= umbral).astype(int)
    auc = roc_auc_score(y, prob) if len(np.unique(y)) == 2 else np.nan
    return {
        "sensibilidad": recall_score(y, pred, pos_label=1, zero_division=0),
        "especificidad": recall_score(y, pred, pos_label=0, zero_division=0),
        "f1": f1_score(y, pred, pos_label=1, zero_division=0),
        "exactitud_balanceada": balanced_accuracy_score(y, pred),
        "auc": auc,
    }


def evaluar(
    X: pd.DataFrame, y: np.ndarray, grupos: np.ndarray, nombre: str, carpeta_salida: str
) -> tuple[pd.DataFrame, str]:
    """Compara los modelos con validación cruzada externa por persona.

    Reporta métricas por grabación y por persona (midiendo la probabilidad de
    todas las grabaciones de cada persona).
    """
    os.makedirs(carpeta_salida, exist_ok=True)
    externa = StratifiedGroupKFold(n_splits=PARTICIONES_EXTERNAS, shuffle=True, random_state=SEMILLA)
    filas = []
    predicciones = {}

    for nombre_modelo, (clf, rejilla) in modelos().items():
        pred_total = np.zeros(len(y), dtype=int)
        for k, (tr, te) in enumerate(externa.split(X, y, grupos)):
            if set(grupos[tr]) & set(grupos[te]):
                raise RuntimeError("Fuga de información: una persona quedó en entrenamiento y prueba")
            modelo, umbral = _ajustar(clf, rejilla, X.iloc[tr], y[tr], grupos[tr])
            prob = modelo.predict_proba(X.iloc[te])[:, 1]
            pred_total[te] = (prob >= umbral).astype(int)
            base = {"modelo": nombre_modelo, "particion": k + 1, "umbral": umbral}
            filas.append({**base, "nivel": "grabación", **_metricas(y[te], prob, umbral)})
            persona = pd.DataFrame({"g": grupos[te], "y": y[te], "p": prob}).groupby("g").mean()
            y_persona = persona["y"].values.astype(int)
            filas.append({**base, "nivel": "persona", **_metricas(y_persona, persona["p"].values, umbral)})
        predicciones[nombre_modelo] = pred_total
        print(f"  ✓ {nombre_modelo}")

    detalle = pd.DataFrame(filas)
    detalle.to_csv(os.path.join(carpeta_salida, f"{nombre}_detalle_particiones.csv"), index=False)

    cols = ["sensibilidad", "especificidad", "f1", "exactitud_balanceada", "auc"]
    resumen = detalle.groupby(["nivel", "modelo"], sort=False)[cols + ["umbral"]].agg(["mean", "std"])
    resumen.to_csv(os.path.join(carpeta_salida, f"{nombre}_resumen.csv"))

    _tabla_latex(resumen, cols, os.path.join(carpeta_salida, f"{nombre}_tabla.tex"))
    _tabla_markdown(resumen, cols, os.path.join(carpeta_salida, f"{nombre}_tabla.md"))

    por_grabacion = resumen.loc["grabación"]
    mejor = por_grabacion[("exactitud_balanceada", "mean")].drop("Base (clase mayoritaria)").idxmax()
    _matriz_confusion(y, predicciones[mejor], mejor, os.path.join(carpeta_salida, f"{nombre}_confusion.png"))
    return resumen, mejor


def _fmt(media: float, desv: float) -> str:
    """Es para dar formato a la media y la desviación, si no hay un
    número entonces lo coloca como '-'"""
    if np.isnan(media):
        return "--"
    return f"{media:.2f} ± {desv:.2f}"

def _tabla_markdown(resumen: pd.DataFrame, cols: list[str], ruta: str) -> None:
    """Se usa para dar formato en tabla en Markdown con la siguiente estructura:
     Filas: combinación de nivel y modelo
     Columnas: las métricas del modelo
     """
    encabezado = ["Nivel", "Modelo", "Sensibilidad", "Especificidad", "F1", "Exact. balanceada", "AUC"]
    lineas = ["| " + " | ".join(encabezado) + " |", "|" + "---|" * len(encabezado)]
    for (nivel, modelo), fila in resumen.iterrows():
        valores = [_fmt(fila[(c, "mean")], fila[(c, "std")]) for c in cols]
        lineas.append(f"| {nivel} | {modelo} | " + " | ".join(valores) + " |")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")


def _tabla_latex(resumen: pd.DataFrame, cols: list[str], ruta: str) -> None:
    """Se usa para dar formato en tabla en Latex con la siguiente estructura:
     Filas: combinación de nivel y modelo
     Columnas: las métricas del modelo
     """
    lineas = [
        r"\begin{tabular}{|l|c|c|c|c|c|}",
        r"\hline",
        r"\textbf{Modelo} & \textbf{Sensibilidad} & \textbf{Especificidad} & \textbf{F1} & "
        r"\textbf{Exact. balanceada} & \textbf{AUC} \\ \hline",
    ]
    for modelo, fila in resumen.loc["grabación"].iterrows():
        valores = [_fmt(fila[(c, "mean")], fila[(c, "std")]).replace("±", r"$\pm$") for c in cols]
        lineas.append(f"{modelo} & " + " & ".join(valores) + r" \\ \hline")
    lineas.append(r"\end{tabular}")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")


def _matriz_confusion(y: np.ndarray, pred: np.ndarray, nombre_modelo: str, ruta: str) -> None:
    """Guarda una imagen en una matriz 2x2 que cuentas aciertos y errores del modelo donde:
    Filas: persona sana o con Parkinson
    Columnas: lo que el modelo predijo
    """
    cm = confusion_matrix(y, pred, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(4.2, 3.8))
    pantalla = ConfusionMatrixDisplay(cm, display_labels=["Sano", "Parkinson"])
    pantalla.plot(ax=ax, cmap="Greens", colorbar=False)
    ax.set_title(f"{nombre_modelo}\n(predicciones fuera de partición)", fontsize=10)
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Real")
    fig.tight_layout()
    fig.savefig(ruta, dpi=200)
    plt.close(fig)


def entrenar_final(
    X: pd.DataFrame,
    y: np.ndarray,
    grupos: np.ndarray,
    nombre_modelo: str,
    caracteristicas: list[str],
    dataset: str,
    resumen: pd.DataFrame,
    ruta: str,
) -> dict[str, Any]:
    """Entrena el modelo elegido con todos los datos y lo guarda para el prototipo."""
    clf, rejilla = modelos()[nombre_modelo]
    modelo, umbral = _ajustar(clf, rejilla, X, y, grupos)
    metricas = resumen.loc[("grabación", nombre_modelo)]
    paquete = {
        "pipeline": modelo,
        "umbral_decision": umbral,
        "caracteristicas": caracteristicas,
        "modelo": nombre_modelo,
        "dataset": dataset,
        "metricas_validacion": {f"{m}_{e}": float(v) for (m, e), v in metricas.items()},
        "fecha": datetime.now().isoformat(timespec="seconds"),
    }
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    joblib.dump(paquete, ruta)
    with open(ruta.replace(".joblib", ".json"), "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in paquete.items() if k != "pipeline"}, f, ensure_ascii=False, indent=2)
    return paquete
