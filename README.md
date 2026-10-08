# SINAPSIS

Prototipo académico de tamizaje que estima, a partir de una grabación de la vocal
/a/ sostenida, si la voz presenta patrones asociados a la enfermedad de Parkinson.

**No es un diagnóstico médico.** Proyecto del curso Principios y Tecnologías de IA,
Escuela Colombiana de Ingeniería Julio Garavito (Grupo 06).

## Arquitectura: monolito modular

Cliente-servidor con un frontend en React y un **único backend** en FastAPI,
organizado internamente en capas. Cada capa solo depende de las de abajo:

| Capa | Responsabilidad |
|---|---|
| `api/` | Recibir peticiones HTTP, validar, responder y traducir errores a códigos HTTP |
| `servicios/` | Orquestar el caso de uso "analizar una grabación" |
| `infraestructura/` | Detalles técnicos: leer el WAV, cargar el modelo de disco |
| `dominio/` | Lógica de IA: extracción de características, nivel de riesgo, errores |

Estas reglas se verifican automáticamente en `tests/test_arquitectura.py`: si
alguien las rompe, la prueba falla y la CI bloquea el Pull Request.

Por qué un monolito modular y no microservicios: el sistema tiene una sola
funcionalidad (analizar una grabación) y un equipo de dos personas. Separarlo en
servicios agregaría latencia y complejidad de despliegue sin beneficios, y
aumentaría el riesgo de que la extracción del entrenamiento y la del prototipo
dejaran de ser la misma.

## Estructura

```
sinapsis/
├── backend/
│   ├── sinapsis/                Aplicación (monolito modular)
│   │   ├── main.py              Construye la app y conecta las capas
│   │   ├── config.py            Configuración por variables de entorno
│   │   ├── api/                 rutas.py, esquemas.py, errores.py
│   │   ├── servicios/           analisis.py
│   │   ├── dominio/             caracteristicas.py, riesgo.py, errores.py
│   │   └── infraestructura/     audio.py, repositorio_modelo.py
│   ├── entrenamiento/           Scripts fuera de línea (comparten el dominio)
│   ├── tests/                   Pruebas con voces sintéticas + reglas de arquitectura
│   ├── modelos/                 Aquí queda modelo_sinapsis.joblib tras entrenar
│   ├── pyproject.toml           Configuración de ruff y pytest
│   └── requirements*.txt
├── frontend/
│   └── src/
│       ├── app/                 App.jsx: navegación entre pantallas
│       ├── pantallas/           Inicio, PruebaVoz, Resultado
│       ├── componentes/         Piezas reutilizables (barra, íconos)
│       ├── servicios/           api.js: comunicación con el backend
│       ├── audio/               Grabación con MediaRecorder y conversión a WAV
│       └── estilos/
├── .github/workflows/ci.yml     Integración continua
├── CONTRIBUTING.md              Flujo de trabajo del equipo
└── PLAN_DE_COMMITS.md           Guía para la primera subida entre los dos
```

