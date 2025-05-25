
import sqlite3
import os

# Ruta a la base de datos
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, 'database', 'crm_database.db')

# Crear conexión
print(f'📌 Usando base de datos en: {DB_PATH}')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Eliminar y crear tabla propuestas con todos los campos correctos
cursor.executescript("""
DROP TABLE IF EXISTS propuestas;

CREATE TABLE propuestas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
print("✅ Tabla 'propuestas' recreada con el campo 'nro_antiguo' correctamente.")
