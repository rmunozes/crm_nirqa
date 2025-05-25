
import sqlite3
import os

# === Definir nueva ruta de base de datos ===
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEW_DB_PATH = os.path.join(ROOT_DIR, 'database', 'crm_database_nuevo.db')

# === Crear nueva base de datos y tabla ===
conn = sqlite3.connect(NEW_DB_PATH)
cursor = conn.cursor()

print(f"📌 Creando nueva base de datos en: {NEW_DB_PATH}")

cursor.executescript("""
DROP TABLE IF EXISTS propuestas;

CREATE TABLE propuestas (
    id TEXT PRIMARY KEY,
    nro_oportunidad TEXT,
    nro_antiguo TEXT,
    fecha_solicitud TEXT,
    fecha_actualizacion TEXT,
    cliente TEXT,
    cliente_final TEXT,
    nombre_oportunidad TEXT,
    account_manager TEXT,
    contacto_cliente TEXT,
    preventa_asignado TEXT,
    probabilidad_cierre REAL,
    status TEXT,
    cierre_soles REAL,
    cierre_dolares REAL
);
""")

conn.commit()
conn.close()
print("✅ Base de datos y tabla 'propuestas' creadas correctamente.")
