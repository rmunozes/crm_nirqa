import pandas as pd
import sqlite3
import os
from datetime import datetime

# Ruta a la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../database/crm_database.db")
EXCEL_PATH = os.path.join(BASE_DIR, "propuestas_datos_reales.xlsx")

# ⚠️ DOBLE ADVERTENCIA
print("⚠️ ESTE SCRIPT REEMPLAZARÁ TODOS LOS DATOS DE LA TABLA 'propuestas'")
confirmacion1 = input("¡¡¡PELIGRO !!! ¿Estás seguro que deseas continuar? Escribe 'CONFIRMAR': ")
if confirmacion1 != "CONFIRMAR":
    print("❌ Operación cancelada.")
    exit()

confirmacion2 = input("Para continuar, escribe 'PROCEDER': ")
if confirmacion2 != "PROCEDER":
    print("❌ Operación cancelada.")
    exit()

# Cargar Excel
df = pd.read_excel(EXCEL_PATH)

# Validar columnas requeridas
columnas_esperadas = {
    "id", "nro_antiguo", "fecha_solicitud", "fecha_actualizacion",
    "cliente", "cliente_final", "nombre_oportunidad",
    "account_manager", "contacto_cliente", "preventa_asignado",
    "probabilidad_cierre", "status", "cierre_soles", "cierre_dolares", "comentarios"
}

faltantes = columnas_esperadas - set(df.columns)
if faltantes:
    print(f"❌ Faltan columnas en el Excel: {faltantes}")
    exit()

# Convertir fechas
for campo_fecha in ["fecha_solicitud", "fecha_actualizacion"]:
    df[campo_fecha] = pd.to_datetime(df[campo_fecha], errors="coerce").dt.date

# Convertir nulos en numéricos
df["probabilidad_cierre"] = pd.to_numeric(df["probabilidad_cierre"], errors="coerce").fillna(0.0)
df["cierre_soles"] = pd.to_numeric(df["cierre_soles"], errors="coerce").fillna(0.0)
df["cierre_dolares"] = pd.to_numeric(df["cierre_dolares"], errors="coerce").fillna(0.0)

# Conectar a la base de datos
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Eliminar todo
cursor.execute("DELETE FROM propuestas")
conn.commit()

# Insertar fila por fila
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO propuestas (
            id, nro_antiguo, fecha_solicitud, fecha_actualizacion,
            cliente, cliente_final, nombre_oportunidad,
            account_manager, contacto_cliente, preventa_asignado,
            probabilidad_cierre, status, cierre_soles, cierre_dolares, comentarios
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["id"],
        row["nro_antiguo"],
        row["fecha_solicitud"].isoformat() if pd.notnull(row["fecha_solicitud"]) else None,
        row["fecha_actualizacion"].isoformat() if pd.notnull(row["fecha_actualizacion"]) else None,
        row["cliente"],
        row["cliente_final"],
        row["nombre_oportunidad"],
        row["account_manager"],
        row["contacto_cliente"],
        row["preventa_asignado"],
        row["probabilidad_cierre"],
        row["status"],
        row["cierre_soles"],
        row["cierre_dolares"],
        row["comentarios"]
    ))

conn.commit()
conn.close()
print("✅ Datos de propuestas cargados exitosamente.")
