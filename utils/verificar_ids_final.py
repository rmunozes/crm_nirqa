
import sqlite3

# Ruta absoluta a la base de datos
DB_PATH = "/Users/raphaelmunoz/PycharmProjects/PROYECTO_CRM/database/crm_database.db"

# Conectar y mostrar propuestas
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT id, nro_oportunidad, nro_antiguo FROM propuestas ORDER BY id")
rows = cursor.fetchall()
conn.close()

print("\n✅ Verificación final de IDs con formato NQXXXXXX:")
for row in rows:
    print(dict(row))
