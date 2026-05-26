from models.sbc_model import SBCModel
from models.dispositivo_model import DispositivoModel

class SBCController:
    
    @staticmethod
    def obtener_formulario():
        preguntas_bd = SBCModel.obtener_preguntas()
        return [{"id_pregunta": p["id_pregunta"], "pregunta": p["pregunta"]} for p in preguntas_bd]

    @classmethod
    def _evaluar_condicion_pura(cls, condicion_str: str, memoria: dict) -> bool:
        """
        PARSER LÓGICO DE REGLAS (Sin Hardcoding)
        Evalúa textualmente condiciones complejas divididas por 'and'
        comparando las llaves de la memoria de trabajo.
        """
        # Limpieza básica de la string de la BD
        condicion_limpia = condicion_str.strip().lower()
        sub_condiciones = [c.strip() for c in condicion_limpia.split(" and ")]
        
        resultados_sub = []
        
        for sub in sub_condiciones:
            # Caso 1: Operadores de comparación numérica (>=, <=, >, <)
            if ">=" in sub:
                var, val = sub.split(">=")
                resultados_sub.append(memoria.get(var.strip(), 0) >= float(val.strip()))
            elif "<=" in sub:
                var, val = sub.split("<=")
                resultados_sub.append(memoria.get(var.strip(), 0) <= float(val.strip()))
            elif ">" in sub:
                var, val = sub.split(">")
                resultados_sub.append(memoria.get(var.strip(), 0) > float(val.strip()))
            elif "<" in sub:
                var, val = sub.split("<")
                resultados_sub.append(memoria.get(var.strip(), 0) < float(val.strip()))
            # Caso 2: Operadores de igualdad estricta (=)
            elif "=" in sub:
                var, val = sub.split("=")
                var, val = var.strip(), val.strip()
                # Conversión booleana implícita para valores string en BD
                val_actual = memoria.get(var)
                if val == "true":
                    resultados_sub.append(val_actual is True)
                elif val == "false":
                    resultados_sub.append(val_actual is False)
                else:
                    resultados_sub.append(str(val_actual).lower() == val)
            else:
                # Si es una variable bandera suelta, se asume su estado booleano
                resultados_sub.append(bool(memoria.get(sub, False)))
                
        return all(resultados_sub) if resultados_sub else False

    @classmethod
    def procesar_recomendacion(cls, respuestas_usuario: dict):
        """
        MOTOR DE INFERENCIA ESTRATÉGICO CON ENCADENAMIENTO HACIA ADELANTE (FORWARD CHAINING)
        Ejecuta ciclos reiterativos de combinación hasta que la memoria de trabajo se estabiliza.
        """
        
        # 1. INICIALIZAR MEMORIA DE TRABAJO (Hechos Iniciales)
        memoria_trabajo = {
            "presupuesto": float(respuestas_usuario.get("presupuesto", 0)),
            "gaming": True if respuestas_usuario.get("uso") == "gaming" else False,
            "fotografia": "alta" if respuestas_usuario.get("fotografia") == "muy importante" else "normal",
            "bateria": "alta" if respuestas_usuario.get("bateria") == "sí" else "normal",
            "multitarea": False,
            "estudio": True if respuestas_usuario.get("uso") == "estudio" else False,
            "trabajo": True if respuestas_usuario.get("uso") == "trabajo" else False,
            "almacenamiento": "normal",
            "pantalla": "normal",
            "5g": False,
            "android": True, # Valores base por defecto
            "ios": False
        }

        # Estructura de control para la salida final hacia el hardware
        requisitos_hardware = {
            "presupuesto_max": memoria_trabajo["presupuesto"],
            "benchmark_min": 0,
            "ram_min": 4,
            "requiere_camara": False,
            "requiere_bateria": False
        }

        # 2. CARGAR BASE DE CONOCIMIENTO (Reglas desde Supabase)
        todas_las_reglas = SBCModel.obtener_reglas()
        
        # Set de control para no disparar dos veces la misma regla (Garantiza eficiencia)
        reglas_ya_disparadas = set()
        reglas_explicacion_sbc = []

        # 3. CICLO DE INFERENCIA (Algoritmo de Match-Resolve-Act)
        hay_cambios = True
        ciclos_ejecutados = 0
        
        while hay_cambios and ciclos_ejecutados < 10:  # El límite de 10 evita bucles infinitos por reglas mal formadas
            hay_cambios = False
            ciclos_ejecutados += 1
            
            # RESOLUCIÓN DE CONFLICTOS: Las reglas ya vienen ordenadas por prioridad desde Supabase
            for regla in todas_las_reglas:
                id_regla = regla['id_regla']
                
                if id_regla in reglas_ya_disparadas:
                    continue
                
                # FASE DE MATCH (Emparejamiento)
                if cls._evaluar_condicion_pura(regla['condicion'], memoria_trabajo):
                    
                    # FASE DE ACTUACIÓN (Se dispara la regla)
                    reglas_ya_disparadas.add(id_regla)
                    reglas_explicacion_sbc.append(regla)
                    hay_cambios = True # Hubo un cambio en este ciclo, requiere re-evaluar la agenda
                    
                    # Parsear las acciones del consecuente (resultado) e inyectar nuevos hechos
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

        # 4. TRADUCIR HECHOS DE LA MEMORIA DE TRABAJO A REQUISITOS DE HARDWARE
        # Tras la inferencia, extraemos los hechos técnicos consolidados
        requisitos_hardware["benchmark_min"] = memoria_trabajo.get("benchmark", 0)
        requisitos_hardware["ram_min"] = memoria_trabajo.get("ram", 4)
        if memoria_trabajo.get("camara", 0) >= 50 or memoria_trabajo.get("fotografia") == "alta":
            requisitos_hardware["requiere_camara"] = True
        if memoria_trabajo.get("bateria", 0) >= 5000 or memoria_trabajo.get("bateria") == "alta":
            requisitos_hardware["requiere_bateria"] = True

        # 5. CONSULTAR LAS CONCLUSIONES A LA BASE DE DATOS
        celulares_candidatos = DispositivoModel.buscar_celulares_por_filtros(requisitos_hardware)
        
        # 6. MÓDULO EXPLICADOR (Rastreo del Camino de Razonamiento)
        recomendaciones_finales = []
        for cel in celulares_candidatos:
            explicaciones = [f"Se ajusta al presupuesto asignado de {cel['precio']} Bs."]
            
            # Explicamos basándonos explícitamente en el ID de las reglas que se dispararon en el bucle
            for r in reglas_explicacion_sbc:
                if "gaming" in r['condicion'] and cel['cpu_benchmark'] >= 700000:
                    explicaciones.append(f"Regla #{r['id_regla']} disparada: Al requerir Gaming con presupuesto válido se exige alta tasa de refresco y procesamiento (Benchmark >= 700,000 pts).")
                elif "fotografia" in r['condicion'] and requisitos_hardware["requiere_camara"]:
                    explicaciones.append(f"Regla #{r['id_regla']} disparada: Su perfil requiere fotografía avanzada, activando la búsqueda de sensores superiores a 50 MP.")
                elif "bateria" in r['condicion'] and requisitos_hardware["requiere_bateria"]:
                    explicaciones.append(f"Regla #{r['id_regla']} disparada: Se dedujo una necesidad de autonomía extendida (Batería >= 5,000 mAh).")
            
            justificacion_sbc = " ".join(list(set(explicaciones)))
            
            recomendaciones_finales.append({
                "id_dispositivo": cel["id_dispositivo"],
                "marca": cel["marca"],
                "modelo": cel["modelo"],
                "precio": float(cel["precio"]),
                "moneda": "Bs",
                "explicacion": justificacion_sbc
            })
            
        return recomendaciones_finales