from config.database import get_db_connection

class SBCModel:
    @staticmethod
    def obtener_preguntas():
        """Trae todas las preguntas registradas para el cuestionario del SBC."""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            query = "SELECT id_pregunta, pregunta FROM preguntas ORDER BY id_pregunta ASC;"
            cursor.execute(query)
            preguntas = cursor.fetchall()
            cursor.close()
            return preguntas
        except Exception as e:
            print(f"❌ Error al obtener preguntas: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def obtener_reglas():
        """Trae las reglas lógicas (condición y resultado) ordenadas por prioridad."""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            query = "SELECT id_regla, condicion, resultado, prioridad FROM reglas_sbc ORDER BY prioridad DESC;"
            cursor.execute(query)
            reglas = cursor.fetchall()
            cursor.close()
            return reglas
        except Exception as e:
            print(f"❌ Error al obtener reglas: {e}")
            return []
        finally:
            conn.close()