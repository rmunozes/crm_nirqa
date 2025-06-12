import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["ENV"] = "production"

from utils.db_connection import get_db_connection

conn = get_db_connection()
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
tables = cur.fetchall()
print("🧪 Tablas en PostgreSQL:", tables)
conn.close()

