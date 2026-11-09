#!/usr/bin/env python3
"""
reducer.py - MapReduce Reducer para calcular Ticket Promedio por Tienda
Matrícula: 125055462 (Último dígito 2 -> Ticket promedio por tienda)
"""
import sys

def main():
    current_tienda = None
    total_ingreso = 0.0
    total_count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            parts = line.split("\t")
            if len(parts) == 3:
                tienda, ingreso_str, count_str = parts
                ingreso = float(ingreso_str)
                count = int(count_str)
            elif len(parts) == 2:
                tienda, ingreso_str = parts
                ingreso = float(ingreso_str)
                count = 1
            else:
                continue

            if current_tienda == tienda:
                total_ingreso += ingreso
                total_count += count
            else:
                if current_tienda is not None and total_count > 0:
                    ticket_promedio = total_ingreso / total_count
                    print(f"{current_tienda}\t{ticket_promedio:.2f}")

                current_tienda = tienda
                total_ingreso = ingreso
                total_count = count

        except (ValueError, IndexError):
            continue

    # Emitir la última tienda acumulada
    if current_tienda is not None and total_count > 0:
        ticket_promedio = total_ingreso / total_count
        print(f"{current_tienda}\t{ticket_promedio:.2f}")

if __name__ == "__main__":
    main()
