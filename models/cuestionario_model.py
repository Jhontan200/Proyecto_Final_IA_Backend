from config.database import get_db_connection

class CuestionarioModel:
    @staticmethod
    def obtener_preguntas_con_respuestas():
        """Cruza las tablas 'preguntas' y 'respuestas' para generar el formulario dinámico"""
        conn = get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            # Leemos las preguntas y concatenamos sus respuestas válidas en un arreglo estructurado
            query = """
                SELECT p.id_pregunta, p.pregunta, 
                       ARRAY_AGG(r.valor) AS opciones
                FROM preguntas p
                LEFT JOIN respuestas r ON p.id_pregunta = r.id_pregunta
                GROUP BY p.id_pregunta, p.pregunta
                ORDER BY p.id_pregunta ASC;
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
            cursor.close()

            # Estructuramos el diccionario para el Agente Interfaz
            formulario = []
            for item in resultados:
                formulario.append({
                    "id_pregunta": item[0],
                    "pregunta": item[1],
                    "opciones": item[2] if item[2] != [None] else []
                })
            return formulario
        except Exception as e:
            print(f"Error en CuestionarioModel: {e}")
            return []
        finally:
            conn.close()