@echo off
REM Script de inicialización para Windows

echo =========================================
echo Asistente Financiero - Setup
echo =========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    pause
    exit /b 1
)

echo [*] Python encontrado
echo.

REM Ir a backend
cd backend

REM Crear entorno virtual
if not exist venv (
    echo [*] Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
echo [*] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo [*] Instalando dependencias...
pip install -q -r ..\requirements.txt

REM Crear directorio de datos
if not exist data (
    echo [*] Creando directorio de datos...
    mkdir data
)

echo.
echo =========================================
echo Setup completado!
echo =========================================
echo.
echo Para iniciar:
echo 1. Abre otra terminal y ejecuta: ollama serve
echo 2. Ejecuta en esta terminal: python app.py
echo 3. Abre frontend/index.html en tu navegador
echo.
pause
