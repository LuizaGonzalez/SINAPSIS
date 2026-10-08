"""
Experimento de referencia con el dataset Parkinsons de UCI (Little et al., 2009).

Uso:
    python -m entrenamiento.entrenar_uci --datos datos/uci/parkinsons.data

Descarga: https://archive.ics.uci.edu/dataset/174/parkinsons (archivo parkinsons.data)

Se evalúan dos conjuntos de características:
  - "todas": las 22 del dataset (incluye RPDE, DFA, D2, PPE, spread1, spread2).
  - "praat": solo las 16 que el prototipo puede calcular con Parselmouth.
La diferencia entre ambos muestra cuánto se pierde al usar solo las
características reproducibles en el prototipo.
"""

import argparse

import pandas as pd

from entrenamiento.evaluacion import evaluar
from sinapsis.dominio.caracteristicas import NOMBRES_CARACTERISTICAS


def cargar(ruta):
    df = pd.read_csv(ruta)
    # name tiene formato "phon_R01_S01_1": el sujeto es "S01"
    df["sujeto"] = df["name"].str.split("_").str[2]
    return df


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--datos", default="datos/uci/parkinsons.data")
    p.add_argument("--salida", default="resultados/uci")
    args = p.parse_args()

    df = cargar(args.datos)
    y = df["status"].values.astype(int)
    grupos = df["sujeto"].values

    print(
        f"Grabaciones: {len(df)} | Personas: {df['sujeto'].nunique()} "
        f"| Personas con PD: {df.groupby('sujeto')['status'].first().sum()} "
        f"| Grabaciones PD: {y.sum()} ({y.mean():.0%})"
    )

    todas = [c for c in df.columns if c not in ("name", "status", "sujeto")]
    conjuntos = {"todas": todas, "praat": NOMBRES_CARACTERISTICAS}

    for nombre, columnas in conjuntos.items():
        print(f"\n== Conjunto '{nombre}' ({len(columnas)} características) ==")
        resumen, mejor = evaluar(df[columnas], y, grupos, f"uci_{nombre}", args.salida)
        print(resumen.loc["grabación"][[("exactitud_balanceada", "mean"), ("auc", "mean")]].round(3))
        print(f"Mejor modelo (exactitud balanceada): {mejor}")

    print(f"\nResultados guardados en {args.salida}/")


if __name__ == "__main__":
    main()
