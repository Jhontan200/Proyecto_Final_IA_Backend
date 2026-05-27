# models/dispositivo_model.py
from config.database import supabase  # <-- Importamos tu cliente unificado

class DispositivoModel:
    @staticmethod
    def buscar_dispositivos_sbc_avanzado(requisitos_hardware: dict):
        """
        CONSUllTA MAESTRA DE RENDIMIENTO Y TIENDAS
        Filtra y cruza: dispositivos, categorias, marcas, procesadores, gpu, benchmarks, tiendas y precios.
        """
        try:
            # 1. Definimos la estructura del JOIN masivo de forma declarativa.
            # Supabase mapea las relaciones basándose en tus Foreign Keys.
            select_query = """
                id_dispositivo,
                modelo,
                ram,
                almacenamiento,
                sistema_operativo,
                marcas(nombre),
                categorias(id_categoria),
                procesadores(nombre, benchmark, gama),
                gpu(nombre),
                benchmarks(antutu),
                precios(precio, tiendas(nombre, url))
            """
            
            # Iniciamos la consulta base apuntando a la tabla principal
            query = supabase.table("dispositivos").select(select_query)
            
            # Filtro estático inicial: Limitado a Celulares (id_categoria = 1)
            query = query.eq("id_categoria", 1)

            # 2. Restricciones Dinámicas Básicas
            if "ram_min" in requisitos_hardware and requisitos_hardware["ram_min"] > 0:
                query = query.gte("ram", requisitos_hardware["ram_min"])

            if "benchmark_min" in requisitos_hardware and requisitos_hardware["benchmark_min"] > 0:
                # Para filtrar por tablas relacionadas usamos la sintaxis 'tabla.columna'
                query = query.gte("procesadores.benchmark", requisitos_hardware["benchmark_min"])

            if "presupuesto_max" in requisitos_hardware:
                query = query.lte("precios.precio", requisitos_hardware["presupuesto_max"])

            # 3. Ordenación por rendimiento bruto (Benchmarks) y economía
            # Nota: Supabase API ordena de manera principal y secundaria usando comas
            query = query.order("id_cpu->benchmark", ascending=False).order("precios->precio", ascending=True)

            # Ejecutamos la consulta en Supabase
            respuesta = query.execute()
            datos_raw = respuesta.data
            
            dispositivos_procesados = []
            
            # 4. Post-procesamiento y aplanado del JSON (Emulando la salida exacta que esperan tus Agentes)
            for item in datos_raw:
                
                # Extraemos la información de los nodos relacionales (evitando KeyErrors con .get)
                marca_info = item.get("marcas") or {}
                cpu_info = item.get("procesadores") or {}
                gpu_info = item.get("gpu") or {}
                bench_info = item.get("benchmarks") or {}
                
                # 'precios' y 'tiendas' pueden devolver listas o diccionarios dependiendo de tu cardinalidad. 
                # Asumiendo estructura estándar:
                lista_precios = item.get("precios") or []
                precio_info = lista_precios[0] if isinstance(lista_precios, list) and len(lista_precios) > 0 else (lista_precios or {})
                tienda_info = precio_info.get("tiendas") or {}

                # --- FILTROS AVANZADOS EN MEMORIA (Para resolver el SPLIT_PART complejo) ---
                # Nota: Si manejas miles de registros, lo ideal sería migrar esto a una función RPC en Postgres.
                # Para volumen escolar/académico, este filtrado en el ciclo es rápido y seguro.
                
                if requisitos_hardware.get("requiere_bateria"):
                    # Aquí tendrías que evaluar si el dispositivo cumple con la condición de la batería.
                    # Como la API no trae dispositivo_caracteristicas a menos que lo pidas, si usas mucho este filtro,
                    # lo óptimo es agregar la columna 'bateria_mah' directa a la tabla dispositivos.
                    pass 

                dispositivos_procesados.append({
                    "id_dispositivo": item["id_dispositivo"],
                    "marca": marca_info.get("nombre"),
                    "modelo": item["modelo"],
                    "precio": float(precio_info.get("precio")) if precio_info.get("precio") else 0.0,
                    "tienda": tienda_info.get("nombre"),
                    "tienda_url": tienda_info.get("url"),
                    "cpu": cpu_info.get("nombre"),
                    "cpu_benchmark": cpu_info.get("benchmark"),
                    "cpu_gama": cpu_info.get("gama"),
                    "gpu": gpu_info.get("nombre") if gpu_info.get("nombre") else "Integrada",
                    "antutu": bench_info.get("antutu"),
                    "ram": item["ram"],
                    "almacenamiento": item["almacenamiento"],
                    "sistema_operativo": item["sistema_operativo"]
                })

            return dispositivos_procesados

        except Exception as e:
            print(f"Error en el Modelo de Dispositivos Extendido con Supabase API: {e}")
            return []