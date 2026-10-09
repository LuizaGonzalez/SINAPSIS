"""Configuración de la aplicación.

Los valores se pueden cambiar sin tocar el código, usando variables de entorno:
    SINAPSIS_MODELO     dónde está el modelo entrenado (.joblib).
    SINAPSIS_ORIGENES   desde qué direcciones se permite llamar a la API
                        (por defecto, el frontend en http://localhost:5173).
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

# Carpeta backend/, para armar rutas que funcionen sin importar desde dónde se ejecute
RAIZ_BACKEND = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Configuracion:
    """Todos los ajustes del servidor en un solo lugar.

    Atributos:
        ruta_modelo: ubicación del modelo entrenado.
        origenes_cors: direcciones desde las que el navegador puede llamar a la API.
        tamano_maximo_bytes: tamaño máximo del audio que se acepta (10 MB).
        caracteristicas_destacadas: cuántas medidas de voz inusuales se muestran al usuario.
    """

    ruta_modelo: Path = field(
        default_factory=lambda: Path(
            os.environ.get("SINAPSIS_MODELO", RAIZ_BACKEND / "modelos" / "modelo_sinapsis.joblib")
        )
    )
    origenes_cors: list[str] = field(
        default_factory=lambda: os.environ.get("SINAPSIS_ORIGENES", "http://localhost:5173").split(",")
    )
    tamano_maximo_bytes: int = 10 * 1024 * 1024
    caracteristicas_destacadas: int = 3
