#!/usr/bin/env python3
"""
mapper.py - MapReduce Mapper para calcular Ticket Promedio por Tienda
Matrícula: 125055462 (Último dígito 2 -> Ticket promedio por tienda)
"""
import sys

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        # Ignorar encabezado
        if line.startswith("id,") or line.startswith("id\t"):
            continue

        # Procesar con tolerancia a errores (líneas mal formadas)
        try:
            fields = line.split(",")
            if len(fields) < 8:
                continue

            # Campos del CSV:
            # 0: id, 1: fecha_hora, 2: tienda, 3: categoria, 4: producto, 
            # 5: cantidad, 6: precio_unitario, 7: metodo_pago
            tienda = fields[2].strip()
            cantidad = float(fields[5].strip())
            precio_unitario = float(fields[6].strip())
            
            # Validación básica de datos
            if not tienda or cantidad < 0 or precio_unitario < 0:
                continue

            ingreso = cantidad * precio_unitario

            # Emitir clave-valor: tienda \t ingreso \t 1
            # (Se emite el ingreso y un contador de 1 para calcular el promedio en el reducer)
            print(f"{tienda}\t{ingreso:.4f}\t1")

        except (ValueError, IndexError):
            # Línea mal formada o tipos incompatibles: ignorar sin interrumpir el job
            continue

if __name__ == "__main__":
    main()
