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