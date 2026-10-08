"""
Evaluación de modelos con validación cruzada POR PERSONA.

Todas las grabaciones de una misma persona quedan siempre en la misma partición
(StratifiedGroupKFold). La estandarización y la búsqueda de hiperparámetros se
hacen DENTRO de cada partición de entrenamiento, para evitar fuga de información
(Kumar et al., 2026; sección 2.4 del documento).
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
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

SEMILLA = 42
PARTICIONES_EXTERNAS = 5
PARTICIONES_INTERNAS = 3
UMBRAL_DECISION = 0.5


def modelos() -> dict[str, tuple[Any, dict[str, list]]]:
    """Modelos a comparar y su rejilla de hiperparámetros (búsqueda interna)."""
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
            SVC(kernel="rbf", probability=True, class_weight="balanced", random_state=SEMILLA),
            {"clf__C": [0.1, 1, 10, 100], "clf__gamma": ["scale", 0.01, 0.1]},
        ),
        "MLP": (
            MLPClassifier(max_iter=2000, early_stopping=False, random_state=SEMILLA),
            {"clf__hidden_layer_sizes": [(16,), (32,), (16, 8)], "clf__alpha": [1e-3, 1e-2, 1e-1]},
        ),
    }


def _pipeline(clf) -> Pipeline:
    return Pipeline([("escalar", StandardScaler()), ("clf", clf)])


def _ajustar(clf, rejilla: dict, X: pd.DataFrame, y: np.ndarray, grupos: np.ndarray) -> Pipeline:
    """Ajusta el modelo; si tiene hiperparámetros, los busca con CV interna por persona."""
    pipe = _pipeline(clone(clf))
    if not rejilla:
        return pipe.fit(X, y)
    interna = StratifiedGroupKFold(n_splits=PARTICIONES_INTERNAS, shuffle=True, random_state=SEMILLA)
    busqueda = GridSearchCV(pipe, rejilla, cv=interna, scoring="balanced_accuracy", n_jobs=-1)
    busqueda.fit(X, y, groups=grupos)
    return busqueda.best_estimator_


def _metricas(y: np.ndarray, prob: np.ndarray, umbral: float = UMBRAL_DECISION) -> dict[str, float]:
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

    Reporta métricas por grabación y por persona (promediando la probabilidad de
    todas las grabaciones de cada persona, que es como se usaría en tamizaje).
    """
    os.makedirs(carpeta_salida, exist_ok=True)
    externa = StratifiedGroupKFold(n_splits=PARTICIONES_EXTERNAS, shuffle=True, random_state=SEMILLA)
    filas = []
    predicciones = {}

    for nombre_modelo, (clf, rejilla) in modelos().items():
        prob_total = np.zeros(len(y))
        for k, (tr, te) in enumerate(externa.split(X, y, grupos)):
            if set(grupos[tr]) & set(grupos[te]):
                raise RuntimeError("Fuga de información: una persona quedó en entrenamiento y prueba")
            modelo = _ajustar(clf, rejilla, X.iloc[tr], y[tr], grupos[tr])
            prob = modelo.predict_proba(X.iloc[te])[:, 1]
            prob_total[te] = prob
            filas.append(
                {"modelo": nombre_modelo, "particion": k + 1, "nivel": "grabación", **_metricas(y[te], prob)}
            )
            df_te = pd.DataFrame({"g": grupos[te], "y": y[te], "p": prob}).groupby("g").mean()
            filas.append(
                {
                    "modelo": nombre_modelo,
                    "particion": k + 1,
                    "nivel": "persona",
                    **_metricas(df_te["y"].values.astype(int), df_te["p"].values),
                }
            )
        predicciones[nombre_modelo] = prob_total
        print(f"  ✓ {nombre_modelo}")

    detalle = pd.DataFrame(filas)
    detalle.to_csv(os.path.join(carpeta_salida, f"{nombre}_detalle_particiones.csv"), index=False)

    cols = ["sensibilidad", "especificidad", "f1", "exactitud_balanceada", "auc"]
    resumen = detalle.groupby(["nivel", "modelo"], sort=False)[cols].agg(["mean", "std"])
    resumen.to_csv(os.path.join(carpeta_salida, f"{nombre}_resumen.csv"))

    _tabla_latex(resumen, cols, os.path.join(carpeta_salida, f"{nombre}_tabla.tex"))
    _tabla_markdown(resumen, cols, os.path.join(carpeta_salida, f"{nombre}_tabla.md"))

    por_grabacion = resumen.loc["grabación"]
    mejor = por_grabacion[("exactitud_balanceada", "mean")].drop("Base (clase mayoritaria)").idxmax()
    _matriz_confusion(y, predicciones[mejor], mejor, os.path.join(carpeta_salida, f"{nombre}_confusion.png"))
    return resumen, mejor


def _fmt(media: float, desv: float) -> str:
    if np.isnan(media):
        return "--"
    return f"{media:.2f} ± {desv:.2f}"


def _tabla_markdown(resumen: pd.DataFrame, cols: list[str], ruta: str) -> None:
    encabezado = ["Nivel", "Modelo", "Sensibilidad", "Especificidad", "F1", "Exact. balanceada", "AUC"]
    lineas = ["| " + " | ".join(encabezado) + " |", "|" + "---|" * len(encabezado)]
    for (nivel, modelo), fila in resumen.iterrows():
        valores = [_fmt(fila[(c, "mean")], fila[(c, "std")]) for c in cols]
        lineas.append(f"| {nivel} | {modelo} | " + " | ".join(valores) + " |")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")


def _tabla_latex(resumen: pd.DataFrame, cols: list[str], ruta: str) -> None:
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


def _matriz_confusion(y: np.ndarray, prob: np.ndarray, nombre_modelo: str, ruta: str) -> None:
    pred = (prob >= UMBRAL_DECISION).astype(int)
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
    """Entrena el modelo elegido con TODOS los datos y lo guarda para el prototipo."""
    clf, rejilla = modelos()[nombre_modelo]
    modelo = _ajustar(clf, rejilla, X, y, grupos)
    metricas = resumen.loc[("grabación", nombre_modelo)]
    paquete = {
        "pipeline": modelo,
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
