
import sqlite3
import os

# === Rutas ===
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, 'database', 'crm_database.db')

# === Conectar a la base de datos ===
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print(f"📌 Usando base de datos en: {DB_PATH}")

# === Eliminar y recrear la tabla ===
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
print("✅ Tabla 'propuestas' recreada correctamente con la estructura esperada.")
