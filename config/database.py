import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar las variables del archivo .env
load_dotenv()

# Obtenemos las nuevas credenciales para la API REST
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Inicializamos la instancia global del cliente
supabase: Client = None

try:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Faltan las variables SUPABASE_URL o SUPABASE_KEY en el archivo .env")
    
    # Se crea el cliente único (Pattern Singleton)
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("🚀 Cliente de Supabase inicializado correctamente a través de la API HTTP.")

except Exception as e:
    print(f"❌ Error crítico al inicializar el cliente de Supabase: {e}")
    supabase = None

def get_supabase() -> Client:
    """
    Retorna la instancia del cliente de Supabase.
    Reemplaza conceptualmente a la antigua función get_db_connection().
    """
    if supabase is None:
        print("⚠️ Advertencia: Intentando recuperar un cliente de Supabase no inicializado.")
    return supabase