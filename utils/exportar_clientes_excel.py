import sqlite3
import pandas as pd
import os

# Detecta la ruta absoluta del proyecto y construye la ruta a la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'crm_database.db')  # ajusta si tu ruta es diferente

# Conexión a la base de datos
try:
    conn = sqlite3.connect(DB_PATH)
    print("✅ Conexión exitosa a la base de datos")

    # Leer la tabla clientes
    df = pd.read_sql_query("SELECT * FROM clientes", conn)

    # Exportar a Excel
    output_file = os.path.join(BASE_DIR, "clientes_exportado.xlsx")
    df.to_excel(output_file, index=False)
    print(f"📁 Archivo exportado exitosamente: {output_file}")

except Exception as e:
    print(f"❌ Error al exportar: {e}")

finally:
    conn.close()
