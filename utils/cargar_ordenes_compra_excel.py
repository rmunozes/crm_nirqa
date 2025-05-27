import pandas as pd
import sqlite3
import os
from datetime import datetime

def cargar_ordenes_compra_desde_excel(confirmar=True):

    import os

    # Rutas absolutas corregidas
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DB_PATH = os.path.join(BASE_DIR, "database", "crm_database.db")
    EXCEL_PATH = os.path.join(BASE_DIR, "utils", "oc_datos_reales.xlsx")

    print("🧭 Usando base de datos:", DB_PATH)
    print("📄 Usando archivo Excel:", EXCEL_PATH)

    EXCEL_PATH = os.path.join(BASE_DIR, "oc_datos_reales.xlsx")

    if confirmar:
        print("⚠️ ESTE SCRIPT REEMPLAZARÁ TODOS LOS DATOS DE LA TABLA 'ordenes_compra'")
        conf1 = input("¿Estás seguro? Escribe 'CONFIRMAR': ")
        if conf1 != "CONFIRMAR":
            print("❌ Operación cancelada.")
            return
        conf2 = input("Para continuar, escribe 'PROCEDER': ")
        if conf2 != "PROCEDER":
            print("❌ Operación cancelada.")
            return

    df = pd.read_excel(EXCEL_PATH)

    columnas_requeridas = {
        "id_oc", "id_propuesta", "nro_oc", "fecha_oc", "monto_oc", "pm_asignado", "moneda"
    }
    if not columnas_requeridas.issubset(set(df.columns)):
        raise Exception(f"❌ Faltan columnas: {columnas_requeridas - set(df.columns)}")

    df["fecha_oc"] = pd.to_datetime(df["fecha_oc"], errors="coerce").dt.date
    df["monto_oc"] = pd.to_numeric(df["monto_oc"], errors="coerce").fillna(0.0)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM ordenes_compra")
    conn.commit()

    contador_ok = 0
    contador_skip = 0

    for index, row in df.iterrows():
        try:
            monto = float(row["monto_oc"])
            if monto <= 0:
                print(f"⚠️ OC ignorada (monto inválido <= 0): ID {row['id_oc']}")
                contador_skip += 1
                continue

            cursor.execute("""
                INSERT INTO ordenes_compra (
                    id_oc, id_propuesta, nro_oc, fecha_oc,
                    monto_oc, pm_asignado, moneda
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row["id_oc"]),
                str(row["id_propuesta"]),
                str(row["nro_oc"]),
                row["fecha_oc"].isoformat() if pd.notnull(row["fecha_oc"]) else None,
                monto,
                str(row["pm_asignado"]) if pd.notnull(row["pm_asignado"]) else "",
                str(row["moneda"])
            ))
            contador_ok += 1
        except Exception as e:
            print(f"❌ Error al procesar OC ID {row.get('id_oc', '?')}: {e}")
            contador_skip += 1

    conn.commit()
    conn.close()

    print(f"✅ OC cargadas correctamente: {contador_ok}")
    print(f"⚠️ OC omitidas por error o validación: {contador_skip}")

    if not confirmar:
        print("✅ Carga completada automáticamente.")

    return contador_ok

if __name__ == "__main__":
    cargar_ordenes_compra_desde_excel(confirmar=True)
