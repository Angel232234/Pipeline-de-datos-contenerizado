#!/usr/bin/env python3
"""
API REST para exposición y gestión de resultados del pipeline Big Data
Matrícula: 125055462
Dominio: Ticket Promedio por Tienda
"""
import os
import time
from flask import Flask, jsonify, request, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.json.ensure_ascii = False  # Mantiene acentos y ñ correctos en JSON

# Configuración de base de datos desde variables de entorno
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "datamart")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def get_db_connection():
    """Establece conexión con la base de datos PostgreSQL con reintentos."""
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                cursor_factory=RealDictCursor
            )
            return conn
        except psycopg2.OperationalError as e:
            retries -= 1
            if retries == 0:
                raise e
            time.sleep(2)

def init_db():
    """Crea la tabla de resultados si no existe al iniciar la aplicación."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resultados (
                id SERIAL PRIMARY KEY,
                tienda VARCHAR(50) UNIQUE NOT NULL,
                ticket_promedio NUMERIC(10, 2) NOT NULL,
                actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Tabla 'resultados' inicializada correctamente.")
    except Exception as e:
        print(f"Error inicializando tabla en BD: {e}")

# Inicializar esquema
init_db()

@app.route("/", methods=["GET"])
def index():
    """Renderiza la vista gráfica en HTML."""
    return render_template("index.html")

@app.route("/info", methods=["GET"])
def info():
    """Devuelve la información de los endpoints en formato JSON."""
    return jsonify({
        "status": "ok",
        "proyecto": "Examen Segundo Parcial - Pipeline de datos contenerizado",
        "matricula": "125055462",
        "pregunta_negocio": "Ticket promedio (ingreso promedio por registro) por tienda",
        "endpoints": {
            "GET /resultados": "Listar todos los resultados de ticket promedio por tienda",
            "GET /resultados/<tienda>": "Consultar el ticket promedio de una tienda específica",
            "POST /resultados": "Insertar un nuevo registro",
            "PUT /resultados/<tienda>": "Actualizar el ticket promedio de una tienda",
            "DELETE /resultados/<tienda>": "Eliminar el registro de una tienda",
            "GET /health": "Verificar estado y conectividad a base de datos"
        }
    })

@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route("/resultados", methods=["GET"])
def get_resultados():
    """Obtiene todos los registros calculados."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, tienda, ticket_promedio, actualizado_en FROM resultados ORDER BY tienda ASC;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        for r in rows:
            r["ticket_promedio"] = float(r["ticket_promedio"])
            r["actualizado_en"] = r["actualizado_en"].isoformat() if r.get("actualizado_en") else None

        return jsonify({
            "total": len(rows),
            "resultados": rows
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/resultados/<tienda>", methods=["GET"])
def get_resultado_tienda(tienda):
    """Filtra por la clave de negocio asignada: tienda."""
    tienda = tienda.strip().upper()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, tienda, ticket_promedio, actualizado_en FROM resultados WHERE UPPER(tienda) = %s;", (tienda,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return jsonify({"error": f"No se encontró información para la tienda '{tienda}'"}), 404

        row["ticket_promedio"] = float(row["ticket_promedio"])
        row["actualizado_en"] = row["actualizado_en"].isoformat() if row.get("actualizado_en") else None
        return jsonify(row), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/resultados", methods=["POST"])
def create_resultado():
    """Inserta un nuevo registro en la tabla de resultados (CRUD escritura)."""
    data = request.get_json(silent=True) or {}
    tienda = str(data.get("tienda", "")).strip().upper()
    ticket_promedio = data.get("ticket_promedio")

    if not tienda or ticket_promedio is None:
        return jsonify({"error": "Los campos 'tienda' y 'ticket_promedio' son obligatorios."}), 400

    try:
        ticket_val = float(ticket_promedio)
        if ticket_val < 0:
            return jsonify({"error": "'ticket_promedio' debe ser un número positivo."}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO resultados (tienda, ticket_promedio, actualizado_en)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (tienda) 
            DO UPDATE SET ticket_promedio = EXCLUDED.ticket_promedio, actualizado_en = CURRENT_TIMESTAMP
            RETURNING id, tienda, ticket_promedio, actualizado_en;
        """, (tienda, ticket_val))
        nuevo = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        nuevo["ticket_promedio"] = float(nuevo["ticket_promedio"])
        nuevo["actualizado_en"] = nuevo["actualizado_en"].isoformat()
        return jsonify({"mensaje": "Registro guardado exitosamente", "registro": nuevo}), 201

    except ValueError:
        return jsonify({"error": "'ticket_promedio' debe ser numérico."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/resultados/<tienda>", methods=["PUT"])
def update_resultado(tienda):
    """Actualiza el ticket promedio de una tienda existente."""
    tienda = tienda.strip().upper()
    data = request.get_json(silent=True) or {}
    ticket_promedio = data.get("ticket_promedio")

    if ticket_promedio is None:
        return jsonify({"error": "El campo 'ticket_promedio' es requerido."}), 400

    try:
        ticket_val = float(ticket_promedio)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE resultados
            SET ticket_promedio = %s, actualizado_en = CURRENT_TIMESTAMP
            WHERE UPPER(tienda) = %s
            RETURNING id, tienda, ticket_promedio, actualizado_en;
        """, (ticket_val, tienda))
        actualizado = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if not actualizado:
            return jsonify({"error": f"No se encontró la tienda '{tienda}' para actualizar."}), 404

        actualizado["ticket_promedio"] = float(actualizado["ticket_promedio"])
        actualizado["actualizado_en"] = actualizado["actualizado_en"].isoformat()
        return jsonify({"mensaje": "Registro actualizado exitosamente", "registro": actualizado}), 200

    except ValueError:
        return jsonify({"error": "'ticket_promedio' debe ser numérico."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/resultados/<tienda>", methods=["DELETE"])
def delete_resultado(tienda):
    """Elimina el registro de una tienda de la base de datos."""
    tienda = tienda.strip().upper()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM resultados WHERE UPPER(tienda) = %s RETURNING id, tienda;", (tienda,))
        eliminado = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if not eliminado:
            return jsonify({"error": f"No se encontró la tienda '{tienda}' para eliminar."}), 404

        return jsonify({"mensaje": f"Tienda '{tienda}' eliminada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)  