import sqlite3
import pandas as pd
import os

# Ruta a tu base de datos

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'database', 'crm_database.db')
EXCEL_PATH = os.path.join(BASE_DIR, '..', 'facturas_datos_reales.xlsx')


# Leer Excel
df = pd.read_excel(EXCEL_PATH)

# Conectar a la base de datos
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

errores = []
insertadas = 0

for index, row in df.iterrows():
    nro_factura = str(row["nro_factura"]).strip()
    id_oc = str(row["id_oc"]).strip()
    fecha_factura = str(row["fecha_factura"]).strip()

    monto_soles = row.get("monto_factura_soles", None)
    monto_dolares = row.get("monto_factura_dolares", None)

    try:
        # Validar existencia de OC
        cursor.execute("SELECT id_oc FROM ordenes_compra WHERE nro_oc = ?", (id_oc,))
        oc_row = cursor.fetchone()
        if not oc_row:
            errores.append(f"❌ OC no encontrada: {id_oc}")
            continue

        id_oc_fk = oc_row[0]

        # Validar duplicado
        cursor.execute("SELECT 1 FROM facturas WHERE nro_factura = ?", (nro_factura,))
        if cursor.fetchone():
            errores.append(f"⚠️ Factura ya existe: {nro_factura}")
            continue

        # Validar moneda y monto
        if pd.notna(monto_soles) and pd.isna(monto_dolares):
            moneda = "S/"
            monto_s = float(monto_soles)
            monto_d = None
        elif pd.isna(monto_soles) and pd.notna(monto_dolares):
            moneda = "US$"
            monto_s = None
            monto_d = float(monto_dolares)
        else:
            errores.append(f"❌ Moneda ambigua para factura {nro_factura}")
            continue

        # Insertar
        cursor.execute("""
            INSERT INTO facturas (id_oc, nro_factura, monto_factura_soles, monto_factura_dolares, fecha_factura)
            VALUES (?, ?, ?, ?, ?)
        """, (id_oc_fk, nro_factura, monto_s, monto_d, fecha_factura))
        insertadas += 1

    except Exception as e:
        errores.append(f"❌ Error en fila {index}: {str(e)}")

# Finalizar
conn.commit()
conn.close()

print(f"✅ Facturas insertadas: {insertadas}")
if errores:
    print("⚠️ Errores encontrados:")
    for err in errores:
        print(err)
