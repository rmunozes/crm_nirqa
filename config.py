import os
from dotenv import load_dotenv

load_dotenv()  # Se asegura de cargar el .env lo antes posible

MODE = os.getenv("MODE")
DATABASE_URL = os.getenv("DATABASE_URL")
