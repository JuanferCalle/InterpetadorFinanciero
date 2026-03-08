@echo off
REM Script para iniciar la aplicación completa en Windows

echo =========================================
echo Asistente Financiero - Iniciando
echo =========================================
echo.

REM Verificar si Ollama está corriendo
echo [*] Verificando Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ADVERTENCIA: Ollama no parece estar corriendo
    echo Por favor, ejecuta "ollama serve" en otra terminal
    echo.
)

REM Activar entorno y ejecutar backend
echo [*] Iniciando Backend...
cd backend
call venv\Scripts\activate.bat
start cmd /k python app.py

REM Esperar un poco
timeout /t 2 /nobreak

REM Iniciar servidor frontend
cd ..\frontend
echo [*] Iniciando Frontend...
start cmd /k python -m http.server 8000

echo.
echo =========================================
echo Aplicación iniciada!
echo =========================================
echo.
echo Accede a: http://localhost:8000
echo API: http://localhost:5000
echo.
