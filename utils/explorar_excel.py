
import pandas as pd
import os

# === Rutas ===
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_PATH = os.path.join(ROOT_DIR, 'propuestas_ejemplo.xlsx')

print(f"📁 Leyendo archivo: {EXCEL_PATH}")

# === Leer Excel y mostrar estructura ===
df = pd.read_excel(EXCEL_PATH)

print("\n🧾 Columnas del Excel:")
print(df.columns.tolist())

print("\n🔍 Primeras 5 filas:")
print(df.head(5))

print("\n📋 Tipos de datos:")
print(df.dtypes)
