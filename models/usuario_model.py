from config.database import get_db_connection

class UsuarioModel:
    @staticmethod
    def verificar_credenciales(correo: str, contrasena: str):
        """Valida el inicio de sesión contra la tabla 'usuarios'"""
        conn = get_db_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            query = """
                SELECT id_usuario, nombre, correo 
                FROM usuarios 
                WHERE correo = %s AND contrasena = %s;
            """
            cursor.execute(query, (correo, contrasena))
            usuario = cursor.fetchone()
            cursor.close()
            
            if usuario:
                return {
                    "id_usuario": usuario[0],
                    "nombre": usuario[1],
                    "correo": usuario[2]
                }
            return None
        except Exception as e:
            print(f"Error en UsuarioModel (Login): {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def registrar_usuario(nombre: str, correo: str, contrasena: str):
        """Inserta un nuevo usuario respetando estrictamente las columnas del script SQL"""
        conn = get_db_connection()
        if not conn:
            return {"success": False, "message": "Error de conexión con la base de datos."}
        try:
            cursor = conn.cursor()
            
            # 1. Verificar si el correo ya existe para evitar duplicados accidentales
            query_existe = "SELECT id_usuario FROM usuarios WHERE correo = %s;"
            cursor.execute(query_existe, (correo,))
            if cursor.fetchone():
                cursor.close()
                return {"success": False, "message": "El correo electrónico ya está registrado."}
            
            # 2. Insertar el nuevo usuario con tus columnas reales (id_usuario se genera solo)
            query_insert = """
                INSERT INTO usuarios (nombre, correo, contrasena)
                VALUES (%s, %s, %s)
                RETURNING id_usuario, nombre, correo;
            """
            cursor.execute(query_insert, (nombre, correo, contrasena))
            nuevo_usuario = cursor.fetchone()
            conn.commit()
            cursor.close()
            
            if nuevo_usuario:
                return {
                    "success": True,
                    "message": "Usuario registrado con éxito.",
                    "usuario": {
                        "id_usuario": nuevo_usuario[0],
                        "nombre": nuevo_usuario[1],
                        "correo": nuevo_usuario[2]
                    }
                }
            return {"success": False, "message": "No se pudo crear el usuario."}
        except Exception as e:
            print(f"Error en UsuarioModel (Registro): {e}")
            return {"success": False, "message": f"Error en el servidor: {str(e)}"}
        finally:
            conn.close()

    @staticmethod
    def guardar_en_historial(id_usuario: int, id_dispositivo: int, puntuacion: int = 95):
        """Registra la auditoría de la recomendación exitosa en 'historial_recomendaciones'"""
        conn = get_db_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            # Corregido: 'historial_recommendaciones' corregido a 'historial_recomendaciones' (con una sola m)
            query = """
                INSERT INTO historial_recomendaciones (id_usuario, id_dispositivo, puntuacion)
                VALUES (%s, %s, %s);
            """
            cursor.execute(query, (id_usuario, id_dispositivo, puntuacion))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error en UsuarioModel (Historial): {e}")
            return False
        finally:
            conn.close()