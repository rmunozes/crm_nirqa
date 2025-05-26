import pandas as pd
import sqlite3
import os

# Ruta dinámica de la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../database/crm_database.db")

# ⚠️ Advertencia de seguridad
print("⚠️ ADVERTENCIA: Este script BORRARÁ TODOS LOS CLIENTES existentes en la base de datos.")
confirmacion = input("¿Estás seguro que deseas continuar? Escribe 'CONFIRMAR' para continuar: ")
if confirmacion != "CONFIRMAR":
    print("❌ Operación cancelada.")
    exit()

# Ruta al archivo Excel real
excel_file = os.path.join(BASE_DIR, "clientes_datos_reales.xlsx")

# Lee el archivo
df = pd.read_excel(excel_file)

# Asegura columnas requeridas
columnas_requeridas = {"nombre", "direccion", "telefono", "email"}
faltantes = columnas_requeridas - set(df.columns)
if faltantes:
    print(f"❌ El archivo Excel debe tener las columnas: {columnas_requeridas}")
    exit()

# Agrega columnas faltantes opcionales
for col in ["contacto_principal", "notas"]:
    if col not in df.columns:
        df[col] = None

# Conecta y borra registros anteriores
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DELETE FROM clientes")
conn.commit()

# Inserta nuevos
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO clientes (nombre, direccion, telefono, email, contacto_principal, notas)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        row["nombre"],
        row["direccion"],
        row["telefono"],
        row["email"],
        row["contacto_principal"],
        row["notas"]
    ))

conn.commit()
conn.close()
print("✅ Datos de clientes cargados exitosamente.")
