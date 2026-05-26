import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Establece una conexión directa con la base de datos de Supabase."""
    try:
        # RealDictCursor nos permite recuperar las filas como diccionarios de Python {'columna': valor}
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"❌ Error crítico al conectar a Supabase: {e}")
        return None