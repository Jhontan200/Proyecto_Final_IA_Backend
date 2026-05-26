from models.usuario_model import UsuarioModel
from models.cuestionario_model import CuestionarioModel
from models.sbc_model import SBCModel
from models.dispositivo_model import DispositivoModel
from controllers.sbc_controller import SBCController

# =====================================================================
# AGENTE EXPERTO (SBC AGENT)
# =====================================================================
class AgenteExpertoSBC:
    """
    Agente encargado de la Ingeniería del Conocimiento.
    Usa el motor de inferencia con encadenamiento hacia adelante
    para deducir los requerimientos técnicos óptimos.
    """
    def __init__(self):
        self.nombre = "Agente_Experto_SBC"

    def evaluar_necesidades_tecnicas(self, hechos_iniciales: dict):
        print(f"[{self.nombre}]: Iniciando ciclo de inferencia y emparejamiento de reglas...")
        
        # Reutilizamos el motor puro y dinámico con la memoria de trabajo
        todas_las_reglas = SBCModel.obtener_reglas()
        
        memoria_trabajo = {
            "presupuesto": float(hechos_iniciales.get("presupuesto", 0)),
            "gaming": True if hechos_iniciales.get("uso") == "gaming" else False,
            "fotografia": "alta" if hechos_iniciales.get("fotografia") == "muy importante" else "normal",
            "bateria": "alta" if hechos_iniciales.get("bateria") == "sí" else "normal",
            "multitarea": True if hechos_iniciales.get("multitarea") == "sí" else False,
            "estudio": True if hechos_iniciales.get("uso") == "estudio" else False,
            "trabajo": True if hechos_iniciales.get("uso") == "trabajo" else False,
            "almacenamiento": "alto" if hechos_iniciales.get("almacenamiento") == "alto" else "normal",
            "pantalla": "grande" if hechos_iniciales.get("pantalla") == "grande" else "normal",
            # Soporta tanto el alias '5g' del JSON del Frontend como la propiedad interna de Pydantic
            "5g": True if hechos_iniciales.get("5g") == "sí" or hechos_iniciales.get("red_5g") == "sí" else False,
            "android": True,
            "ios": False
        }

        requisitos_hardware = {
            "presupuesto_max": memoria_trabajo["presupuesto"],
            "benchmark_min": 0,
            "ram_min": 4,
            "requiere_camara": False,
            "requiere_bateria": False
        }

        reglas_ya_disparadas = set()
        reglas_explicacion_sbc = []
        hay_cambios = True
        ciclos = 0
        
        # Algoritmo de Match-Resolve-Act iterativo (Forward Chaining)
        while hay_cambios and ciclos < 12:
            hay_cambios = False
            ciclos += 1
            for regla in todas_las_reglas:
                if regla['id_regla'] in reglas_ya_disparadas:
                    continue
                
                # Evaluación usando el parser matemático abstracto
                if SBCController._evaluar_condicion_pura(regla['condicion'], memoria_trabajo):
                    reglas_ya_disparadas.add(regla['id_regla'])
                    reglas_explicacion_sbc.append(regla)
                    hay_cambios = True
                    
                    # Ejecución del consecuente (Actuación)
                    acciones = [a.strip() for a in regla['resultado'].lower().split(" and ")]
                    for accion in acciones:
                        if ">=" in accion:
                            var, val = accion.split(">=")
                            memoria_trabajo[var.strip()] = float(val.strip())
                        elif "<" in accion:
                            var, val = accion.split("<")
                            memoria_trabajo[var.strip()] = float(val.strip())
                        elif "=" in accion:
                            var, val = accion.split("=")
                            var, val = var.strip(), val.strip()
                            memoria_trabajo[var] = True if val == "true" else (False if val == "false" else val)

        # Consolidación de hechos técnicos deducidos
        requisitos_hardware["benchmark_min"] = memoria_trabajo.get("benchmark", 0)
        requisitos_hardware["ram_min"] = memoria_trabajo.get("ram", 4)
        if memoria_trabajo.get("camara", 0) >= 50 or memoria_trabajo.get("fotografia") == "alta":
            requisitos_hardware["requiere_camara"] = True
        if memoria_trabajo.get("bateria", 0) >= 5000 or memoria_trabajo.get("bateria") == "alta":
            requisitos_hardware["requiere_bateria"] = True

        print(f"[{self.nombre}]: Inferencia completada en {ciclos} ciclos. Requisitos deducidos: {requisitos_hardware}")
        return requisitos_hardware, reglas_explicacion_sbc


# =====================================================================
# AGENTE BROKER COMERCIAL (BROKER AGENT)
# =====================================================================
class AgenteBrokerTiendas:
    """
    Agente encargado del análisis económico del mercado.
    Cruza los requisitos de hardware con el catálogo global y optimiza
    los resultados seleccionando las mejores ofertas comerciales.
    """
    def __init__(self):
        self.nombre = "Agente_Broker_Comercial"

    def optimizar_catalogo_y_precios(self, requisitos_hardware: dict, reglas_disparadas: list):
        print(f"[{self.nombre}]: Extrayendo dispositivos aptos y analizando competitividad de tiendas...")
        
        # Obtenemos los dispositivos crudos aplicando filtros avanzados desde la BD (8 tablas combinadas)
        dispositivos_candidatos = DispositivoModel.buscar_dispositivos_sbc_avanzado(requisitos_hardware)
        
        recomendaciones_finales = []
        
        for cel in dispositivos_candidatos:
            explicaciones = [f"Cumple con tu presupuesto asignado en {cel['tienda']} ({cel['precio']} Bs)."]
            
            # El agente construye de forma proactiva la traza lógica usando la explicación de la BD
            for r in reglas_disparadas:
                if "gaming" in r['condicion'] and cel['cpu_benchmark'] >= 700000:
                    explicaciones.append(f"Regla #{r['id_regla']} ejecutada: Perfil Gaming detectado. Se requiere un SoC de alto rendimiento con GPU certificada ({cel['gpu']}) y potencia Antutu de {cel['antutu']} pts.")
                elif "fotografia" in r['condicion'] and requisitos_hardware["requiere_camara"]:
                    explicaciones.append(f"Regla #{r['id_regla']} ejecutada: Exigencia fotográfica detectada. Filtro de hardware activado para sensores superiores a 50 MP.")
                elif "bateria" in r['condicion'] and requisitos_hardware["requiere_bateria"]:
                    explicaciones.append(f"Regla #{r['id_regla']} ejecutada: Necesidad de autonomía móvil crítica. Exigiendo baterías de alta densidad (>= 5000 mAh).")
            
            recomendaciones_finales.append({
                "id_dispositivo": cel["id_dispositivo"],
                "marca": cel["marca"],
                "modelo": cel["modelo"],
                "precio": cel["precio"],
                "tienda": cel["tienda"],
                "tienda_url": cel["tienda_url"],
                "detalles_tecnicos": f"Procesador: {cel['cpu']} ({cel['cpu_gama']}) | RAM: {cel['ram']}GB | Almacenamiento: {cel['almacenamiento']}GB | OS: {cel['sistema_operativo']}",
                "explicacion": " ".join(list(set(explicaciones)))
            })

        # Ordenar del más barato al más caro y retornar solo el top 3 óptimo
        recomendaciones_optimizadas = sorted(recomendaciones_finales, key=lambda x: x['precio'])
        return recomendaciones_optimizadas[:3]


# =====================================================================
# AGENTE INTERFAZ COORDINADOR (INTERFACE AGENT)
# =====================================================================
class AgenteInterfazCoordinador:
    """
    Agente de cara al usuario.
    Maneja la autenticación, la carga del formulario interactivo,
    la comunicación entre sub-agentes y el registro del historial.
    """
    def __init__(self):
        self.nombre = "Agente_Interfaz_Coordinador"
        self.agente_experto = AgenteExpertoSBC()
        self.agente_broker = AgenteBrokerTiendas()

    def procesar_login(self, correo: str, contrasena: str):
        print(f"[{self.nombre}]: Procesando solicitud de acceso para {correo}...")
        usuario = UsuarioModel.verificar_credenciales(correo, contrasena)
        if usuario:
            print(f"[{self.nombre}]: Acceso concedido a {usuario['nombre']}.")
            return {"success": True, "usuario": usuario}
        print(f"[{self.nombre}]: Credenciales inválidas.")
        return {"success": False, "message": "Correo o contraseña incorrectos."}

    def procesar_registro(self, nombre: str, correo: str, contrasena: str):
        """Coordinación del registro delegando la persistencia en el modelo correspondiente"""
        print(f"[{self.nombre}]: Coordinando el registro de un nuevo usuario: {nombre} ({correo})...")
        resultado = UsuarioModel.registrar_usuario(nombre, correo, contrasena)
        return resultado

    def generar_cuestionario_dinamico(self):
        print(f"[{self.nombre}]: Extrayendo el árbol de preguntas y opciones desde Supabase...")
        preguntas = CuestionarioModel.obtener_preguntas_con_respuestas()
        return {"success": True, "preguntas": preguntas}

    def ejecutar_ciclo_sbc_hibrido(self, respuestas_usuario: dict, id_usuario: int = None):
        print(f"[{self.nombre}]: Iniciando sesión consultiva multiagente...")
        
        # 1. El Agente Interfaz le envía la Memoria de Trabajo Inicial al Agente Experto
        requisitos_hardware, reglas_disparadas = self.agente_experto.evaluar_necesidades_tecnicas(respuestas_usuario)
        
        # 2. El Agente Interfaz comunica los requisitos técnicos deducidos al Agente Broker
        top_recomendaciones = self.agente_broker.optimizar_catalogo_y_precios(requisitos_hardware, reglas_disparadas)
        
        # 3. Persistencia de Auditoría: Si hay un usuario logueado, registramos en la BD de Supabase
        if id_usuario and top_recomendaciones:
            id_ganador = top_recomendaciones[0]["id_dispositivo"]
            print(f"[{self.nombre}]: Registrando recomendación del dispositivo ID {id_ganador} para el usuario {id_usuario} en el Historial...")
            UsuarioModel.guardar_en_historial(id_usuario, id_ganador, puntuacion=95)
            
        print(f"[{self.nombre}]: Flujo SMA finalizado con éxito.")
        return {"success": True, "recomendaciones": top_recomendaciones}