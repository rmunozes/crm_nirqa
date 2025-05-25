
import pandas as pd
import sqlite3
import os
import re
import math

# === Configuración de rutas ===
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_PATH = os.path.join(ROOT_DIR, 'propuestas_ejemplo.xlsx')
DB_PATH = os.path.join(ROOT_DIR, 'database', 'crm_database.db')

# === Validación del campo nro_antiguo ===
def validar_nro_antiguo(valor):
    if not valor or pd.isna(valor):
        return None
    valor_str = str(valor).strip()
    patron = r'^\d{4}N\d+$'
    if re.match(patron, valor_str):
        return valor_str
    else:
        print(f"⚠️ Formato inválido en 'nro_antiguo': {valor_str} — se ignorará.")
        return None

# === Leer Excel ===
df = pd.read_excel(EXCEL_PATH)

# === Establecer conexión a la base de datos ===
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# === Verificar el último ID secuencial ===
cursor.execute("SELECT id FROM propuestas ORDER BY id DESC LIMIT 1")
last_id = cursor.fetchone()
if last_id and isinstance(last_id[0], str) and last_id[0].startswith("NQ"):
    ultimo_num = int(last_id[0][2:])
else:
    ultimo_num = 0

# === Insertar datos ===
for _, row in df.iterrows():
    nuevo_id = f"NQ{ultimo_num + 1:06d}"
    ultimo_num += 1

    valor_raw = row.get("nro_antiguo", None)
    nro_antiguo_valido = validar_nro_antiguo(valor_raw)
    nro_antiguo = str(nro_antiguo_valido) if nro_antiguo_valido else None

    def clean(val):
        return None if pd.isna(val) or (isinstance(val, float) and math.isnan(val)) else val

    print(f"📌 nro_antiguo = {repr(nro_antiguo)} | tipo = {type(nro_antiguo)}")

    data = (
        nuevo_id,
        clean(row["nro_oportunidad"]),
        nro_antiguo,
        clean(row["fecha_solicitud"]),
        clean(row["fecha_actualizacion"]),
        clean(row["cliente"]),
        clean(row["cliente_final"]),
        clean(row["nombre_oportunidad"]),
        clean(row["account_manager"]),
        clean(row["contacto_cliente"]),
        clean(row["preventa_asignado"]),
        clean(row["probabilidad_cierre"]),
        clean(row["status"]),
        clean(row["cierre_soles"]),
        clean(row["cierre_dolares"])
    )

    cursor.execute("""
        INSERT INTO propuestas (
            id,
            nro_oportunidad,
            nro_antiguo,
            fecha_solicitud,
            fecha_actualizacion,
            cliente,
            cliente_final,
            nombre_oportunidad,
            account_manager,
            contacto_cliente,
            preventa_asignado,
            probabilidad_cierre,
            status,
            cierre_soles,
            cierre_dolares
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

conn.commit()
conn.close()
