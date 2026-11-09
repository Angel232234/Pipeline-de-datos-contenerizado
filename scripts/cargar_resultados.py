#!/usr/bin/env python3
"""
cargar_resultados.py - Script para leer la salida de MapReduce (part-00000)
e insertar los registros en la base de datos PostgreSQL.
Matrícula: 125055462
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "datamart")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def cargar_datos(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        print(f"Error: El archivo '{ruta_archivo}' no existe.")
        sys.exit(1)

    print(f"Conectando a PostgreSQL en {DB_HOST}:{DB_PORT}/{DB_NAME}...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        sys.exit(1)

    # Asegurar creación de la tabla
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resultados (
            id SERIAL PRIMARY KEY,
            tienda VARCHAR(50) UNIQUE NOT NULL,
            ticket_promedio NUMERIC(10, 2) NOT NULL,
            actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

    print(f"Leyendo archivo de resultados: {ruta_archivo}")
    registros_cargados = 0

    with open(ruta_archivo, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) >= 2:
                tienda = parts[0].strip()
                try:
                    ticket_promedio = float(parts[1].strip())
                except ValueError:
                    print(f"Línea inválida ignorada: {line}")
                    continue

                cur.execute("""
                    INSERT INTO resultados (tienda, ticket_promedio, actualizado_en)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (tienda) 
                    DO UPDATE SET ticket_promedio = EXCLUDED.ticket_promedio, actualizado_en = CURRENT_TIMESTAMP;
                """, (tienda, ticket_promedio))
                registros_cargados += 1

    conn.commit()

    # Verificar datos insertados
    cur.execute("SELECT COUNT(*) FROM resultados;")
    total_en_bd = cur.fetchone()[0]

    print("\n--- Resumen de Carga ---")
    print(f"Registros procesados del archivo: {registros_cargados}")
    print(f"Total de registros en base de datos: {total_en_bd}")

    print("\n--- Primeros registros en la base de datos ---")
    cur.execute("SELECT tienda, ticket_promedio, actualizado_en FROM resultados ORDER BY tienda LIMIT 5;")
    for row in cur.fetchall():
        print(f"Tienda: {row[0]:<6} | Ticket Promedio: ${row[1]:<10} | Fecha: {row[2]}")

    cur.close()
    conn.close()
    print("\nCarga completada exitosamente.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ruta = sys.argv[1]
    else:
        # Rutas por defecto comunes
        posibles_rutas = [
            "/data/output/resultado/part-00000",
            "resultado/part-00000",
            "resultado_secuencial.txt"
        ]
        ruta = None
        for r in posibles_rutas:
            if os.path.exists(r):
                ruta = r
                break
        if not ruta:
            ruta = "/data/output/resultado/part-00000"

    cargar_datos(ruta)
