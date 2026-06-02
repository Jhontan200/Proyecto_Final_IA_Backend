# controllers/sma_controller.py
from models.usuario_model import UsuarioModel
from models.cuestionario_model import CuestionarioModel
from models.sbc_model import SBCModel
from models.dispositivo_model import DispositivoModel
from controllers.sbc_controller import SBCController


class AgenteExpertoSBC:
    def __init__(self):
        self.nombre = "Agente_Experto_SBC"

    def evaluar_necesidades_tecnicas(self, hechos_iniciales: dict):
        print(f"[{self.nombre}]: Iniciando inferencia y emparejamiento de reglas...")
        todas_las_reglas = SBCModel.obtener_reglas()
        pref_os = hechos_iniciales.get("sistema_operativo", "android").lower()

        memoria_trabajo = {
            "presupuesto": float(hechos_iniciales.get("presupuesto", 0)),
            "gaming": hechos_iniciales.get("uso") == "gaming",
            "fotografia": hechos_iniciales.get("fotografia", "normal"),
            "bateria_perfil": "alta"
            if hechos_iniciales.get("bateria") == "sí"
            else "normal",
            "multitarea": hechos_iniciales.get("multitarea") == "sí",
            "estudio": hechos_iniciales.get("uso") == "estudio",
            "trabajo": hechos_iniciales.get("uso") == "trabajo",
            "carga": True,
            "almacenamiento": "alto"
            if hechos_iniciales.get("almacenamiento") == "alto"
            else "normal",
            "pantalla": "grande"
            if hechos_iniciales.get("pantalla") == "grande"
            else "normal",
            "5g": hechos_iniciales.get("5g") == "sí",
            "android": pref_os == "android",
            "ios": pref_os == "ios",
        }

        reglas_disparadas, condiciones_explicacion = set(), []
        hay_cambios, ciclos = True, 0

        while hay_cambios and ciclos < 12:
            hay_cambios = False
            ciclos += 1
            for r in todas_las_reglas:
                if r.get("id_regla") in reglas_disparadas:
                    continue
                if SBCController._evaluar_condicion_pura(
                    r.get("condicion", ""), memoria_trabajo
                ):
                    reglas_disparadas.add(r.get("id_regla"))
                    condiciones_explicacion.append(r)
                    hay_cambios = True
                    for accion in [
                        a.strip() for a in r.get("resultado", "").lower().split(" and ")
                    ]:
                        if ">=" in accion:
                            var, val = accion.split(">=")
                            memoria_trabajo[var.strip()] = float(val.strip())
                        elif "<" in accion:
                            var, val = accion.split("<")
                            memoria_trabajo[var.strip()] = float(val.strip())
                        elif "=" in accion:
                            var, val = accion.split("=")
                            var, val = var.strip(), val.strip()
                            if val in ["true", "false"]:
                                memoria_trabajo[var] = val == "true"
                            else:
                                memoria_trabajo[var] = (
                                    float(val)
                                    if val.replace(".", "", 1).isdigit()
                                    else val
                                )

            requisitos_hardware = {
                "presupuesto_max": memoria_trabajo["presupuesto"],
                "benchmark_min": memoria_trabajo.get("benchmark", 0),
                "ram_min": memoria_trabajo.get("ram", 4),
                "sistema_operativo": pref_os,
                "almacenamiento": memoria_trabajo.get("almacenamiento"),
                "pantalla": memoria_trabajo.get("pantalla"),
            }
            return requisitos_hardware, condiciones_explicacion


class AgenteBrokerTiendas:
    def __init__(self):
        self.nombre = "Agente_Broker_Comercial"

    def optimizar_catalogo_y_precios(
        self, requisitos_hardware: dict, reglas_disparadas: list
    ):
        dispositivos = DispositivoModel.buscar_dispositivos_sbc_avanzado(
            requisitos_hardware
        )
        recomendaciones_finales = []

        for cel in dispositivos:
            tienda = cel.get("tienda") or "General"
            explicaciones = [
                f"Se ajusta al presupuesto en {tienda} ({cel.get('precio', 0)} Bs)."
            ]
            for r in reglas_disparadas:
                c = r.get("condicion", "")
                if "gaming" in c and cel.get("cpu_benchmark", 0) >= 450000:
                    explicaciones.append(
                        f"Regla #{r.get('id_regla')}: Optimización de rendimiento para videojuegos."
                    )
                elif "fotografia" in c:
                    explicaciones.append(
                        f"Regla #{r.get('id_regla')}: Activación de sensores fotográficos de alta resolución."
                    )
                elif "ios" in c:
                    explicaciones.append(
                        f"Regla #{r.get('id_regla')}: Filtrado estricto del ecosistema Apple."
                    )

            recomendaciones_finales.append(
                {
                    "id_dispositivo": cel.get("id_dispositivo"),
                    "marca": cel.get("marca"),
                    "modelo": cel.get("modelo"),
                    "precio": cel.get("precio", 0.0),
                    "tienda": tienda,
                    "tienda_url": cel.get("tienda_url") or "#",
                    "detalles_tecnicos": f"Procesador: {cel.get('cpu')} ({cel.get('cpu_gama')}) | RAM: {cel.get('ram')}GB | ROM: {cel.get('almacenamiento')}GB | OS: {cel.get('sistema_operativo')}",
                    "explicacion": " ".join(list(set(explicaciones))),
                }
            )
        return recomendaciones_finales[:3]


class AgenteInterfazCoordinador:
    def __init__(self):
        self.nombre, self.agente_experto, self.agente_broker = (
            "Agente_Interfaz_Coordinador",
            AgenteExpertoSBC(),
            AgenteBrokerTiendas(),
        )

    def procesar_login(self, correo, contrasena):
        u = UsuarioModel.verificar_credenciales(correo, contrasena)
        return (
            {"success": True, "usuario": u}
            if u
            else {"success": False, "message": "Credenciales inválidas."}
        )

    def procesar_registro(self, n, c, p):
        return UsuarioModel.registrar_usuario(n, c, p)

    def generar_cuestionario_dinamico(self):
        return {
            "success": True,
            "preguntas": CuestionarioModel.obtener_preguntas_con_respuestas(),
        }

    def ejecutar_ciclo_sbc_hibrido(self, respuestas, id_u=None):
        reqs, reglas = self.agente_experto.evaluar_necesidades_tecnicas(respuestas)
        top = self.agente_broker.optimizar_catalogo_y_precios(reqs, reglas)
        if id_u and top and top[0].get("id_dispositivo"):
            UsuarioModel.guardar_en_historial(id_u, top[0].get("id_dispositivo"), 95)
        return {"success": True, "recomendaciones": top}

    def obtener_historial_usuario(self, id_usuario):
        return UsuarioModel.obtener_historial(id_usuario)
