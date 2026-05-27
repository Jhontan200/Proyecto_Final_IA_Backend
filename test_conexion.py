import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def probar_puente():
    print("🔄 Intentando conectar a Supabase vía API Client...")
    
    # Obtener credenciales desde el entorno
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: Faltan las variables SUPABASE_URL o SUPABASE_KEY en tu archivo .env")
        print("❌ CONEXIÓN FALLIDA. Revisa tu archivo .env.")
        return

    try:
        # Inicializar el cliente de Supabase (equivale a levantar el puente)
        supabase: Client = create_client(url, key)
        
        print("¡CONEXIÓN EXITOSA! 🎉")
        print(f"📡 Conectado exitosamente al proyecto: {url}")
        
        # Validar que tus tablas existan haciendo un conteo rápido de categorías
        # Usamos .count("exact") para emular el SELECT COUNT(*) de SQL
        print("📦 Verificando persistencia de datos...")
        respuesta = supabase.table("categorias").select("*", count="exact").limit(1).execute()
        
        # Obtener el total desde los metadatos de la respuesta
        total_categorias = respuesta.count
        print(f"📦 Conexión operacional. Categorías encontradas en tu base de datos: {total_categorias}")
        
    except Exception as e:
        print(f"❌ Error al ejecutar la consulta de prueba a través de la API: {e}")
        print("❌ Revisa que la tabla 'categorias' exista y que tus credenciales tengan los accesos correctos.")
    finally:
        # Nota: El cliente HTTP de Supabase no requiere un conn.close() explícito
        print("🔒 Sesión de prueba finalizada de forma segura.")

if __name__ == "__main__":
    probar_puente()