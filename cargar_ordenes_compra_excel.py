import pandas as pd
import sqlite3
import os
from datetime import datetime

def cargar_ordenes_compra_desde_excel(confirmar=True):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "database", "crm_database.db")
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

    for _, row in df.iterrows():
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
            float(row["monto_oc"]),
            str(row["pm_asignado"]) if pd.notnull(row["pm_asignado"]) else "",
            str(row["moneda"])
        ))

    conn.commit()
    conn.close()

    if not confirmar:
        print("✅ Ordenes de compra cargadas exitosamente.")
    return len(df)

if __name__ == "__main__":
    cargar_ordenes_compra_desde_excel(confirmar=True)
