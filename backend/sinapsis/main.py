"""Punto de entrada del backend de SINAPSIS (monolito modular).

Resumen de las capas (cada una solo depende de las de abajo):
    api/              HTTP: rutas, esquemas y traducción de errores
    servicios/        casos de uso: orquestan dominio e infraestructura
    dominio/          lógica de IA: características, riesgo y errores
    infraestructura/  detalles técnicos: lectura del audio y carga del modelo
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sinapsis.api.errores import registrar_manejadores
from sinapsis.api.rutas import router
from sinapsis.config import Configuracion
from sinapsis.infraestructura.repositorio_modelo import RepositorioModelo
from sinapsis.servicios.analisis import ServicioAnalisis

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def crear_app(config: Configuracion | None = None, repositorio: RepositorioModelo | None = None) -> FastAPI:
    """Arma la aplicación completa y conecta todas las capas.

    Parámetros:
        config: ajustes del servidor.
        repositorio: un modelo ya cargado. Las pruebas lo usan para no depender
            de un modelo entrenado; si no se pasa, se carga desde el archivo.

    Retorna:
        La aplicación lista para ejecutarse con uvicorn.
    """
    config = config or Configuracion()

    @asynccontextmanager
    async def ciclo_de_vida(app: FastAPI):
        # Se ejecuta una vez al arrancar el servidor
        repo = repositorio or RepositorioModelo.desde_archivo(config.ruta_modelo)
        app.state.repositorio = repo
        app.state.servicio = ServicioAnalisis(
            repo, config.tamano_maximo_bytes, config.caracteristicas_destacadas
        )
        yield

    app = FastAPI(title="SINAPSIS API", version="0.2.0", lifespan=ciclo_de_vida)
    # Permite que el frontend (en otra ruta) llame a la API desde el navegador
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.origenes_cors,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    registrar_manejadores(app)
    app.include_router(router)
    return app


# Aplicación que ejecuta uvicorn
app = crear_app()
