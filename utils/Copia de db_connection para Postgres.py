import os
from dotenv import load_dotenv

# Cargar primero el entorno de desarrollo por defecto
load_dotenv(dotenv_path=".env.development")

# Detectar si se debe usar el entorno de producción
if os.getenv("ENV") == "production":
    load_dotenv(dotenv_path=".env.production", override=True)

# Modo de entorno
ENV = os.getenv("ENV", "development")
print("🔧 Modo:", ENV)

# Decidir si se usa SQLite (en desarrollo) o PostgreSQL (en producción)
USE_SQLITE = ENV == "development"

if USE_SQLITE:
    import sqlite3
    def get_db_connection():
        db_path = os.getenv("SQLITE_DB_PATH", "database/crm_database.db")
        print("📁 Conectando a SQLite en:", db_path)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

else:
    import psycopg2
    import psycopg2.extras
    def get_db_connection():
        db_url = os.getenv("DATABASE_URL")
        if db_url and "sslmode" not in db_url:
            db_url += "?sslmode=require"
        print("🐘 Conectando a PostgreSQL en:", db_url)
        return psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)
