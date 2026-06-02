import math
import random
import datetime
import numpy as np
from typing import List, Optional



ahora = datetime.datetime.now()
n0 = (ahora.hour * 3600) + (ahora.minute * 60) + ahora.second

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
    u1 = gu();
    u2 = gu();

    if u1 == 0:
        u1 = 1e-10

    z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
    valor = media + desv * z
    
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
    cant_mouses:       int,
    cant_teclados:     int,
    costo_hora:        float, 
    horas_jornada:     int,
    costo_por_unidad:  float, 
    min_empleados:     int,
    max_empleados:     int,
) -> dict:


    cantidad_P      = cant_mouses + cant_teclados
    tipo            = "Mouse"
    tiempo_total    = 0.0
    ingreso_Total   = 0.0
    reciclados = reutilizados = 0
    piezas_recicladas = piezas_reutilizadas = piezas_desechadas = 0
    total_residuo_peligroso = 0.0
    total_reutilizable = 0.0

    i = 0
    while i < cantidad_P:

        u = gu()
        
        if u <= 0.75:

            ingreso, masa_pel, masa_reut = desensamblar(tipo) 
        
            total_residuo_peligroso += masa_pel
            total_reutilizable += masa_reut
            
            
            T = uniforme(5, 10)
            
            reciclados += 1
            
        else:

            reutilizados += 1
            
            if tipo == "Mouse":
               
                T = exponencial_inversa(20)

                ingreso = uniforme(5000, 8000)
            
            else:

                T = uniforme(45,60)
                
                ingreso = uniforme(6000, 12000)

        ingreso_Total += ingreso
        tiempo_total += T
    
        if i + 1 == cant_mouses:
            tipo = "Teclado"
        
        i += 1
   

    
    escenarios = []

    for n in range(min_empleados, max_empleados + 1):
        
        TU = tiempo_total 
        dias = 0
        unidades_restantes = cantidad_P
        CostoAlmacenamiento = 0.0

        while TU > 0:
            dias += 1
            j = 1
            tiempo_trabajado_hoy = 0.0
        

            while j <= n and TU > 0:
                tiempo = normal_distribucion(420.0, 60.0) 
                # Evitamos que el operario trabaje más tiempo del que queda en el lote
                if tiempo > TU:
                    tiempo = TU

                TU = TU - tiempo
                tiempo_trabajado_hoy += tiempo
                j += 1


            # 1. Calculamos la proporción del lote que se terminó hoy
            proporcion_hoy = tiempo_trabajado_hoy / tiempo_total
            unidades_procesadas_hoy = proporcion_hoy * cantidad_P
            
            # 2. Descontamos las unidades procesadas del inventario total
            unidades_restantes -= unidades_procesadas_hoy
            
            # Limpiamos posibles decimales negativos de Python
            unidades_restantes = max(0.0, unidades_restantes)

            # 3. Si el lote no se terminó (TU > 0), las unidades sobrantes pasan la noche
            if TU > 0:
                CostoAlmacenamiento += unidades_restantes * costo_por_unidad

        CostoLaboral = n * dias * horas_jornada * costo_hora
        CostoTot = CostoLaboral + CostoAlmacenamiento
        Rentabilidad = ingreso_Total - CostoTot

        escenarios.append({
            "n_empleados": n,
            "dias_requeridos": dias,
            "costo_laboral": round(CostoLaboral, 2),
            "costo_almacenamiento": round(CostoAlmacenamiento, 2),
            "costo_total": round(CostoTot, 2),
            "rentabilidad": round(Rentabilidad, 2)
        })

    optimo = max(escenarios, key=lambda esc: esc["rentabilidad"])

    return {
        "Datos_Generales": {
            "Total_Perifericos": cantidad_P,
            "Ingreso_Bruto_USD": round(ingreso_Total, 2),
            "Tiempo_Total_Horas": round(tiempo_total / 60, 2),
            "Material_Reutilizable_gr": round(total_reutilizable, 2),
            "Residuo_Peligroso_gr": round(total_residuo_peligroso, 2),
            "Perifericos_Reciclados": reciclados,
            "Perifericos_Reutilizados": reutilizados,
        },
        "Recomendacion_Optima": optimo,
        "Todos_Los_Escenarios": escenarios
    }
