import sqlite3
from utils.db_connection import get_db_connection
from utils.db_connection import get_db_connection

def crear_orden_compra(datos):
    print("✔ crear_orden_compra ejecutada con datos:", datos)  # ← Añadido para verificación

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Validar que el ID de propuesta exista
        cursor.execute("SELECT id FROM propuestas WHERE id = ?", (datos['id_propuesta'],))
        propuesta = cursor.fetchone()
        if not propuesta:
            return {"ok": False, "error": "ID de propuesta no existe."}

        # Validar monto > 0 y que sea numérico
        try:
            monto = float(datos['monto_oc'])
            if monto <= 0:
                return {"ok": False, "error": "El monto debe ser mayor a 0."}
        except ValueError:
            return {"ok": False, "error": "El monto debe ser un número válido."}

        # Validar moneda
        if datos['moneda'] not in ['S/', 'US$']:
            return {"ok": False, "error": "Moneda inválida. Debe ser 'S/' o 'US$'."}

        # Validar consistencia de moneda para las OC previas de esa propuesta
        cursor.execute("SELECT DISTINCT moneda FROM ordenes_compra WHERE id_propuesta = ?", (datos['id_propuesta'],))
        monedas_existentes = [row['moneda'] for row in cursor.fetchall()]
        if monedas_existentes and datos['moneda'] not in monedas_existentes:
            return {"ok": False, "error": "Todas las OC de esta propuesta deben tener la misma moneda."}

        # Insertar OC
        cursor.execute("""
            INSERT INTO ordenes_compra (id_propuesta, nro_oc, fecha_oc, monto_oc, pm_asignado, moneda)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datos['id_propuesta'],
            datos['nro_oc'],
            datos['fecha_oc'],
            monto,
            datos['pm_asignado'],
            datos['moneda']
        ))

        conn.commit()
        return {"ok": True}

    except Exception as e:
        return {"ok": False, "error": f"Error al crear OC: {str(e)}"}
    finally:
        conn.close()

def obtener_todo_facturacion():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener todas las OC
    cursor.execute("SELECT * FROM ordenes_compra")
    ordenes = cursor.fetchall()

    # Obtener todas las facturas
    cursor.execute("SELECT * FROM facturas")
    facturas = cursor.fetchall()

    conn.close()
    return ordenes, facturas

def obtener_propuestas_booking():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, cliente, cliente_final, nombre_oportunidad
        FROM propuestas
        WHERE status = 'Booking'
        ORDER BY fecha_actualizacion DESC
    """)

    propuestas = cursor.fetchall()

    conn.close()
    return propuestas

def crear_factura(datos):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Validar que la OC exista
        cursor.execute("SELECT * FROM ordenes_compra WHERE id_oc = ?", (datos['id_oc'],))
        oc = cursor.fetchone()
        if not oc:
            return {"ok": False, "error": "Orden de Compra no existe"}

        # Validar monto > 0
        try:
            monto = float(datos['monto_factura'])
            if monto <= 0:
                return {"ok": False, "error": "El monto debe ser mayor a 0"}
        except ValueError:
            return {"ok": False, "error": "Monto inválido"}

        # Validar no duplicidad de factura en esa OC
        cursor.execute("SELECT * FROM facturas WHERE id_oc = ? AND nro_factura = ?", (datos['id_oc'], datos['nro_factura']))
        if cursor.fetchone():
            return {"ok": False, "error": "Ya existe una factura con ese número para esta OC"}

        # Insertar
        cursor.execute("""
            INSERT INTO facturas (id_oc, nro_factura, monto_factura, fecha_factura)
            VALUES (?, ?, ?, ?)
        """, (
            datos['id_oc'],
            datos['nro_factura'],
            monto,
            datos['fecha_factura']
        ))
        conn.commit()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()

def obtener_todas_oc():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ordenes_compra")
    ordenes = cursor.fetchall()
    conn.close()
    return ordenes

def obtener_resumen_facturacion():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            p.id AS id_propuesta,
            p.cliente,
            p.nombre_oportunidad,
            oc.id_oc,
            oc.nro_oc,
            oc.moneda,
            SUM(oc.monto_oc) AS monto_total_oc,
            SUM(f.monto_factura) AS monto_total_factura
        FROM propuestas p
        JOIN ordenes_compra oc ON p.id = oc.id_propuesta
        LEFT JOIN facturas f ON oc.id_oc = f.id_oc
        WHERE p.status = 'Booking'
        GROUP BY p.id, oc.id_oc
        ORDER BY p.id, oc.fecha_oc
    """)
    resumen = cursor.fetchall()
    conn.close()
    return resumen

def obtener_status_propuesta(id_propuesta):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM propuestas WHERE id = ?", (id_propuesta,))
    fila = cursor.fetchone()
    conn.close()
    return fila["status"] if fila else None

def obtener_moneda_oc_existentes(id_propuesta):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT moneda FROM ordenes_compra WHERE id_propuesta = ?", (id_propuesta,))
    monedas = [fila["moneda"] for fila in cursor.fetchall()]
    conn.close()
    return monedas

def leer_ordenes_compra(id_propuesta):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ordenes_compra WHERE id_propuesta = ?", (id_propuesta,))
    ordenes = cursor.fetchall()
    conn.close()
    return ordenes

def leer_facturas(id_propuesta):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.*
        FROM facturas f
        JOIN ordenes_compra oc ON f.id_oc = oc.id_oc
        WHERE oc.id_propuesta = ?
    """, (id_propuesta,))
    facturas = cursor.fetchall()
    conn.close()
    return facturas


def obtener_logs_por_propuesta():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_propuesta, campo, valor_anterior, valor_nuevo, fecha, usuario
        FROM logs_propuesta
        WHERE campo = 'status'
        ORDER BY fecha ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    logs_por_id = {}
    for row in rows:
        id_prop = row["id_propuesta"]
        logs_por_id.setdefault(id_prop, []).append({
            "campo": row["campo"],
            "valor_anterior": row["valor_anterior"],
            "valor_nuevo": row["valor_nuevo"],
            "fecha": row["fecha"],
            "usuario": row["usuario"]
        })
    return logs_por_id


def crear_nota_credito(datos):
    """
    Inserta una nota de crédito como una factura con monto negativo.
    No valida si el monto excede el de la OC.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO facturas (id_oc, nro_factura, fecha_factura, monto_factura)
            VALUES (?, ?, ?, ?)
        """, (
            datos["id_oc"],
            datos["nro_factura"],
            datos["fecha_factura"],
            datos["monto_factura"]
        ))
        conn.commit()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()
