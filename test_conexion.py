# test_conexion.py
from config.database import supabase

def diagnosticar_datos_reales():
    print("\n🔍 --- INSPECTOR DE DATOS RELACIONALES ---")
    try:
        # 1. Validar registros de dispositivos
        disp = supabase.table("dispositivos").select("id_dispositivo, modelo, id_categoria, ram").execute()
        print(f"📱 Total celulares en la tabla 'dispositivos': {len(disp.data)}")
        if disp.data:
            print(f"   💡 Ejemplo de fila 1: {disp.data[0]}")
        
        # 2. Validar registros de precios
        precios = supabase.table("precios").select("id_dispositivo, precio").execute()
        print(f"💰 Total registros en la tabla 'precios': {len(precios.data)}")
        if precios.data:
            print(f"   💡 Ejemplo de fila 1: {precios.data[0]}")
            
            # Calcular rango de precios en tiempo real
            valores = [float(p['precio']) for p in precios.data if p.get('precio')]
            if valores:
                print(f"   💵 Celular más barato en BD: {min(valores)} Bs")
                print(f"   💵 Celular más caro en BD: {max(valores)} Bs")

    except Exception as e:
        print(f"❌ Error al consultar Supabase: {e}")

if __name__ == "__main__":
    diagnosticar_datos_reales()