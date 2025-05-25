import sqlite3
import os

def get_db_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, '..', 'database', 'crm_database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # ✅ Esto permite acceder a las columnas por nombre
    return conn

