# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from controllers.sma_controller import AgenteInterfazCoordinador

app = FastAPI(
    title="SBC + SMA Celulares - API Híbrida", description="Backend Inteligente"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agente_coordinador = AgenteInterfazCoordinador()


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
    red_5g: Optional[str] = Field(default="no", alias="5g")
    sistema_operativo: Optional[str] = "android"

    class Config:
        populate_by_name = True


@app.get("/")
def read_root():
    return {"status": "Online", "sistema": "Híbrido SMA + SBC"}


@app.post("/api/login")
def login(payload: LoginRequest):
    res = agente_coordinador.procesar_login(payload.correo, payload.contrasena)
    if not res["success"]:
        raise HTTPException(status_code=401, detail=res["message"])
    return res


@app.post("/api/registro")
def registrar_usuario(payload: RegistroRequest):
    res = agente_coordinador.procesar_registro(
        payload.nombre, payload.correo, payload.contrasena
    )
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["message"])
    return res


@app.get("/api/formulario")
def obtener_formulario_dinamico():
    return agente_coordinador.generar_cuestionario_dinamico()


@app.post("/api/recomendar")
def recomendar_dispositivos(payload: RecomendacionRequest):
    respuestas_dict = payload.model_dump(by_alias=True)
    id_usuario = respuestas_dict.pop("id_usuario", None)
    return agente_coordinador.ejecutar_ciclo_sbc_hibrido(respuestas_dict, id_usuario)


@app.get("/api/historial/{id_usuario}")
def obtener_historial_usuario(id_usuario: int):
    return agente_coordinador.obtener_historial_usuario(id_usuario)
