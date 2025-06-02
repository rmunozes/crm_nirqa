import sqlite3
import pandas as pd
import os

# Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'crm_database.db')
EXCEL_PATH = os.path.join(BASE_DIR, '..', 'facturas_datos_reales.xlsx')
EXPORT_PATH = os.path.join(BASE_DIR, '..', 'ocs_no_encontradas.xlsx')

# Leer Excel
df = pd.read_excel(EXCEL_PATH)

# Extraer OCs únicas del Excel
ocs_excel = df['id_oc'].dropna().astype(str).str.strip().unique()

# Conectar a la base de datos
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Verificar OC una por una
ocs_no_encontradas = []
for oc in ocs_excel:
    cursor.execute("SELECT id_oc FROM ordenes_compra WHERE nro_oc = ?", (oc,))
    if not cursor.fetchone():
        ocs_no_encontradas.append(oc)

conn.close()

# Mostrar resultados
print("📌 Total OCs únicas en Excel:", len(ocs_excel))
print("❌ OCs no encontradas en base de datos:", len(ocs_no_encontradas))
print("------------")
for oc in ocs_no_encontradas:
    print(oc)

# Exportar a Excel
df_resultado = pd.DataFrame(ocs_no_encontradas, columns=["OC_no_encontrada"])
df_resultado.to_excel(EXPORT_PATH, index=False)
print(f"✅ Lista exportada a: {EXPORT_PATH}")
