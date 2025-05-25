from datetime import datetime
from utils.db_connection import get_db_connection
from services.propuesta_validations import (
    validar_fecha,
    validar_probabilidad_cierre,
    validar_valor_numerico_opcional
)

class Propuesta:
    def __init__(self, id, nro_antiguo, fecha_solicitud, fecha_actualizacion,
                 cliente, cliente_final, nombre_oportunidad, account_manager,
                 contacto_cliente, preventa_asignado, probabilidad_cierre,
                 status, cierre_soles, cierre_dolares, comentarios):
        self.id = id
        self.nro_antiguo = nro_antiguo
        self.fecha_solicitud = fecha_solicitud
        self.fecha_actualizacion = fecha_actualizacion
        self.cliente = cliente
        self.cliente_final = cliente_final
        self.nombre_oportunidad = nombre_oportunidad
        self.account_manager = account_manager
        self.contacto_cliente = contacto_cliente
        self.preventa_asignado = preventa_asignado
        self.probabilidad_cierre = probabilidad_cierre
        self.status = status
        self.cierre_soles = cierre_soles
        self.cierre_dolares = cierre_dolares
        self.comentarios = comentarios

    @property
    def nro_oportunidad(self):
        return self.id

def leer_propuestas(filtros=None, pagina=1, filas_por_pagina=50, sort=None, order="asc"):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT id, nro_antiguo, fecha_solicitud, fecha_actualizacion,
               cliente, cliente_final, nombre_oportunidad, account_manager,
               contacto_cliente, preventa_asignado, probabilidad_cierre,
               status, cierre_soles, cierre_dolares, comentarios
        FROM propuestas WHERE 1=1
    """

    params = []

    if filtros:
        if filtros.get("id"):
            query += " AND id LIKE ?"
            params.append(f"%{filtros['id']}%")
        if filtros.get("nro_antiguo"):
            query += " AND nro_antiguo LIKE ?"
            params.append(f"%{filtros['nro_antiguo']}%")
        if filtros.get("cliente"):
            query += " AND cliente LIKE ?"
            params.append(f"%{filtros['cliente']}%")
        if filtros.get("cliente_final"):
            query += " AND cliente_final LIKE ?"
            params.append(f"%{filtros['cliente_final']}%")
        if filtros.get("preventa_asignado"):
            query += " AND preventa_asignado LIKE ?"
            params.append(f"%{filtros['preventa_asignado']}%")
        if filtros.get("status"):
            query += " AND status LIKE ?"
            params.append(f"%{filtros['status']}%")
        if filtros.get("account_manager"):
            query += " AND account_manager LIKE ?"
            params.append(f"%{filtros['account_manager']}%")
        if filtros.get("nombre_oportunidad"):
            query += " AND nombre_oportunidad LIKE ?"
            params.append(f"%{filtros['nombre_oportunidad']}%")
        if filtros.get("contacto_cliente"):
            query += " AND contacto_cliente LIKE ?"
            params.append(f"%{filtros['contacto_cliente']}%")
        if filtros.get("probabilidad_cierre"):
            query += " AND probabilidad_cierre = ?"
            params.append(float(filtros["probabilidad_cierre"]))
        if filtros.get("fecha_solicitud_desde"):
            query += " AND fecha_solicitud >= ?"
            params.append(filtros["fecha_solicitud_desde"])
        if filtros.get("fecha_solicitud_hasta"):
            query += " AND fecha_solicitud <= ?"
            params.append(filtros["fecha_solicitud_hasta"])
        if filtros.get("fecha_actualizacion_desde"):
            query += " AND fecha_actualizacion >= ?"
            params.append(filtros["fecha_actualizacion_desde"])
        if filtros.get("fecha_actualizacion_hasta"):
            query += " AND fecha_actualizacion <= ?"
            params.append(filtros["fecha_actualizacion_hasta"])
        if filtros.get("cierre_soles_min"):
            query += " AND cierre_soles >= ?"
            params.append(float(filtros["cierre_soles_min"]))
        if filtros.get("cierre_soles_max"):
            query += " AND cierre_soles <= ?"
            params.append(float(filtros["cierre_soles_max"]))
        if filtros.get("cierre_dolares_min"):
            query += " AND cierre_dolares >= ?"
            params.append(float(filtros["cierre_dolares_min"]))
        if filtros.get("cierre_dolares_max"):
            query += " AND cierre_dolares <= ?"
            params.append(float(filtros["cierre_dolares_max"]))

    # Validación segura de columnas
    columnas_validas = [
        "id", "nro_antiguo", "fecha_solicitud", "fecha_actualizacion",
        "cliente", "cliente_final", "nombre_oportunidad", "account_manager",
        "contacto_cliente", "preventa_asignado", "probabilidad_cierre",
        "status", "cierre_soles", "cierre_dolares"
    ]
    if sort in columnas_validas:
        query += f" ORDER BY {sort} {'ASC' if order == 'asc' else 'DESC'}"
    else:
        # Ordenamiento por ID numérico descendente por defecto
        query += " ORDER BY CAST(SUBSTR(id, 3) AS INTEGER) DESC"

    offset = (pagina - 1) * filas_por_pagina
    query += " LIMIT ? OFFSET ?"
    params.extend([filas_por_pagina, offset])

    print(">>> CONSULTA SQL:", query)
    print(">>> PARÁMETROS:", params)

    cursor.execute(query, params)
    propuestas = [Propuesta(*row) for row in cursor.fetchall()]
    conn.close()
    return propuestas




def contar_propuestas(filtros=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT COUNT(*) FROM propuestas WHERE 1=1"
    params = []

    if filtros:
        if filtros.get("id"):
            query += " AND id LIKE ?"
            params.append(f"%{filtros['id']}%")
        if filtros.get("nro_antiguo"):
            query += " AND nro_antiguo LIKE ?"
            params.append(f"%{filtros['nro_antiguo']}%")
        if filtros.get("cliente"):
            query += " AND cliente LIKE ?"
            params.append(f"%{filtros['cliente']}%")
        if filtros.get("cliente_final"):
            query += " AND cliente_final LIKE ?"
            params.append(f"%{filtros['cliente_final']}%")
        if filtros.get("preventa_asignado"):
            query += " AND preventa_asignado LIKE ?"
            params.append(f"%{filtros['preventa_asignado']}%")
        if filtros.get("status"):
            query += " AND status LIKE ?"
            params.append(f"%{filtros['status']}%")
        if filtros.get("fecha_solicitud_desde"):
            query += " AND fecha_solicitud >= ?"
            params.append(filtros["fecha_solicitud_desde"])
        if filtros.get("fecha_solicitud_hasta"):
            query += " AND fecha_solicitud <= ?"
            params.append(filtros["fecha_solicitud_hasta"])

    cursor.execute(query, params)
    total = cursor.fetchone()[0]
    conn.close()
    return total

def guardar_propuesta(propuesta):
    validar_fecha(propuesta.fecha_solicitud)
    validar_fecha(propuesta.fecha_actualizacion)
    validar_probabilidad_cierre(propuesta.probabilidad_cierre)
    propuesta.cierre_soles = validar_valor_numerico_opcional(propuesta.cierre_soles)
    propuesta.cierre_dolares = validar_valor_numerico_opcional(propuesta.cierre_dolares)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO propuestas (
            id, nro_antiguo, fecha_solicitud, fecha_actualizacion,
            cliente, cliente_final, nombre_oportunidad, account_manager,
            contacto_cliente, preventa_asignado, probabilidad_cierre,
            status, cierre_soles, cierre_dolares, comentarios
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        propuesta.id, propuesta.nro_antiguo,
        propuesta.fecha_solicitud, propuesta.fecha_actualizacion, propuesta.cliente,
        propuesta.cliente_final, propuesta.nombre_oportunidad, propuesta.account_manager,
        propuesta.contacto_cliente, propuesta.preventa_asignado, propuesta.probabilidad_cierre,
        propuesta.status, propuesta.cierre_soles, propuesta.cierre_dolares, propuesta.comentarios
    ))

    conn.commit()
    conn.close()

def actualizar_propuesta(propuesta):
    validar_fecha(propuesta.fecha_solicitud)
    validar_fecha(propuesta.fecha_actualizacion)
    validar_probabilidad_cierre(propuesta.probabilidad_cierre)
    propuesta.cierre_soles = validar_valor_numerico_opcional(propuesta.cierre_soles)
    propuesta.cierre_dolares = validar_valor_numerico_opcional(propuesta.cierre_dolares)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE propuestas
        SET fecha_solicitud = ?, fecha_actualizacion = ?, nro_antiguo = ?, cliente = ?, cliente_final = ?,
            nombre_oportunidad = ?, account_manager = ?, contacto_cliente = ?, preventa_asignado = ?,
            probabilidad_cierre = ?, status = ?, cierre_soles = ?, cierre_dolares = ?
        WHERE id = ?
    """, (
        propuesta.fecha_solicitud, propuesta.fecha_actualizacion, propuesta.nro_antiguo, propuesta.cliente,
        propuesta.cliente_final, propuesta.nombre_oportunidad, propuesta.account_manager,
        propuesta.contacto_cliente, propuesta.preventa_asignado, propuesta.probabilidad_cierre,
        propuesta.status, propuesta.cierre_soles, propuesta.cierre_dolares, propuesta.id
    ))
    conn.commit()
    conn.close()

import re

def generar_nuevo_id(propuestas):
    patron = re.compile(r"^NQ\d{6}$")
    max_num = 0
    for p in propuestas:
        if p.id and patron.match(p.id):
            num = int(p.id[2:])
            if num > max_num:
                max_num = num
    return f"NQ{max_num + 1:06d}"


def actualizar_comentario(id, comentarios):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE propuestas SET comentarios = ? WHERE id = ?", (comentarios, id))
    conn.commit()
    conn.close()


#agregar comentario en editar_propuesta
def leer_logs_propuesta(id_propuesta):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT campo, valor_anterior, valor_nuevo, usuario, fecha
        FROM logs_propuesta
        WHERE id_propuesta = ?
        ORDER BY fecha DESC
    """, (id_propuesta,))
    logs = cursor.fetchall()
    conn.close()
    return logs



def guardar_log(id_propuesta, campo, valor_anterior, valor_nuevo, usuario_id):
    from datetime import datetime
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs_propuesta (id_propuesta, campo, valor_anterior, valor_nuevo, fecha, usuario)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        id_propuesta,
        campo,
        valor_anterior,
        valor_nuevo,
        datetime.now().isoformat(timespec='seconds'),
        usuario_id  # aquí todavía puedes pasar el ID o nombre, según cómo uses `usuario`
    ))

    conn.commit()
    conn.close()

def obtener_propuesta_por_id(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM propuestas WHERE id = ?", (id,))
    propuesta = cursor.fetchone()
    conn.close()
    return propuesta
