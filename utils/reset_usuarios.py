import sqlite3
import bcrypt
import os
import shutil

import os
DB_PATH = os.path.join(os.path.dirname(__file__), "../database/crm_database.db")
DB_PATH = os.path.abspath(DB_PATH)


# Usuarios iniciales a crear
usuarios_iniciales = [
    {"nombre": "Administrador General", "email": "admin@empresa.com", "password": "admin123", "rol": "administrador"},
    {"nombre": "Gerente Comercial", "email": "gerente@empresa.com", "password": "gerente123", "rol": "administrador"},
    {"nombre": "Ricardo del Valle", "email": "ricardo@nirqa.com", "password": "ricardo123", "rol": "preventa"},
    {"nombre": "Eder Huillca", "email": "eder@nirqa.com", "password": "eder123", "rol": "preventa"},
    {"nombre": "Jhonny Avila", "email": "jhonny.avila@nirqa.com", "password": "jhonny123", "rol": "preventa"},
    {"nombre": "Andrea U", "email": "andrea.u@nirqa.com", "password": "andrea123", "rol": "account_manager"},
    {"nombre": "Raphael Muñoz", "email": "raphael.munoz@nirqa.com", "password": "raphael123", "rol": "account_manager"},
    {"nombre": "Alejandra O", "email": "alejandra@nirqa.com", "password": "alejandra123", "rol": "account_manager"},
    {"nombre": "Jorge Avendaño", "email": "jorge.avendano@nirqa.com", "password": "jorge123", "rol": "preventa"},
]

def conectar_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hacer_respaldo():
    backup_path = DB_PATH.replace(".db", "_backup.db")
    shutil.copyfile(DB_PATH, backup_path)
    print(f"📄 Se creó una copia de respaldo en {backup_path}.")

def resetear_usuarios():
    print("\n========================================")
    print(" ATENCIÓN ⚠️  - RESETEO DE USUARIOS")
    print("========================================")
    print("Este script eliminará TODOS los usuarios actuales y los reemplazará")
    print("por un conjunto de usuarios iniciales predefinidos.\n")
    print("SI CONTINÚAS, los usuarios actuales serán PERDIDOS (aunque se hará una copia de respaldo).\n")

    print("Opciones:")
    print(" 1. Resetear Usuarios")
    print(" 2. Salir")

    opcion = input("\nIngrese una opción: ")

    if opcion != "1":
        print("Operación cancelada. ❌")
        return

    confirmacion = input("\n¿ESTÁS SEGURO DE QUERER RESETEAR LOS USUARIOS? (escriba 'sí' o 'si' para continuar): ").strip().lower()
    if confirmacion not in ["sí", "si"]:
        print("\nOperación cancelada. No se realizó ningún cambio. ❌")
        return

    hacer_respaldo()

    conn = conectar_db()
    cursor = conn.cursor()

    try:
        # Eliminamos todos los usuarios
        cursor.execute("DELETE FROM usuarios")
        conn.commit()

        # Insertamos los usuarios iniciales
        for usuario in usuarios_iniciales:
            hashed_password = bcrypt.hashpw(usuario["password"].encode("utf-8"), bcrypt.gensalt())
            cursor.execute("""
                INSERT INTO usuarios (nombre, email, password, rol, activo)
                VALUES (?, ?, ?, ?, 1)
            """, (usuario["nombre"], usuario["email"], hashed_password, usuario["rol"]))

        conn.commit()
        print("\n✅ Usuarios reseteados exitosamente.")
    except Exception as e:
        print(f"Error durante el reseteo: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    resetear_usuarios()
