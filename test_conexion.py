from config.database import get_db_connection

def probar_puente():
    print("🔄 Intentando conectar a Supabase...")
    conn = get_db_connection()
    
    if conn is None:
        print("❌ CONEXIÓN FALLIDA. Revisa tu archivo .env, tu contraseña o tu conexión a internet.")
        return

    try:
        cursor = conn.cursor()
        # Hacemos una consulta simple para pedirle la versión al servidor de Postgres
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print("¡CONEXIÓN EXITOSA! 🎉")
        print(f"📡 Conectado a: {db_version['version']}")
        
        # Opcional: Validar que tus tablas existan haciendo un conteo rápido de categorías
        cursor.execute("SELECT COUNT(*) FROM categorias;")
        total_categorias = cursor.fetchone()
        print(f"📦 Conexión operacional. Categorías encontradas en tu base de datos: {total_categorias['count']}")
        
        cursor.close()
    except Exception as e:
        print(f"❌ Error al ejecutar la consulta de prueba: {e}")
    finally:
        conn.close()
        print("🔒 Conexión cerrada de forma segura.")

if __name__ == "__main__":
    probar_puente()