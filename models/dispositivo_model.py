# models/dispositivo_model.py
from config.database import supabase


class DispositivoModel:
    @staticmethod
    def buscar_dispositivos_sbc_avanzado(requisitos_hardware: dict):
        """Filtra dispositivos adaptando categorías y aplicando degradación elástica de hardware."""
        try:
            # Detección dinámica de categoría (Celular = 1 vs Tablet = 3) basado en hechos de almacenamiento/pantalla
            p_rom = str(requisitos_hardware.get("almacenamiento"))
            p_screen = str(requisitos_hardware.get("pantalla"))
            id_cat = (
                3
                if ("256" in p_rom or "512" in p_rom or "alto" in p_rom)
                and "grande" in p_screen
                else 1
            )

            res_disp = (
                supabase.table("dispositivos")
                .select("""
                id_dispositivo, modelo, ram, almacenamiento, sistema_operativo,
                marcas(nombre), categorias(id_categoria), procesadores(nombre, benchmark, gama), gpu(nombre)
            """)
                .eq("id_categoria", id_cat)
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
            pref_os = requisitos_hardware.get("sistema_operativo", "android")

            if p_max > 0 and p_max < min_precio_stock:
                p_max = min_precio_stock + 300

            # Cuatro capas de relajación elástica para resolver la contradicción de hardware de raíz
            for nivel in ["estricto", "relajado_cpu", "tolerante_ram", "libre"]:
                dispositivos_processed = []
                modelos_vistos = set()

                for item in res_disp.data:
                    id_disp = item["id_dispositivo"]
                    modelo_normalizado = str(item["modelo"]).strip().lower()
                    if modelo_normalizado in modelos_vistos:
                        continue

                    precio_info = mapa_precios.get(id_disp, {})
                    precio_val = (
                        float(precio_info.get("precio"))
                        if precio_info.get("precio")
                        else 0.0
                    )

                    # FILTRO DE ECOSISTEMA: Inquebrantable
                    db_os = str(item.get("sistema_operativo", "")).lower()
                    if pref_os == "ios" and "ios" not in db_os:
                        continue
                    if pref_os == "android" and "ios" in db_os:
                        continue

                    # Degradación progresiva por niveles de exigencia de la IA
                    if nivel != "libre" and p_max > 0 and precio_val > p_max:
                        continue
                    if (
                        nivel in ["estricto", "relajado_cpu"]
                        and ram_min > 0
                        and float(item.get("ram", 0)) < ram_min
                    ):
                        continue

                    cpu_info = item.get("procesadores") or {}
                    bench_val = float(cpu_info.get("benchmark", 0))
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
                    modelos_vistos.add(modelo_normalizado)

                # CORRECCIÓN: Si encontramos teléfonos aptos en este nivel, los devolvemos sin romper prematuramente las opciones
                if dispositivos_processed:
                    break

            dispositivos_processed.sort(
                key=lambda x: (-x["cpu_benchmark"], x["precio"])
            )
            return dispositivos_processed

        except Exception as e:
            print(f"❌ Error crítico en el Modelo de Dispositivos: {e}")
            return []
