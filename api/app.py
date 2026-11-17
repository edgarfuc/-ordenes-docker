
import os
import time
from flask import Flask, request, jsonify
import pyodbc

app = Flask(__name__)

# Configuracion de SQL Server
DB_SERVER = os.getenv("DB_SERVER", "db")
DB_NAME = os.getenv("DB_NAME", "OrdenesDB")
DB_USER = os.getenv("DB_APP_USER", "app_ordenes")
DB_PASSWORD = os.getenv("DB_APP_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")


# Conexion a SQL Server
def get_connection():
    connection_string = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER},1433;"
        f"DATABASE={DB_NAME};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(connection_string, timeout=5)


# Verificar conexion con la base de datos
def connect_with_retry():
    for attempt in range(15):
        try:
            return get_connection()
        except pyodbc.Error:
            if attempt == 14:
                raise
            time.sleep(3)


# Recalcular total de una orden
def update_total(cursor, order_id):
    cursor.execute("""
        UPDATE ordenes
        SET total = (
            SELECT COALESCE(SUM(subtotal), 0)
            FROM orden_detalle
            WHERE orden_id = ?
        )
        WHERE id = ?
    """, order_id, order_id)


# Consultar detalles de una orden
def get_details(cursor, order_id):
    cursor.execute("""
        SELECT id, orden_id, producto, cantidad,
               precio_unitario, subtotal
        FROM orden_detalle
        WHERE orden_id = ?
    """, order_id)

    return [
        {
            "id": row[0],
            "orden_id": row[1],
            "producto": row[2],
            "cantidad": row[3],
            "precio_unitario": float(row[4]),
            "subtotal": float(row[5])
        }
        for row in cursor.fetchall()
    ]


# HEALTH CHECK
@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_connection()
        conn.close()
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Exception as error:
        return jsonify({"status": "error", "message": str(error)}), 503


# LISTAR ORDENES
@app.route("/api/ordenes", methods=["GET"])
def list_orders():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, cliente, fecha, estado, total
            FROM ordenes ORDER BY id
        """)

        orders = [
            {
                "id": r[0],
                "cliente": r[1],
                "fecha": str(r[2]),
                "estado": r[3],
                "total": float(r[4])
            }
            for r in cursor.fetchall()
        ]

        conn.close()
        return jsonify(orders), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


# CONSULTAR UNA ORDEN Y SUS DETALLES
@app.route("/api/ordenes/<int:order_id>", methods=["GET"])
def get_order(order_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, cliente, fecha, estado, total
            FROM ordenes WHERE id = ?
        """, order_id)

        r = cursor.fetchone()

        if not r:
            conn.close()
            return jsonify({"error": "Orden no encontrada"}), 404

        order = {
            "id": r[0],
            "cliente": r[1],
            "fecha": str(r[2]),
            "estado": r[3],
            "total": float(r[4]),
            "detalles": get_details(cursor, order_id)
        }

        conn.close()
        return jsonify(order), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


# CREAR ORDEN
@app.route("/api/ordenes", methods=["POST"])
def create_order():
    data = request.get_json(silent=True) or {}
    cliente = data.get("cliente")

    if not isinstance(cliente, str) or not cliente.strip():
        return jsonify({"error": "El cliente es obligatorio"}), 400

    estado = data.get("estado", "Pendiente")
    total = data.get("total", 0)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
    INSERT INTO ordenes (cliente, estado, total)
    OUTPUT INSERTED.id
    VALUES (?, ?, ?)
""", (cliente.strip(), estado, float(total)))

        order_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        return jsonify({
            "mensaje": "Orden creada correctamente",
            "id": order_id
        }), 201

    except Exception as error:
        return jsonify({"error": str(error)}), 500


# ACTUALIZAR ORDEN
@app.route("/api/ordenes/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    data = request.get_json(silent=True) or {}

    if "cliente" not in data and "estado" not in data:
        return jsonify({"error": "Debe enviar cliente o estado"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM ordenes WHERE id = ?", order_id
        )

        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Orden no encontrada"}), 404

        if "cliente" in data:
            if not isinstance(data["cliente"], str) or not data["cliente"].strip():
                conn.close()
                return jsonify({"error": "Cliente invalido"}), 400

            cursor.execute(
                "UPDATE ordenes SET cliente = ? WHERE id = ?",
                data["cliente"].strip(), order_id
            )

        if "estado" in data:
            cursor.execute(
                "UPDATE ordenes SET estado = ? WHERE id = ?",
                data["estado"], order_id
            )

        conn.commit()
        conn.close()

        return jsonify({"mensaje": "Orden actualizada"}), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


# ELIMINAR ORDEN Y SUS DETALLES
@app.route("/api/ordenes/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM ordenes WHERE id = ?", order_id
        )

        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Orden no encontrada"}), 404

        cursor.execute(
            "DELETE FROM orden_detalle WHERE orden_id = ?", order_id
        )

        cursor.execute(
            "DELETE FROM ordenes WHERE id = ?", order_id
        )

        conn.commit()
        conn.close()

        return jsonify({"mensaje": "Orden eliminada"}), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


# LISTAR DETALLES DE UNA ORDEN
@app.route("/api/ordenes/<int:order_id>/detalles", methods=["GET"])
def list_details(order_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM ordenes WHERE id = ?", order_id
        )

        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Orden no encontrada"}), 404

        details = get_details(cursor, order_id)
        conn.close()

        return jsonify(details), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


# AGREGAR DETALLE A UNA ORDEN
@app.route("/api/ordenes/<int:order_id>/detalles", methods=["POST"])
def add_detail(order_id):
    data = request.get_json(silent=True) or {}

    try:
        product = data.get("producto")
        quantity = data.get("cantidad")
        price = data.get("precio_unitario")

        if not isinstance(product, str) or not product.strip():
            return jsonify({"error": "Producto obligatorio"}), 400

        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"error": "Cantidad invalida"}), 400

        if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
            return jsonify({"error": "Precio invalido"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM ordenes WHERE id = ?", order_id
        )

        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Orden no encontrada"}), 404

        subtotal = quantity * price

        cursor.execute("""
            INSERT INTO orden_detalle
            (orden_id, producto, cantidad, precio_unitario, subtotal)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?)
        """, order_id, product.strip(), quantity, price, subtotal)

        detail_id = cursor.fetchone()[0]
        update_total(cursor, order_id)

        conn.commit()
        conn.close()

        return jsonify({
            "mensaje": "Detalle agregado",
            "id": detail_id,
            "subtotal": subtotal
        }), 201

    except Exception as error:
        return jsonify({"error": str(error)}), 500


# ACTUALIZAR DETALLE
@app.route("/api/detalles/<int:detail_id>", methods=["PUT"])
def update_detail(detail_id):
    data = request.get_json(silent=True) or {}

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT orden_id, producto, cantidad, precio_unitario FROM orden_detalle WHERE id = ?",
            detail_id
        )

        row = cursor.fetchone()

        if not row:
            conn.close()
            return jsonify({"error": "Detalle no encontrado"}), 404

        order_id = row[0]
        product = data.get("producto", row[1])
        quantity = data.get("cantidad", row[2])
        price = data.get("precio_unitario", float(row[3]))

        if not isinstance(product, str) or not product.strip():
            conn.close()
            return jsonify({"error": "Producto invalido"}), 400

        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            conn.close()
            return jsonify({"error": "Cantidad invalida"}), 400

        if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
            conn.close()
            return jsonify({"error": "Precio invalido"}), 400

        subtotal = quantity * price

        cursor.execute("""
            UPDATE orden_detalle
            SET producto = ?, cantidad = ?,
                precio_unitario = ?, subtotal = ?
            WHERE id = ?
        """, product.strip(), quantity, price, subtotal, detail_id)

        update_total(cursor, order_id)

        conn.commit()
        conn.close()

        return jsonify({"mensaje": "Detalle actualizado"}), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500
# 

# ELIMINAR DETALLE
@app.route("/api/detalles/<int:detail_id>", methods=["DELETE"])
def delete_detail(detail_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT orden_id FROM orden_detalle WHERE id = ?",
            detail_id
        )

        row = cursor.fetchone()

        if not row:
            conn.close()
            return jsonify({"error": "Detalle no encontrado"}), 404

        order_id = row[0]

        cursor.execute(
            "DELETE FROM orden_detalle WHERE id = ?",
            detail_id
        )

        update_total(cursor, order_id)

        conn.commit()
        conn.close()

        return jsonify({"mensaje": "Detalle eliminado"}), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    connect_with_retry().close()
    app.run(host="0.0.0.0", port=5000)

