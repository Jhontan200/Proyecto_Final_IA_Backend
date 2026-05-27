# models/cuestionario_model.py
from config.database import supabase  # <-- Importamos el cliente global de Supabase

class CuestionarioModel:
    @staticmethod
    def obtener_preguntas_con_respuestas():
        """Cruza las tablas 'preguntas' y 'respuestas' para generar el formulario dinámico"""
        try:
            # Reemplazamos el SQL crudo por la API declarativa de Supabase.
            # Realiza un LEFT JOIN automático usando la relación de llaves foráneas.
            respuesta = (
                supabase.table("preguntas")
                .select("id_pregunta, pregunta, respuestas(valor)")
                .order("id_pregunta", ascending=True)
                .execute()
            )

            # respuesta.data ya viene convertido en una lista de diccionarios de Python
            datos_raw = respuesta.data
            formulario = []
            
            for item in datos_raw:
                # Extraemos los strings de la columna 'valor' dentro del nodo anidado de respuestas
                opciones = [r["valor"] for r in item.get("respuestas", []) if r.get("valor") is not None]
                
                # Mantenemos exactamente la misma estructura de salida para el Agente Interfaz
                formulario.append({
                    "id_pregunta": item["id_pregunta"],
                    "pregunta": item["pregunta"],
                    "opciones": opciones
                })
                
            return formulario
            
        except Exception as e:
            print(f"Error en CuestionarioModel con Supabase API: {e}")
            return []
        # Nota: Ya no es necesario el bloque 'finally' ni 'conn.close()' 
        # porque la API gestiona las peticiones HTTP de forma automática.