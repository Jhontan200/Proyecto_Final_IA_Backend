from config.database import supabase

def diagnosticar_entorno_apple():
    print("\n🔍 --- DIAGNÓSTICO DE IPHONES Y PREGUNTAS CLAVE ---")
    try:
        # 1. Escaneo de inventario Apple (Consulta corregida sin la columna precio)
        iphones = supabase.table("dispositivos").select("id_dispositivo, modelo, sistema_operativo").ilike("modelo", "%iPhone%").execute()
        print(f"\n🍏 Total de iPhones físicos en la BD: {len(iphones.data)}")
        for ip in iphones.data:
            print(f"   📱 ID: {ip.get('id_dispositivo')} | {ip.get('modelo')} | OS: {ip.get('sistema_operativo')}")
            
        # 2. Mapeo de IDs de Cuestionario
        preguntas = supabase.table("preguntas").select("id_pregunta, pregunta").order("id_pregunta", desc=False).execute()
        print(f"\n📋 Catálogo de Preguntas ({len(preguntas.data)} en total):")
        for p in preguntas.data:
            print(f"   ID {p['id_pregunta']} -> {p['pregunta'][:60]}...")

    except Exception as e:
        print(f"❌ Error al consultar Supabase: {e}")

if __name__ == "__main__":
    diagnosticar_entorno_apple()