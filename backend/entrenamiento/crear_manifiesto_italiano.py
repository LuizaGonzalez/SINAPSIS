"""
Crea el manifiesto (CSV) de las vocales /a/ del dataset italiano de Parkinson.

Se usan los controles mayores y las personas con Parkinson. Los controles jóvenes
se excluyen para que el modelo no aprenda a distinguir por edad.
"""

import argparse
import os

import pandas as pd

# Palabra que identifica cada grupo en el nombre de su carpeta -> etiqueta.
# Los controles jóvenes ("young healthy") no están en la lista: se excluyen.
GRUPOS = {"elderly healthy": 0, "parkinson": 1}
PREFIJO_VOCAL_A = "VA"


def leer_argumentos() -> argparse.Namespace:
    """
    Lee las opciones escritas en la terminal.

    Retorna: un objeto con la carpeta del dataset y el archivo CSV de salida.
    """
    parser = argparse.ArgumentParser(
        description="Crea el manifiesto de las vocales /a/ del dataset italiano."
    )
    parser.add_argument("--raiz", required=True, help="Carpeta donde está el dataset descomprimido")
    parser.add_argument(
        "--salida", default="datos/manifiesto_italiano.csv", help="Archivo CSV que se va a crear"
    )
    return parser.parse_args()


def etiqueta_de(ruta_relativa: str) -> int | None:
    """
    Decide la etiqueta de un audio a partir de su ruta dentro del dataset.

    Parámetros:
        ruta_relativa: ruta del audio respecto a la carpeta principal del dataset.

    Retorna: 1 si es de una persona con Parkinson, 0 si es un control sano mayor,
    o None si el audio no se debe usar.
    """
    texto = ruta_relativa.lower()
    if "young" in texto:
        return None
    for clave, etiqueta in GRUPOS.items():
        if clave in texto:
            return etiqueta
    return None


def es_vocal_a(nombre_archivo: str) -> bool:
    """
    Indica si un archivo es un audio de la vocal /a/ sostenida.

    Parámetros:
        nombre_archivo: nombre del archivo.

    Retorna: True si es un .wav cuyo nombre empieza por "VA".
    """
    return nombre_archivo.lower().endswith(".wav") and nombre_archivo.upper().startswith(PREFIJO_VOCAL_A)


def buscar_audios(raiz: str) -> list[dict]:
    """
    Recorre el dataset y reúne los audios de la vocal /a/ que se van a usar.

    El identificador de cada persona es la ruta de su carpeta dentro del dataset,
    así dos personas con el mismo nombre en subcarpetas distintas no se confunden.

    Parámetros:
        raiz: carpeta principal del dataset.

    Retorna: lista de filas, cada una con las claves ruta, sujeto y etiqueta.
    """
    filas = []
    for carpeta, _, archivos in os.walk(raiz):
        for archivo in archivos:
            if not es_vocal_a(archivo):
                continue
            ruta = os.path.join(carpeta, archivo)
            etiqueta = etiqueta_de(os.path.relpath(ruta, raiz))
            if etiqueta is None:
                continue
            filas.append({"ruta": ruta, "sujeto": os.path.relpath(carpeta, raiz), "etiqueta": etiqueta})
    return filas


def armar_manifiesto(filas: list[dict]) -> pd.DataFrame:
    """
    Convierte las filas en una tabla ordenada por etiqueta, persona y ruta.

    Parámetros:
        filas: la lista que entrega la función buscar_audios.

    Retorna: la tabla del manifiesto (columnas ruta, sujeto y etiqueta).
    """
    return pd.DataFrame(filas).sort_values(["etiqueta", "sujeto", "ruta"])


def guardar(manifiesto: pd.DataFrame, salida: str) -> None:
    """
    Guarda el manifiesto como archivo CSV, creando la carpeta si no existe.

    Parámetros:
        manifiesto: la tabla del manifiesto.
        salida: ruta del archivo CSV que se crea.
    """
    os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
    manifiesto.to_csv(salida, index=False)


def resumir(manifiesto: pd.DataFrame, salida: str) -> None:
    """
    Muestra en pantalla cuántas grabaciones y personas quedaron en el manifiesto.

    Parámetros:
        manifiesto: la tabla del manifiesto.
        salida: ruta del archivo CSV donde se guardó.
    """
    con_parkinson = manifiesto.groupby("sujeto")["etiqueta"].first().sum()
    print(
        f"{len(manifiesto)} grabaciones de {manifiesto['sujeto'].nunique()} personas "
        f"({con_parkinson} con PD) -> {salida}"
    )


def main() -> None:
    """Punto de entrada: busca los audios, arma el manifiesto, lo guarda y muestra el resumen."""
    args = leer_argumentos()
    manifiesto = armar_manifiesto(buscar_audios(args.raiz))
    guardar(manifiesto, args.salida)
    resumir(manifiesto, args.salida)


if __name__ == "__main__":
    main()
