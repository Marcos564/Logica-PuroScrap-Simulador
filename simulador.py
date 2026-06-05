import math
import datetime
import numpy as np
from typing import List, Optional


ahora = datetime.datetime.now()
n0 = (ahora.hour * 3600 * 1000000) + (ahora.minute * 60 * 1000000) + (ahora.second * 1000000) + ahora.microsecond
n0 = n0 % (2**32)

def gu() -> float:
    global n0  # Le dice a la función que use y actualice el 'n0' de arriba
    
    a = 1664525
    c = 1013904223
    m = 2**32
    digitos = 5
    
    n0 = (a * n0 + c) % m
    
    return round(n0 / m, digitos)


def exponencial_inversa(media: float = 7.0) -> float:
    u = max(gu(), 1e-10)
    return -media * math.log(u)

def normal_distribucion(media: float, desv: float = 1.6) -> float:
    
    suma = 0

    for i in range (1,13):
        u = gu();
        suma = suma + u    
        
    valor = desv * (suma - 6) + media
    
    return max(0.0, valor)

def uniforme(minimo: float = 15.0, maximo: float = 30.0) -> float:
    return minimo + (maximo - minimo) * gu()


def desensamblar(tipo: str):
    
    if tipo == "Mouse":
        peso_total = normal_distribucion(100.0, 10.0)
        masa_reciclable = peso_total * 0.72
        masa_reutilizable = peso_total * 0.25
        masa_peligrosa = peso_total * 0.03
        
        cobre_extr = normal_distribucion(10.0, 1.8)
        hierro_extr = normal_distribucion(7.0, 1.8)
        
    else: 
        peso_total = normal_distribucion(800.0, 50.0)
        masa_reciclable = peso_total * 0.72
        masa_reutilizable = peso_total * 0.25
        masa_peligrosa = peso_total * 0.03
        
        cobre_extr = normal_distribucion(15.0, 3.0) 
        hierro_extr = normal_distribucion(50.0, 15.0)

    ingreso = (cobre_extr * 13.7) + (hierro_extr * 0.50)
    
    return ingreso, masa_peligrosa, masa_reutilizable

def ejecutar_simulacion(
    min_lote:       int,
    max_lote:     int,
    costo_hora:        float, 
    horas_jornada:     int,
    costo_por_unidad:  float, 
    min_empleados:     int,
    max_empleados:     int,
) -> dict:

     # ── 1. Generación del lote ─────────────────────────

    lote = round(uniforme(min_lote, max_lote))

    cant_mouses = 0
    cant_teclados = 0

    for _ in range(lote):

        if gu() <= 0.60:
            cant_teclados += 1
        else:
            cant_mouses += 1

    # ── 2. Acumuladores ────────────────────────────────

    tiempo_total = 0.0
    ingreso_total = 0.0

    reciclados = 0
    reutilizados = 0
    Cant_Mouses_Reutilizados = 0
    Cant_Teclados_Reutilizados = 0
    Cant_Teclados_Reciclados = 0
    Cant_Mouses_Reciclados = 0

    total_residuo_peligroso = 0.0
    total_reutilizable = 0.0


     # ── 3. Procesamiento de mouses ─────────────────────

    for _ in range(cant_mouses):

        u = gu()

        # 75% reciclaje
        if u <= 0.75:
            Cant_Mouses_Reciclados += 1

            ingreso, masa_pel, masa_reut = desensamblar("Mouse")

            total_residuo_peligroso += masa_pel
            total_reutilizable += masa_reut

            T = uniforme(5, 10)

            reciclados += 1

        # 25% reutilización
        else:

            Cant_Mouses_Reutilizados += 1

            T = exponencial_inversa(20)

            ingreso = uniforme(5000, 8000)

        ingreso_total += ingreso
        tiempo_total += T

 # ── 4. Procesamiento de teclados ───────────────────

    for _ in range(cant_teclados):

        u = gu()

        # 75% reciclaje
        if u <= 0.75:

            ingreso, masa_pel, masa_reut = desensamblar("Teclado")

            total_residuo_peligroso += masa_pel
            total_reutilizable += masa_reut

            T = uniforme(10, 20)

            Cant_Teclados_Reciclados += 1

        # 25% reutilización
        else:

            Cant_Teclados_Reutilizados += 1

            T = uniforme(45, 60)

            ingreso = uniforme(6000, 12000)

        ingreso_total += ingreso
        tiempo_total += T

    # ── 5. Evaluación de escenarios ────────────────────

    escenarios = []

    for n in range(min_empleados, max_empleados + 1):

        TU = tiempo_total
        dias = 0
        unidades_restantes = lote
        costo_almacenamiento = 0.0
        tiempo_laboral_real = 0.0

        while TU > 0:

            dias += 1
            j = 1
            tiempo_trabajado_hoy = 0.0

            while j <= n and TU > 0:

                tiempo = normal_distribucion(420.0, 60.0)

                horas_pagadas_totales += (tiempo_disponible / 60.0)
                
                if tiempo > TU:
                    tiempo = TU

                TU -= tiempo
                tiempo_trabajado_hoy += tiempo

                j += 1

            tiempo_laboral_real += tiempo_trabajado_hoy/ tiempo_total
            proporcion_hoy = tiempo_trabajado_hoy / tiempo_total
            unidades_procesadas_hoy = proporcion_hoy * lote

            unidades_restantes -= unidades_procesadas_hoy
            unidades_restantes = max(0.0, unidades_restantes)

            if TU > 0:
                costo_almacenamiento += (
                    unidades_restantes * costo_por_unidad
                )

        #costo_laboral = (tiempo_laboral_real / 60) * costo_hora
        costo_laboral = horas_pagadas_totales * costo_hora

        costo_total = (
            costo_laboral +
            costo_almacenamiento
        )

        rentabilidad = ingreso_total - costo_total

        escenarios.append({
            "n_empleados": n,
            "dias_requeridos": dias,
            "costo_laboral": round(costo_laboral, 2),
            "costo_almacenamiento": round(costo_almacenamiento, 2),
            "costo_total": round(costo_total, 2),
            "rentabilidad": round(rentabilidad, 2)
        })

    # ── 6. Escenario óptimo ────────────────────────────

    optimo = max(
        escenarios,
        key=lambda esc: esc["rentabilidad"]
    )

    # ── 7. Resultado ───────────────────────────────────

    return {
        "Datos_Generales": {
            "Total_Perifericos": lote,
            "Cantidad_Mouses": cant_mouses,
            "Cantidad_Teclados": cant_teclados,
            "Ingreso_Bruto_USD": round(ingreso_total, 2),
            "Tiempo_Total_Horas": round(tiempo_total / 60, 2),
            "Material_Reutilizable_gr": round(total_reutilizable, 2),
            "Residuo_Peligroso_gr": round(total_residuo_peligroso, 2),
            "Cant_Mouses_Reciclados": Cant_Mouses_Reciclados,
            "Cant_Teclados_Reciclados": Cant_Teclados_Reciclados,
            "Cant_Mouses_Reutilizados": Cant_Mouses_Reutilizados,
            "Cant_Teclados_Reutilizados": Cant_Teclados_Reutilizados,
            "Perifericos_Reutilizados": Cant_Mouses_Reutilizados + Cant_Teclados_Reutilizados,
            "Perifericos_Reciclados": Cant_Mouses_Reciclados + Cant_Teclados_Reciclados,
            "Lote": lote,
            "Cant_Teclados": cant_teclados,
            "Cant_Mouses": cant_mouses
        },
        "Recomendacion_Optima": optimo,
        "Todos_Los_Escenarios": escenarios
    }
   

    
   
