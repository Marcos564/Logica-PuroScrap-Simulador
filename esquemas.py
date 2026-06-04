from typing import List
from pydantic import BaseModel

class EscenarioOut(BaseModel):
    n_empleados:          int
    dias_requeridos:      int
    costo_laboral:        float
    costo_almacenamiento: float
    costo_total:          float
    rentabilidad:         float

class DatosGeneralesOut(BaseModel):
    Total_Perifericos:        int
    Cantidad_Mouses:          int
    Cantidad_Teclados:        int
    
    Ingreso_Bruto_USD:        float
    Tiempo_Total_Horas:       float
    Material_Reutilizable_gr: float
    Residuo_Peligroso_gr:     float

    Cant_Mouses_Reciclados: int
    Cant_Teclados_Reciclados: int
    Cant_Mouses_Reutilizados: int
    Cant_Teclados_Reutilizados: int
    
    Perifericos_Reciclados:   int
    Perifericos_Reutilizados: int

    Lote: int
    Cant_Mouses: int
    Cant_Teclados: int


class SimulacionOut(BaseModel):
    Datos_Generales:      DatosGeneralesOut
    Recomendacion_Optima: EscenarioOut
    Todos_Los_Escenarios: List[EscenarioOut]
