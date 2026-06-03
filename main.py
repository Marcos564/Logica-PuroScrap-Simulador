import uvicorn
from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from esquemas import SimulacionOut
from simulador import ejecutar_simulacion

app = FastAPI(
    title       = "PuroScrap API",
    description = "Simulación Montecarlo de planta de reciclaje electrónico.",
    version     = "1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite que cualquier frontend se conecte
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, etc.
    allow_headers=["*"],
)

@app.get("/health", summary="Estado de la API")
def health():
    return {"status": "ok", "service": "PuroScrap API v1.0.0"}

@app.get(
    "/simular",
    response_model = SimulacionOut,
    summary        = "Ejecutar simulación Montecarlo",
    description    = """
Simula el proceso de desensamble y reciclaje de periféricos electrónicos
y devuelve la tabla comparativa de rentabilidad por número de empleados.

**Parámetros requeridos:** `cant_mouses`, `cant_teclados`

**Parámetros opcionales con defaults razonables:**
- `min_empleados` / `max_empleados`: rango a evaluar (default 1–10)
- `costo_hora`: $/hora-hombre (default 4500)
- `costo_por_unidad`: costo de almacenamiento por unidad/día (default 0.50)
- `horas_jornada`: horas por jornada (default 8)
    """,
)
def simular(
    min_lote: int = Query(
        ..., ge=1, le=10_000,
        description="Cantidad de mouses a procesar (requerido, 1–10000)"
    ),
    max_lote: int = Query(
        ..., ge=1, le=10_000,
        description="Cantidad de teclados a procesar (requerido, 1–10000)"
    ),
    min_empleados: int = Query(
        1, ge=1, le=100,
        description="Mínimo de empleados a evaluar (default=1)"
    ),
    max_empleados: int = Query(
        10, ge=1, le=100,
        description="Máximo de empleados a evaluar (default=10)"
    ),
    costo_hora: float = Query(
        4_500, ge=1,
        description="Costo por hora-hombre en $ (default=4500)"
    ),
    costo_por_unidad: float = Query( # <--- CAMBIO AQUÍ
        0.50, ge=0,
        description="Costo de almacenamiento por unidad al día en $ (default=0.50)"
    ),
    horas_jornada: int = Query(
        8, ge=1, le=24,
        description="Horas de trabajo por jornada (default=8)"
    ),
):

    if min_empleados > max_empleados:
        raise HTTPException(
            status_code=422,
            detail="min_empleados no puede ser mayor que max_empleados."
        )

    # Llamada al simulador con el nuevo nombre de parámetro
    resultado = ejecutar_simulacion(
        min_lote     = min_lote,
        max_lote         = max_lote,
        costo_hora       = costo_hora,
        horas_jornada    = horas_jornada,
        costo_por_unidad = costo_por_unidad, 
        min_empleados    = min_empleados,
        max_empleados    = max_empleados,
    )

    return resultado 


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
