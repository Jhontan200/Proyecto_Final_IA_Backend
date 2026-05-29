# models/dispositivo_model.py
from config.database import supabase


class DispositivoModel:
    @staticmethod
    def buscar_dispositivos_sbc_avanzado(requisitos_hardware: dict):
        """Filtra dispositivos usando degradación progresiva de restricciones para garantizar resultados."""
        try:
            # 1. Consultas desacopladas independientes para eludir la falta de FKs relacionales
            res_disp = (
                supabase.table("dispositivos")
                .select("""
                id_dispositivo, modelo, ram, almacenamiento, sistema_operativo,
                marcas(nombre), categorias(id_categoria), procesadores(nombre, benchmark, gama), gpu(nombre)
            """)
                .eq("id_categoria", 1)
                .execute()
            )

            res_precios = (
                supabase.table("precios")
                .select("id_dispositivo, precio, tiendas(nombre, url)")
                .execute()
            )
            mapa_precios = {
                p["id_dispositivo"]: p
                for p in res_precios.data
                if p.get("id_dispositivo")
            }

            valores_existentes = [
                float(p["precio"]) for p in res_precios.data if p.get("precio")
            ]
            min_precio_stock = min(valores_existentes) if valores_existentes else 0.0

            p_max = float(requisitos_hardware.get("presupuesto_max", 0))
            b_min = float(requisitos_hardware.get("benchmark_min", 0))
            ram_min = float(requisitos_hardware.get("ram_min", 4))

            # Calibración comercial: Si el presupuesto es inferior al stock real, ajustamos al mínimo
            if p_max > 0 and p_max < min_precio_stock:
                p_max = min_precio_stock + 300

            # Motor de degradación de 4 niveles: Soluciona la asimetría de raíz
            for nivel in ["estricto", "relajado_cpu", "tolerante_ram", "libre"]:
                dispositivos_processed = []
                for item in res_disp.data:
                    id_disp = item["id_dispositivo"]
                    precio_info = mapa_precios.get(id_disp, {})
                    precio_val = (
                        float(precio_info.get("precio"))
                        if precio_info.get("precio")
                        else 0.0
                    )

                    # Filtro de presupuesto (se libera en modo de emergencia si todo falla)
                    if nivel != "libre" and p_max > 0 and precio_val > p_max:
                        continue

                    # Filtro de memoria RAM base
                    if nivel in ["estricto", "relajado_cpu"] and ram_min > 0:
                        if float(item.get("ram", 0)) < ram_min:
                            continue

                    cpu_info = item.get("procesadores") or {}
                    bench_val = float(cpu_info.get("benchmark", 0))

                    # Filtro de potencia bruta de CPU deducida por la IA
                    if nivel == "estricto" and b_min > 0 and bench_val < b_min:
                        continue

                    dispositivos_processed.append(
                        {
                            "id_dispositivo": id_disp,
                            "marca": (item.get("marcas") or {}).get("nombre")
                            or "Genérica",
                            "modelo": item["modelo"],
                            "precio": precio_val,
                            "tienda": (precio_info.get("tiendas") or {}).get("nombre")
                            or "Tienda Central",
                            "tienda_url": (precio_info.get("tiendas") or {}).get("url")
                            or "#",
                            "cpu": cpu_info.get("nombre") or "S/D",
                            "cpu_benchmark": bench_val,
                            "cpu_gama": cpu_info.get("gama") or "Media",
                            "gpu": (item.get("gpu") or {}).get("nombre") or "Integrada",
                            "antutu": bench_val,
                            "ram": item["ram"],
                            "almacenamiento": item["almacenamiento"],
                            "sistema_operativo": item["sistema_operativo"],
                        }
                    )
                if dispositivos_processed:
                    break

            # Clasificación comercial premium: El mejor rendimiento disponible para tu bolsillo
            dispositivos_processed.sort(
                key=lambda x: (-x["cpu_benchmark"], x["precio"])
            )
            return dispositivos_processed

        except Exception as e:
            print(f"❌ Error crítico en el Modelo de Dispositivos: {e}")
            return []
