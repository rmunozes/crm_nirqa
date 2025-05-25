
import pandas as pd
import sqlite3
import os
import re

# === Rutas ===
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_PATH = os.path.join(ROOT_DIR, 'propuestas_ejemplo.xlsx')
DB_PATH = os.path.join(ROOT_DIR, 'database', 'crm_database.db')

# === Leer Excel ===
df = pd.read_excel(EXCEL_PATH)

# === Validación nro_antiguo ===
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

# === Función para limpiar datos ===
def clean(val):
    if pd.isna(val):
        return None
    if isinstance(val, pd.Timestamp):
        return str(val.date())
    return str(val) if isinstance(val, (int, float)) else val

# === Conectar a la base de datos ===
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# === Generar ID incremental NQ000001 ===
cursor.execute("SELECT id FROM propuestas ORDER BY id DESC LIMIT 1")
last = cursor.fetchone()
last_num = int(last[0][2:]) if last else 0

# === Insertar fila por fila ===
for _, row in df.iterrows():
    nuevo_id = f"NQ{last_num + 1:06d}"
    last_num += 1

    nro_antiguo = validar_nro_antiguo(row.get("nro_antiguo"))

    data = (
        nuevo_id,
        clean(row.get("nro_oportunidad")),
        nro_antiguo,
        clean(row.get("fecha_solicitud")),
        clean(row.get("fecha_actualizacion")),
        clean(row.get("cliente")),
        clean(row.get("cliente_final")),
        clean(row.get("nombre_oportunidad")),
        clean(row.get("account_manager")),
        clean(row.get("contacto_cliente")),
        clean(row.get("preventa_asignado")),
        row.get("probabilidad_cierre"),
        clean(row.get("status")),
        row.get("cierre_soles"),
        row.get("cierre_dolares")
    )

    cursor.execute("""
        INSERT INTO propuestas (
            id, nro_oportunidad, nro_antiguo, fecha_solicitud, fecha_actualizacion,
            cliente, cliente_final, nombre_oportunidad, account_manager,
            contacto_cliente, preventa_asignado, probabilidad_cierre,
            status, cierre_soles, cierre_dolares
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

conn.commit()
conn.close()
print("✅ Datos importados exitosamente a la nueva base limpia.")
