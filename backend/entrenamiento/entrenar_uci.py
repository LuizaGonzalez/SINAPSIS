"""
Experimenta con referencias del dataset Parkinsons de UCI.

Prueba varios modelos para ver qué tan bien distinguen entre personas con
Parkinson y personas sanas, usando las medidas de voz que ya trae el dataset.
Sirve para tener un punto de comparación antes de entrenar con audios reales.

"""

import argparse

import numpy as np
import pandas as pd

from entrenamiento.evaluacion import evaluar
from sinapsis.dominio.caracteristicas import NOMBRES_CARACTERISTICAS

# Columnas del dataset que no son medidas de voz
COLUMNAS_NO_CARACTERISTICAS = ("name", "status", "sujeto")


def leer_argumentos() -> argparse.Namespace:
    """Lee las opciones que se escriben al ejecutar el script.

    Retorna:
        Las dos opciones: dónde está el archivo de datos y en qué
        carpeta se guardan los resultados.
    """
    p = argparse.ArgumentParser(description="Experimento de referencia con el dataset UCI Parkinsons")
    p.add_argument("--datos", default="datos/uci/parkinsons.data", help="Ruta al archivo parkinsons.data")
    p.add_argument("--salida", default="resultados/uci", help="Carpeta donde se guardan los resultados")
    return p.parse_args()


def cargar(ruta: str) -> pd.DataFrame:
    """Lee el archivo de datos y anota a qué persona pertenece cada grabación para que el modelo
    no se entrene con la misma persona.

    Parámetros:
        ruta: ubicación del archivo (parkinsons.data).

    Retorna:
        Una tabla con una fila por grabación (phon_R01_SO1_1) y una columna nueva, "sujeto",
        con el código de la persona (S01).
    """
    df = pd.read_csv(ruta)
    df["sujeto"] = df["name"].str.split("_").str[2]
    return df


def separar_etiquetas_y_grupos(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Saca de la tabla el diagnóstico y la persona de cada grabación.

    Parámetros:
        df: tabla devuelta por la función cargar.

    Retorna:
        - y: el diagnóstico de cada grabación (1 = Parkinson, 0 = sano).
        - grupos: la persona a la que pertenece cada grabación.
    """
    y = df["status"].values.astype(int)
    grupos = df["sujeto"].values
    return y, grupos


def describir_dataset(df: pd.DataFrame, y: np.ndarray) -> str:
    """Resume cuántos datos hay, para ver que hay muchas más personas con Parkinson que sanas.

    Parámetros:
        df: tabla devuelta por la función cargar.
        y: diagnóstico de cada grabación.

    Retorna:
        Un texto con el número de grabaciones, cantidad de personas, cantidad de personas con
        Parkinson y el porcentaje de grabaciones con Parkinson.
    """
    personas_pd = df.groupby("sujeto")["status"].first().sum()
    return (
        f"Grabaciones: {len(df)} | Personas: {df['sujeto'].nunique()} "
        f"| Personas con PD: {personas_pd} "
        f"| Grabaciones PD: {y.sum()} ({y.mean():.0%})"
    )


def conjuntos_de_caracteristicas(df: pd.DataFrame) -> dict[str, list[str]]:
    """Define los dos grupos de medidas de voz que se van a comparar.

    Parámetros:
        df: tabla devuelta por la función cargar.

    Retorna:
        - "todas": todas las medidas del dataset.
        - "praat": solo las que el prototipo puede calcular.
    """
    todas = [c for c in df.columns if c not in COLUMNAS_NO_CARACTERISTICAS]
    return {"todas": todas, "praat": NOMBRES_CARACTERISTICAS}


def evaluar_conjunto(
    df: pd.DataFrame,
    columnas: list[str],
    y: np.ndarray,
    grupos: np.ndarray,
    nombre: str,
    carpeta_salida: str,
) -> tuple[pd.DataFrame, str]:
    """Prueba todos los modelos con un grupo de medidas y muestra los resultados.

    Parámetros:
        df: tabla devuelta por la función cargar.
        columnas: medidas de voz que se usan.
        y: diagnóstico de cada grabación.
        grupos: persona de cada grabación.
        nombre: nombre del grupo ("todas" o "praat"), se usa en los archivos.
        carpeta_salida: carpeta donde se guardan los resultados.

    Retorna:
        - resumen: tabla con los resultados de cada modelo.
        - mejor: nombre del modelo que obtuvo el mejor resultado.
    """
    print(f"\n== Conjunto '{nombre}' ({len(columnas)} características) ==")
    resumen, mejor = evaluar(df[columnas], y, grupos, f"uci_{nombre}", carpeta_salida)
    print(resumen.loc["grabación"][[("exactitud_balanceada", "mean"), ("auc", "mean")]].round(3))
    print(f"Mejor modelo (exactitud balanceada): {mejor}")
    return resumen, mejor


def main() -> None:
    args = leer_argumentos()
    df = cargar(args.datos)
    y, grupos = separar_etiquetas_y_grupos(df)
    print(describir_dataset(df, y))

    for nombre, columnas in conjuntos_de_caracteristicas(df).items():
        evaluar_conjunto(df, columnas, y, grupos, nombre, args.salida)

    print(f"\nResultados guardados en {args.salida}/")


if __name__ == "__main__":
    main()
