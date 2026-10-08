"""Verifica las reglas del monolito modular: cada capa solo importa de las capas de abajo.

    api  ->  servicios  ->  dominio
                 \\->  infraestructura  ->  dominio

Si alguien rompe una regla (por ejemplo, importa FastAPI en el dominio), esta
prueba falla y la CI bloquea el Pull Request.
"""

import ast
from pathlib import Path

import pytest

PAQUETE = Path(__file__).resolve().parent.parent / "sinapsis"

PROHIBIDOS = {
    "dominio": [
        "fastapi",
        "pydantic",
        "starlette",
        "sinapsis.api",
        "sinapsis.servicios",
        "sinapsis.infraestructura",
    ],
    "infraestructura": ["fastapi", "pydantic", "starlette", "sinapsis.api", "sinapsis.servicios"],
    "servicios": ["fastapi", "pydantic", "starlette", "sinapsis.api"],
}


def importaciones(archivo: Path) -> set[str]:
    arbol = ast.parse(archivo.read_text(encoding="utf-8"))
    nombres = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            nombres.update(a.name for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            nombres.add(nodo.module)
    return nombres


@pytest.mark.parametrize("capa", PROHIBIDOS)
def test_la_capa_no_importa_capas_superiores_ni_el_framework_web(capa):
    violaciones = []
    for archivo in (PAQUETE / capa).glob("*.py"):
        for modulo in importaciones(archivo):
            if any(modulo == p or modulo.startswith(p + ".") for p in PROHIBIDOS[capa]):
                violaciones.append(f"{archivo.name} importa {modulo}")
    assert not violaciones, f"La capa '{capa}' rompe la arquitectura: {violaciones}"
