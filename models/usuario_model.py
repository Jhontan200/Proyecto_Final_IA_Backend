# models/usuario_model.py
from config.database import supabase


class UsuarioModel:
    @staticmethod
    def verificar_credenciales(correo: str, contrasena: str):
        try:
            res = (
                supabase.table("usuarios")
                .select("id_usuario, nombre, correo")
                .eq("correo", correo)
                .eq("contrasena", contrasena)
                .execute()
            )
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"Error Login: {e}")
            return None

    @staticmethod
    def registrar_usuario(nombre: str, correo: str, contrasena: str):
        try:
            chk = (
                supabase.table("usuarios")
                .select("id_usuario")
                .eq("correo", correo)
                .execute()
            )
            if chk.data:
                return {"success": False, "message": "El correo ya está registrado."}
            res = (
                supabase.table("usuarios")
                .insert({"nombre": nombre, "correo": correo, "contrasena": contrasena})
                .execute()
            )
            if res.data:
                u = res.data[0]
                return {
                    "success": True,
                    "message": "Usuario registrado con éxito.",
                    "usuario": {
                        "id_usuario": u["id_usuario"],
                        "nombre": u["nombre"],
                        "correo": u["correo"],
                    },
                }
            return {"success": False, "message": "No se pudo crear el usuario."}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    @staticmethod
    def guardar_en_historial(
        id_usuario: int, id_dispositivo: int, puntuacion: int = 95
    ):
        try:
            supabase.table("historial_recomendaciones").insert(
                {
                    "id_usuario": id_usuario,
                    "id_dispositivo": id_dispositivo,
                    "puntuacion": puntuacion,
                }
            ).execute()
            return True
        except Exception as e:
            print(f"Error Historial: {e}")
            return False

    @staticmethod
    def obtener_historial(id_usuario: int):
        """Obtiene el historial mediante consultas desacopladas eludiendo el error de caché PGRST200."""
        try:
            # 1. Obtener los registros de auditoría crudos del usuario activo
            res_historial = (
                supabase.table("historial_recomendaciones")
                .select("id_historial, id_dispositivo, puntuacion, fecha")
                .eq("id_usuario", id_usuario)
                .order("fecha", desc=True)
                .execute()
            )
            if not res_historial.data:
                return []

            # 2. Obtener la lista completa de dispositivos indexados con sus marcas asociadas
            res_disp = (
                supabase.table("dispositivos")
                .select("id_dispositivo, modelo, sistema_operativo, marcas(nombre)")
                .execute()
            )
            mapa_disp = {
                d["id_dispositivo"]: d for d in res_disp.data if d.get("id_dispositivo")
            }

            # 3. Recomponer el árbol relacional exacto que HistoryView.js requiere en el Frontend
            historial_combinado = []
            for item in res_historial.data:
                id_d = item.get("id_dispositivo")
                disp_info = mapa_disp.get(id_d) or {}

                historial_combinado.append(
                    {
                        "id_historial": item["id_historial"],
                        "puntuacion": item["puntuacion"],
                        "fecha": item["fecha"],
                        "id_dispositivo": id_d,
                        "dispositivos": {
                            "modelo": disp_info.get("modelo", "Modelo Desconocido"),
                            "sistema_operativo": disp_info.get(
                                "sistema_operativo", "S/D"
                            ),
                            "marcas": {
                                "nombre": (disp_info.get("marcas") or {}).get("nombre")
                                or "Genérica"
                            },
                        },
                    }
                )
            return historial_combinado
        except Exception as e:
            print(f"Error Obtener Historial: {e}")
            return []
