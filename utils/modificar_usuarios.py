import sqlite3
import os

# Ruta dinámica a la base de datos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'crm_database.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # ✅ Eliminar respaldo anterior si existiera
    cursor.execute("DROP TABLE IF EXISTS usuarios_backup")

    # Renombrar la tabla original como respaldo
    cursor.execute("ALTER TABLE usuarios RENAME TO usuarios_backup")

    # Crear la nueva tabla con el campo rol actualizado
    cursor.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            rol TEXT NOT NULL CHECK (
                rol IN ('administrador', 'gerente', 'director', 'account_manager', 'preventa', 'gestor')
            ),
            activo INTEGER NOT NULL DEFAULT 1
        )
    """)

    # Copiar los datos desde la tabla de respaldo (solo filas con roles válidos)
    cursor.execute("""
        INSERT INTO usuarios (id, nombre, email, password, rol, activo)
        SELECT id, nombre, email, password, rol, activo
        FROM usuarios_backup
        WHERE rol IN ('administrador', 'gerente', 'director', 'account_manager', 'preventa', 'gestor')
    """)

    # Eliminar la tabla de respaldo si todo salió bien
    cursor.execute("DROP TABLE usuarios_backup")

    conn.commit()
    print("✅ Tabla usuarios modificada con nuevo rol 'director' incluido.")
except Exception as e:
    print("❌ Ocurrió un error:", e)
    conn.rollback()
finally:
    conn.close()
