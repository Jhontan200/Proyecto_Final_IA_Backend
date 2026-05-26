# 🚀 SBC + SMA Celulares - Backend Inteligente

Este es el backend del sistema híbrido de recomendación de dispositivos móviles, diseñado bajo el enfoque de **IA Simbólica**. Utiliza un **Sistema Multiagente (SMA)** para coordinar las tareas y un **Sistema Basado en Conocimiento (SBC)** con un motor de inferencia de encadenamiento hacia adelante (*Forward Chaining*) para deducir requisitos de hardware óptimos cruzados con ofertas comerciales.

---

## 🛠️ Requisitos Previos (Programas a instalar)

Antes de comenzar, asegúrate de tener instalados los siguientes programas en tu sistema:

1. **Python (Versión 3.11 o superior)**
   * Descárgalo desde [python.org](https://www.python.org/downloads/).
   * **CRITICAL:** Durante la instalación en Windows, asegúrate de marcar la casilla **"Add Python.exe to PATH"**.
2. **Git**
   * Descárgalo desde [git-scm.com](https://git-scm.com/).
   * Necesario para clonar el repositorio y gestionar las ramas de desarrollo.
3. **Visual Studio Code (O el IDE de tu preferencia)**
   * Descárgalo desde [code.visualstudio.com](https://code.visualstudio.com/).
   * Se recomienda instalar la extensión **Python (Pylance)**.

---

## 📦 Pasos para la Instalación Local

Sigue estos pasos en orden secuencial dentro de tu terminal (ej. PowerShell, CMD o la terminal integrada de VS Code):

### Paso 1: Clonar el repositorio e ingresar a la carpeta
Abre tu terminal, posiciónate en el directorio donde deseas guardar el proyecto y ejecuta:
```bash
git clone https://github.com/Jhontan200/Proyecto_Final_IA_Backend.git
cd "Proyecto"
```
### Paso 2: Instalar las Dependencias del Sistema
Instala todas las librerías necesarias ejecutando el siguiente comando:
```bash
pip install fastapi uvicorn pydantic[email] email-validator psycopg2-binary
```
* fastapi: Framework principal para construir los endpoints de la API.

* uvicorn: Servidor ASGI rápido para ejecutar y recargar la aplicación en desarrollo.

* pydantic[email] y email-validator: Encargados de robustecer la validación de estructuras de datos y correos electrónicos reales en las solicitudes de login/registro.

* psycopg2-binary: Conector nativo de PostgreSQL para interactuar mediante cursores con las bases de datos relacionales en la nube.

# 🚀 Ejecución del Servidor de Desarrollo
Para levantar el backend localmente y dejarlo en modo de escucha activa ante cambios en el código, ejecuta:
```bash
uvicorn main:app --reload
```
Si todo se instaló correctamente, verás una salida en la terminal similar a esta:
```bash
INFO:     Uvicorn running on [http://127.0.0.1:8000](http://127.0.0.1:8000) (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Will watch for changes in these directories: ['D:\...\Proyecto']
```
# 🗺️ Endpoints y Documentación Interactiva (Swagger UI)
Una vez que el servidor esté corriendo, FastAPI autogenera la documentación de las rutas. Puedes ingresar desde tu navegador web a:
* Documentación Interactiva: http://127.0.0.1:8000/docs (Aquí puedes probar los métodos de los agentes directamente presionando el botón "Try it out").

* JSON alternativo de la API: http://127.0.0.1:8000/redoc

Rutas principales expuestas para el Frontend:
* POST /api/login: Valida las credenciales de acceso contra la tabla usuarios.

* POST /api/registro: Permite dar de alta cuentas nuevas guardando los campos nombre, correo y contrasena en la base de datos.

* GET /api/formulario: Retorna el árbol de preguntas dinámicas directo de las tablas del cuestionario.

* POST /api/recomendar: Recibe las elecciones del usuario, dispara el motor de inferencia multiagente y registra la auditoría del resultado en historial_recomendaciones.