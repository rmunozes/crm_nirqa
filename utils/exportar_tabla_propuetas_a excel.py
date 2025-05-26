import os
import sqlite3
import pandas as pd

# Ruta dinámica basada en la ubicación de este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "crm_database.db")

try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM propuestas", conn)
    conn.close()

    output_path = os.path.join(BASE_DIR, "propuestas_exportadas.xlsx")
    df.to_excel(output_path, index=False)

    print(f"✅ Archivo Excel exportado exitosamente: {output_path}")

except Exception as e:
    print(f"❌ Error: {e}")
