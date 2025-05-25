"""
Archivo para agregar mas roles a la tabla usuarios
También se debe actualizar manualmente la lista "ROLES" en listas_datos.py

"""


import sqlite3
import os
from datetime import datetime

# Ruta dinámica a la base de datos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'crm_database.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Generar nombre único para el respaldo
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_table = f"usuarios_backup_{timestamp}"

try:
    # Renombrar la tabla original como respaldo
    cursor.execute(f"ALTER TABLE usuarios RENAME TO {backup_table}")

    # Crear la nueva tabla con el campo rol actualizado
    cursor.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            rol TEXT NOT NULL CHECK (
                rol IN (
                    'administrador', 'gerente', 'director', 
                    'account_manager', 'preventa', 'gestor',
                    'gerente_ventas', 'gerente_preventa', 'director_comercial'
                )
            ),
            activo INTEGER NOT NULL DEFAULT 1
        )
    """)

    # Copiar los datos desde la tabla de respaldo (solo filas con roles válidos)
    cursor.execute(f"""
        INSERT INTO usuarios (id, nombre, email, password, rol, activo)
        SELECT id, nombre, email, password, rol, activo
        FROM {backup_table}
        WHERE rol IN (
            'administrador', 'gerente', 'director', 
            'account_manager', 'preventa', 'gestor',
            'gerente_ventas', 'gerente_preventa', 'director_comercial'
        )
    """)

    conn.commit()
    print(f"✅ Tabla usuarios modificada correctamente. Respaldo creado: {backup_table}")
except Exception as e:
    print("❌ Error:", e)
    conn.rollback()
finally:
    conn.close()
