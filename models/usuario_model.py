# models/usuario_model.py
from config.database import supabase  # <-- Importamos el cliente unificado de Supabase

class UsuarioModel:
    @staticmethod
    def verificar_credenciales(correo: str, contrasena: str):
        """Valida el inicio de sesión contra la tabla 'usuarios'"""
        try:
            # Filtramos usando .eq() para emular el WHERE correo = %s AND contrasena = %s
            respuesta = (
                supabase.table("usuarios")
                .select("id_usuario, nombre, correo")
                .eq("correo", correo)
                .eq("contrasena", contrasena)
                .execute()
            )
            
            usuarios = respuesta.data
            
            # Si la lista contiene al menos un elemento, las credenciales son válidas
            if usuarios:
                usuario = usuarios[0]
                return {
                    "id_usuario": usuario["id_usuario"],
                    "nombre": usuario["nombre"],
                    "correo": usuario["correo"]
                }
            return None
        except Exception as e:
            print(f"Error en UsuarioModel (Login): {e}")
            return None

    @staticmethod
    def registrar_usuario(nombre: str, correo: str, contrasena: str):
        """Inserta un nuevo usuario respetando estrictamente las columnas de la base de datos"""
        try:
            # 1. Verificar si el correo ya existe para evitar duplicados accidentales
            chequeo_existe = (
                supabase.table("usuarios")
                .select("id_usuario")
                .eq("correo", correo)
                .execute()
            )
            
            if chequeo_existe.data:
                return {"success": False, "message": "El correo electrónico ya está registrado."}
            
            # 2. Insertar el nuevo usuario. Envías un diccionario con las columnas y valores.
            nuevo_registro = {
                "nombre": nombre,
                "correo": correo,
                "contrasena": contrasena
            }
            
            respuesta_insert = (
                supabase.table("usuarios")
                .insert(nuevo_registro)
                .execute()
            )
            
            nuevo_usuario_lista = respuesta_insert.data
            
            if nuevo_usuario_lista:
                usuario_creado = nuevo_usuario_lista[0]
                return {
                    "success": True,
                    "message": "Usuario registrado con éxito.",
                    "usuario": {
                        "id_usuario": usuario_creado["id_usuario"],
                        "nombre": usuario_creado["nombre"],
                        "correo": usuario_creado["correo"]
                    }
                }
            return {"success": False, "message": "No se pudo crear el usuario."}
            
        except Exception as e:
            print(f"Error en UsuarioModel (Registro): {e}")
            return {"success": False, "message": f"Error en el servidor: {str(e)}"}

    @staticmethod
    def guardar_en_historial(id_usuario: int, id_dispositivo: int, puntuacion: int = 95):
        """Registra la auditoría de la recomendación exitosa en 'historial_recomendaciones'"""
        try:
            # Construimos el diccionario con la data del historial
            datos_historial = {
                "id_usuario": id_usuario,
                "id_dispositivo": id_dispositivo,
                "puntuacion": puntuacion
            }
            
            # Ejecutamos la inserción simple
            supabase.table("historial_recomendaciones").insert(datos_historial).execute()
            return True
            
        except Exception as e:
            print(f"Error en UsuarioModel (Historial): {e}")
            return False
        # Nota: Los bloques 'finally' y 'conn.close()' desaparecen por completo de todo el archivo