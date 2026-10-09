"""
Crea el manifiesto (CSV) de las vocales /a/ del Italian Parkinson's Voice and Speech.

Uso:
    python -m entrenamiento.crear_manifiesto_italiano --raiz "datos/italiano" \
        --salida datos/manifiesto_italiano.csv

Supuestos sobre la estructura del dataset (VERIFICAR al descomprimirlo):
  - Tres carpetas de grupo cuyo nombre contiene "Young Healthy", "Elderly Healthy"
    y "Parkinson".
  - Dentro, una carpeta por persona.
  - Los archivos de la vocal /a/ sostenida empiezan por "VA" (p. ej. VA1....wav).
Si la estructura real es distinta, ajusten GRUPOS y PREFIJO_VOCAL_A.

Los controles jóvenes se EXCLUYEN para que el modelo no aprenda a diferenciar
por edad (sección 7 del documento).
"""

import argparse
import os

import pandas as pd

GRUPOS = {"elderly healthy": 0, "parkinson": 1}  # "young healthy" se excluye
PREFIJO_VOCAL_A = "VA"


def etiqueta_de(ruta_relativa):
    texto = ruta_relativa.lower()
    if "young" in texto:
        return None
    for clave, etiqueta in GRUPOS.items():
        if clave in texto:
            return etiqueta
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raiz", required=True)
    p.add_argument("--salida", default="datos/manifiesto_italiano.csv")
    args = p.parse_args()

    filas = []
    for carpeta, _, archivos in os.walk(args.raiz):
        for archivo in archivos:
            if not archivo.lower().endswith(".wav") or not archivo.upper().startswith(PREFIJO_VOCAL_A):
                continue
            relativa = os.path.relpath(os.path.join(carpeta, archivo), args.raiz)
            etiqueta = etiqueta_de(relativa)
            if etiqueta is None:
                continue
            sujeto = os.path.basename(carpeta)
            filas.append({"ruta": os.path.join(carpeta, archivo), "sujeto": sujeto, "etiqueta": etiqueta})

    df = pd.DataFrame(filas).sort_values(["etiqueta", "sujeto", "ruta"])
    os.makedirs(os.path.dirname(args.salida) or ".", exist_ok=True)
    df.to_csv(args.salida, index=False)
    print(
        f"{len(df)} grabaciones de {df['sujeto'].nunique()} personas "
        f"({df.groupby('sujeto')['etiqueta'].first().sum()} con PD) -> {args.salida}"
    )


if __name__ == "__main__":
    main()
