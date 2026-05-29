# models/sbc_model.py
from config.database import supabase  # <-- Importamos el cliente unificado

class SBCModel:
    @staticmethod
    def obtener_preguntas():
        """Trae todas las preguntas registradas para el cuestionario del SBC."""
        try:
            # Reemplazamos la consulta SQL por métodos declarativos del cliente
            respuesta = (
                supabase.table("preguntas")
                .select("id_pregunta, pregunta")
                .order("id_pregunta", desc=False)
                .execute()
            )
            
            # .data ya contiene la lista estructurada de diccionarios
            return respuesta.data
            
        except Exception as e:
            print(f"❌ Error al obtener preguntas con Supabase API: {e}")
            return []

    @staticmethod
    def obtener_reglas():
        """Trae las reglas lógicas (condición y resultado) ordenadas por prioridad."""
        try:
            # Reemplazamos el SELECT con ordenación descendente
            respuesta = (
                supabase.table("reglas_sbc")
                .select("id_regla, condicion, resultado, prioridad")
                .order("prioridad", desc=True)
                .execute()
            )
            
            return respuesta.data
            
        except Exception as e:
            print(f"❌ Error al obtener reglas con Supabase API: {e}")
            return []
        # Nota: Desaparecen los bloques 'finally' y 'conn.close()' en ambos métodos