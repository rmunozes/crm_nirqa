
import sqlite3
import os

# Ruta a la base de datos
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, 'database', 'crm_database.db')

# Conectar y obtener estructura
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n📋 Estructura actual de la tabla 'propuestas':\n")
cursor.execute("PRAGMA table_info(propuestas)")
columnas = cursor.fetchall()
for col in columnas:
    print(f"Nombre: {col[1]:<20} Tipo: {col[2]}")

conn.close()
