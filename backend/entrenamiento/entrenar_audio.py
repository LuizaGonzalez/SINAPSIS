"""
Entrena el modelo del prototipo a partir de audios crudos de la vocal /a/.

Uso:
    python -m entrenamiento.entrenar_audio --manifiesto datos/manifiesto_italiano.csv \
        --nombre italiano

El manifiesto es un CSV con tres columnas:
    ruta      -> ruta al archivo .wav
    sujeto    -> identificador de la persona (para dividir por persona)
    etiqueta  -> 1 = Parkinson, 0 = control sano

Este script es independiente del dataset: para cambiar a PC-GITA o NeuroVoz solo
hay que generar otro manifiesto con las mismas columnas.

Pasos:
  1. Extrae las características de cada audio con nucleo/caracteristicas.py
     (el MISMO código que usa el backend del prototipo).
  2. Compara los modelos con validación cruzada por persona.
  3. Entrena el mejor modelo con todos los datos y lo guarda en modelos/.
"""

import argparse
import os

import pandas as pd

from entrenamiento.evaluacion import entrenar_final, evaluar
from sinapsis.dominio.caracteristicas import (
    NOMBRES_CARACTERISTICAS,
    extraer_de_archivo,
)
from sinapsis.dominio.errores import AudioInvalidoError


def extraer_todo(manifiesto: pd.DataFrame, cache: str) -> pd.DataFrame:
    if os.path.exists(cache):
        print(f"Usando características en caché: {cache}")
        return pd.read_csv(cache)
    filas, descartadas = [], []
    for i, fila in enumerate(manifiesto.itertuples(index=False), 1):
        try:
            r = extraer_de_archivo(fila.ruta)
            filas.append(
                {
                    "ruta": fila.ruta,
                    "sujeto": fila.sujeto,
                    "etiqueta": fila.etiqueta,
                    "duracion_s": r.duracion_s,
                    **r.caracteristicas,
                }
            )
        except AudioInvalidoError as e:
            descartadas.append((fila.ruta, e.codigo))
        if i % 25 == 0:
            print(f"  {i}/{len(manifiesto)} audios procesados")
    if descartadas:
        print(f"  {len(descartadas)} audios descartados por la validación:")
        for ruta, codigo in descartadas[:10]:
            print(f"    - {os.path.basename(ruta)} ({codigo})")
    df = pd.DataFrame(filas)
    os.makedirs(os.path.dirname(cache) or ".", exist_ok=True)
    df.to_csv(cache, index=False)
    return df


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifiesto", required=True)
    p.add_argument("--nombre", default="audio", help="nombre corto del dataset, para los archivos de salida")
    p.add_argument("--salida", default="resultados")
    p.add_argument("--modelo", default="modelos/modelo_sinapsis.joblib")
    args = p.parse_args()

    manifiesto = pd.read_csv(args.manifiesto)
    df = extraer_todo(manifiesto, os.path.join("datos", f"caracteristicas_{args.nombre}.csv"))

    X = df[NOMBRES_CARACTERISTICAS]
    y = df["etiqueta"].values.astype(int)
    grupos = df["sujeto"].astype(str).values
    print(
        f"Grabaciones: {len(df)} | Personas: {len(set(grupos))} "
        f"| Personas con PD: {df.groupby('sujeto')['etiqueta'].first().sum()}"
    )

    carpeta = os.path.join(args.salida, args.nombre)
    resumen, mejor = evaluar(X, y, grupos, args.nombre, carpeta)
    print(resumen.loc["grabación"][[("exactitud_balanceada", "mean"), ("auc", "mean")]].round(3))
    print(f"Mejor modelo: {mejor}")

    paquete = entrenar_final(X, y, grupos, mejor, NOMBRES_CARACTERISTICAS, args.nombre, resumen, args.modelo)
    print(f"Modelo final ({paquete['modelo']}) guardado en {args.modelo}")


if __name__ == "__main__":
    main()
