"""Accede al modelo entrenado guardado en disco.
"""

import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class RepositorioModelo:
    """Guarda el modelo entrenado y responde las preguntas que la aplicación le hace."""

    def __init__(self, paquete: dict[str, Any] | None = None):
        """Crea el repositorio a partir de un modelo ya cargado.

        Parámetros:
            paquete: el modelo con su información (nombre, dataset, fecha y
                medidas de voz que usa). Si es None, no hay modelo disponible.
        """
        self._paquete = paquete

    @classmethod
    def desde_archivo(cls, ruta: Path) -> "RepositorioModelo":
        """Carga el modelo desde el archivo .joblib que genera el entrenamiento.

        Si el archivo no existe, la aplicación arranca igual, pero sin poder
        analizar grabaciones hasta que se entrene el modelo.

        Parámetros:
            ruta: ubicación del archivo del modelo.

        Retorna:
            Un repositorio con el modelo cargado, o vacío si no se encontró el archivo.
        """
        if not ruta.exists():
            logger.warning("No se encontró el modelo en %s. El análisis no estará disponible.", ruta)
            return cls(None)
        paquete = joblib.load(ruta)
        logger.info("Modelo cargado: %s (dataset: %s)", paquete["modelo"], paquete["dataset"])
        return cls(paquete)

    @property
    def disponible(self) -> bool:
        """Indica si hay un modelo cargado.

        Retorna:
            True si se puede analizar una grabación, False si no hay modelo.
        """
        return self._paquete is not None

    @property
    def metadatos(self) -> dict[str, str | None]:
        """Información básica del modelo, para mostrarla en la API.

        Retorna:
            El nombre del modelo, el dataset con el que se entrenó y la fecha.
            Si no hay modelo, los tres valores son None.
        """
        if not self._paquete:
            return {"modelo": None, "dataset": None, "fecha": None}
        return {k: self._paquete[k] for k in ("modelo", "dataset", "fecha")}

    @property
    def caracteristicas(self) -> list[str]:
        """Nombres de las medidas de voz que el modelo necesita, en el orden en que las usa."""
        return self._paquete["caracteristicas"]

    def _como_tabla(self, caracteristicas: dict[str, float]) -> pd.DataFrame:
        """Pone las medidas de una grabación en una tabla de una fila, en el orden del modelo."""
        return pd.DataFrame([caracteristicas])[self.caracteristicas]

    def probabilidad_parkinson(self, caracteristicas: dict[str, float]) -> float:
        """Calcula la probabilidad de que la voz presente patrones de Parkinson.

        Parámetros:
            caracteristicas: medidas de voz de la grabación (nombre -> valor).

        Retorna:
            Un número entre 0 y 1. Cuanto más cerca de 1, más se parece la voz
            a las de personas con Parkinson del entrenamiento.
        """
        return float(self._paquete["pipeline"].predict_proba(self._como_tabla(caracteristicas))[0, 1])

    def desviaciones(self, caracteristicas: dict[str, float]) -> dict[str, float]:
        """Mide qué tan lejos está cada valor del promedio de las voces de entrenamiento.

        Sirve para mostrarle al usuario qué medidas de su voz son más inusuales.
        No indica cuáles pesaron más en la decisión del modelo.

        Parámetros:
            caracteristicas: medidas de voz de la grabación (nombre -> valor).

        Retorna:
            Para cada medida, cuántas desviaciones estándar está por encima
            (positivo) o por debajo (negativo) del promedio.
        """
        escalador = self._paquete["pipeline"].named_steps["escalar"]
        fila = self._como_tabla(caracteristicas).to_numpy()[0]
        z = (fila - escalador.mean_) / escalador.scale_
        return dict(zip(self.caracteristicas, np.round(z.astype(float), 2), strict=True))
