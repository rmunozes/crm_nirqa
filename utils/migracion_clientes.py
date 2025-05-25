
import sqlite3

# Ruta a tu base de datos
db_path = "database/crm_database.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Agrega la columna 'contacto' si no existe
try:
    cursor.execute("ALTER TABLE clientes ADD COLUMN contacto TEXT")
    print("✅ Columna 'contacto' añadida correctamente.")
except sqlite3.OperationalError as e:
    print("⚠️ Ya existe o hubo un error:", e)

conn.commit()
conn.close()
