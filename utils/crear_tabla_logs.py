import sqlite3
import os

# Ruta dinámica al archivo DB
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "database", "crm_database.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 🚨 Elimina la tabla si existe
cursor.execute("DROP TABLE IF EXISTS logs_propuesta")

# ✅ Crea la tabla correcta
cursor.execute("""
    CREATE TABLE logs_propuesta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_propuesta TEXT NOT NULL,
        campo TEXT NOT NULL,
        valor_anterior TEXT,
        valor_nuevo TEXT,
        fecha TEXT NOT NULL,
        usuario TEXT NOT NULL
    )
""")

conn.commit()
conn.close()
print("✅ Tabla 'logs_propuesta' eliminada y recreada correctamente.")
