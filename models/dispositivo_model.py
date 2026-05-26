from config.database import get_db_connection

class DispositivoModel:
    @staticmethod
    def buscar_dispositivos_sbc_avanzado(requisitos_hardware: dict):
        """
        CONSULTA MAESTRA DE RENDIMIENTO Y TIENDAS
        Filtra y cruza: dispositivos, categorias, marcas, procesadores, gpu, benchmarks, tiendas y precios.
        """
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            # Consulta relacional masiva para procesar los requisitos técnicos y comerciales
            query = """
                SELECT DISTINCT 
                    d.id_dispositivo, 
                    m.nombre AS marca, 
                    d.modelo, 
                    p.precio, 
                    t.nombre AS tienda,
                    t.url AS tienda_url,
                    proc.nombre AS cpu_nombre,
                    proc.benchmark AS cpu_benchmark,
                    proc.gama AS cpu_gama,
                    g.nombre AS gpu_nombre,
                    b.antutu AS antutu_score,
                    d.ram,
                    d.almacenamiento,
                    d.sistema_operativo
                FROM dispositivos d
                JOIN marcas m ON d.id_marca = m.id_marca
                JOIN categorias c ON d.id_categoria = c.id_categoria
                LEFT JOIN procesadores proc ON d.id_cpu = proc.id_cpu
                LEFT JOIN gpu g ON d.id_gpu = g.id_gpu
                LEFT JOIN benchmarks b ON proc.id_cpu = b.id_cpu
                LEFT JOIN precios p ON d.id_dispositivo = p.id_dispositivo
                LEFT JOIN tiendas t ON p.id_tienda = t.id_tienda
                WHERE c.id_categoria = 1 -- Limitado inicialmente a Celulares
            """
            params = []

            # Restricción Dinámica de Presupuesto Máximo
            if "presupuesto_max" in requisitos_hardware:
                query += " AND p.precio <= %s"
                params.append(requisitos_hardware["presupuesto_max"])
                
            # Restricciones de Potencia de Hardware deducidas por el Motor
            if "benchmark_min" in requisitos_hardware and requisitos_hardware["benchmark_min"] > 0:
                query += " AND proc.benchmark >= %s"
                params.append(requisitos_hardware["benchmark_min"])

            if "ram_min" in requisitos_hardware and requisitos_hardware["ram_min"] > 0:
                query += " AND d.ram >= %s"
                params.append(requisitos_hardware["ram_min"])

            # Filtros Avanzados sobre la tabla dispositivo_caracteristicas
            if requisitos_hardware.get("requiere_bateria"):
                query += """ AND d.id_dispositivo IN (
                    SELECT id_dispositivo FROM dispositivo_caracteristicas 
                    WHERE id_caracteristica = 1 AND CAST(SPLIT_PART(valor, ' ', 1) AS INTEGER) >= 5000
                )"""

            if requisitos_hardware.get("requiere_camara"):
                query += """ AND d.id_dispositivo IN (
                    SELECT id_dispositivo FROM dispositivo_caracteristicas 
                    WHERE id_caracteristica = 3 AND CAST(SPLIT_PART(valor, ' ', 1) AS INTEGER) >= 50
                )"""

            # Ordenación por rendimiento bruto (Benchmarks) y economía de Tiendas
            query += " ORDER BY proc.benchmark DESC, p.precio ASC;"
            
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            cursor.close()
            
            # Estructuramos la respuesta en un diccionario limpio para el procesamiento de los Agentes
            dispositivos_procesados = []
            for row in resultados:
                dispositivos_procesados.append({
                    "id_dispositivo": row[0],
                    "marca": row[1],
                    "modelo": row[2],
                    "precio": float(row[3]) if row[3] else 0.0,
                    "tienda": row[4],
                    "tienda_url": row[5],
                    "cpu": row[6],
                    "cpu_benchmark": row[7],
                    "cpu_gama": row[8],
                    "gpu": row[9] if row[9] else "Integrada",
                    "antutu": row[10],
                    "ram": row[11],
                    "almacenamiento": row[12],
                    "sistema_operativo": row[13]
                })
                
            return dispositivos_procesados
            
        except Exception as e:
            print(f"Error en el Modelo de Dispositivos Extendido: {e}")
            return []
        finally:
            conn.close()