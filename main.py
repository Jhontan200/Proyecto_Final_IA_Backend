from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from controllers.sma_controller import AgenteInterfazCoordinador

app = FastAPI(
    title="SBC + SMA Celulares - API Híbrida",
    description="Backend Inteligente basado en Sistemas Multiagentes y Motores de Inferencia"
)

# =====================================================================
# CONFIGURACIÓN DE CORS (Permite la comunicación con el Frontend)
# =====================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instanciamos al Agente Coordinador Principal del Sistema
agente_coordinador = AgenteInterfazCoordinador()

# =====================================================================
# MODELOS DE TRANSFERENCIA DE DATOS (Pydantic Validation)
# =====================================================================
class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str

class RegistroRequest(BaseModel):
    nombre: str
    correo: EmailStr
    contrasena: str

class RecomendacionRequest(BaseModel):
    id_usuario: Optional[int] = None 
    presupuesto: float
    uso: str
    fotografia: str
    bateria: str
    multitarea: Optional[str] = "no"
    almacenamiento: Optional[str] = "normal"
    pantalla: Optional[str] = "normal"
    # Solución al error de Pylance usando un alias para el JSON del Frontend
    red_5g: Optional[str] = Field(default="no", alias="5g")

    class Config:
        # Permite que Pydantic lea los datos tanto por el nombre de la variable como por el alias
        populate_by_name = True


# =====================================================================
# ENDPOINTS (API RUTAS)
# =====================================================================

@app.get("/")
def read_root():
    return {
        "status": "Online",
        "sistema": "Híbrido SMA + SBC Inteligente",
        "tablas_activas": 15
    }


@app.post("/api/login")
def login(payload: LoginRequest):
    """
    Ruta delegada al Agente Interfaz para comprobar el acceso
    contra la tabla 'usuarios'.
    """
    resultado = agente_coordinador.procesar_login(payload.correo, payload.contrasena)
    if not resultado["success"]:
        raise HTTPException(status_code=401, detail=resultado["message"])
    return resultado


@app.post("/api/registro")
def registrar_usuario(payload: RegistroRequest):
    """
    Ruta delegada al Agente Interfaz para dar de alta a nuevos usuarios
    en la tabla 'usuarios' respetando el script SQL.
    """
    resultado = agente_coordinador.procesar_registro(payload.nombre, payload.correo, payload.contrasena)
    if not resultado["success"]:
        raise HTTPException(status_code=400, detail=resultado["message"])
    return resultado


@app.get("/api/formulario")
def obtener_formulario_dinamico():
    """
    Ruta delegada al Agente Interfaz para construir las preguntas
    de forma dinámica leyendo directo desde Supabase (Tablas preguntas y respuestas).
    """
    resultado = agente_coordinador.generar_cuestionario_dinamico()
    return resultado


@app.post("/api/recomendar")
def recomendar_dispositivos(payload: RecomendacionRequest):
    """
    Ruta principal del motor. Ejecuta el ciclo completo de inferencia,
    búsqueda competitiva en tiendas y guardado en el historial de auditoría.
    """
    # Convertimos a diccionario incluyendo los alias del Frontend ('5g')
    respuestas_dict = payload.dict(by_alias=True)
    id_usuario = respuestas_dict.pop("id_usuario", None)
    
    # Delegamos la ejecución del problema al ecosistema de agentes
    resultado = agente_coordinador.ejecutar_ciclo_sbc_hibrido(respuestas_dict, id_usuario)
    return resultado