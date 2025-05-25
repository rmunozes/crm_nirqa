
import sqlite3
import os

# Ruta al archivo de base de datos
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, 'database', 'crm_database.db')

# Conexión a la base de datos
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Eliminar tabla si existe y crearla nuevamente
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
print("✅ Tabla 'propuestas' recreada con ID tipo texto (formato NQXXXXXX).")
