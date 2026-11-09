#!/usr/bin/env python3
"""
secuencial.py - Solución secuencial en Python para la comparativa de rendimiento
Matrícula: 125055462 (Ticket promedio por tienda)
"""
import sys
import time
from collections import defaultdict

def procesar_archivo(ruta_csv, ruta_salida=None):
    print(f"Iniciando procesamiento secuencial de: {ruta_csv}")
    inicio = time.perf_counter()

    # Estructura: tienda -> [total_ingreso, conteo]
    acumulado = defaultdict(lambda: [0.0, 0])
    lineas_procesadas = 0
    lineas_invalidas = 0

    with open(ruta_csv, mode="r", encoding="utf-8", errors="replace") as f:
        # Saltar encabezado
        encabezado = f.readline()
        
        for line in f:
            lineas_procesadas += 1
            line = line.strip()
            if not line:
                continue
            
            try:
                parts = line.split(",")
                if len(parts) < 8:
                    lineas_invalidas += 1
                    continue

                tienda = parts[2].strip()
                cantidad = float(parts[5].strip())
                precio_unitario = float(parts[6].strip())

                if not tienda or cantidad < 0 or precio_unitario < 0:
                    lineas_invalidas += 1
                    continue

                ingreso = cantidad * precio_unitario
                acumulado[tienda][0] += ingreso
                acumulado[tienda][1] += 1

            except (ValueError, IndexError):
                lineas_invalidas += 1
                continue

    fin = time.perf_counter()
    duracion = fin - inicio

    resultados = []
    for tienda in sorted(acumulado.keys()):
        total_ingreso, conteo = acumulado[tienda]
        promedio = (total_ingreso / conteo) if conteo > 0 else 0.0
        resultados.append((tienda, promedio))

    # Imprimir resumen
    print("\n--- Resultados (Ticket Promedio por Tienda) ---")
    print(f"{'Tienda':<10} | {'Ticket Promedio':<15}")
    print("-" * 28)
    for tienda, promedio in resultados:
        print(f"{tienda:<10} | ${promedio:.2f}")

    print("\n--- Métricas de Rendimiento Secuencial ---")
    print(f"Líneas procesadas:     {lineas_procesadas:,}")
    print(f"Líneas descartadas:    {lineas_invalidas:,}")
    print(f"Tiendas encontradas:   {len(resultados)}")
    print(f"Tiempo de ejecución:   {duracion:.4f} segundos")

    if ruta_salida:
        with open(ruta_salida, "w", encoding="utf-8") as out:
            for tienda, promedio in resultados:
                out.write(f"{tienda}\t{promedio:.2f}\n")
        print(f"Resultados guardados en: {ruta_salida}")

    return resultados, duracion

if __name__ == "__main__":
    archivo_entrada = sys.argv[1] if len(sys.argv) > 1 else "ventas_125055462.csv"
    archivo_salida = sys.argv[2] if len(sys.argv) > 2 else "resultado_secuencial.txt"
    procesar_archivo(archivo_entrada, archivo_salida)
