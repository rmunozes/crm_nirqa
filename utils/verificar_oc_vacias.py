import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, '..', 'facturas_datos_reales.xlsx')

df = pd.read_excel(EXCEL_PATH)

print("🔍 Verificando filas con OC vacía o inválida...\n")

oc_invalidas = []

for index, row in df.iterrows():
    id_oc = str(row.get("id_oc", "")).strip()
    nro_factura = row.get("nro_factura", "¿sin número?")

    if not id_oc or id_oc.lower() == "nan":
        oc_invalidas.append((index + 2, nro_factura))  # +2 por encabezado y base 0

if oc_invalidas:
    print(f"🚫 Se encontraron {len(oc_invalidas)} filas con OC vacía o inválida:\n")
    for fila, factura in oc_invalidas:
        print(f"  - Fila {fila}: Factura {factura}")
else:
    print("✅ No se encontraron OCs vacías o inválidas.")
