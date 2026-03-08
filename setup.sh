#!/bin/bash
# Script de inicialización para macOS/Linux

echo "========================================="
echo "Asistente Financiero - Setup"
echo "========================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no está instalado"
    exit 1
fi

echo "[*] Python encontrado: $(python3 --version)"
echo ""

# Ir a backend
cd backend

# Crear entorno virtual
if [ ! -d "venv" ]; then
    echo "[*] Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "[*] Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "[*] Instalando dependencias..."
pip install -q -r ../requirements.txt

# Crear directorio de datos
if [ ! -d "data" ]; then
    echo "[*] Creando directorio de datos..."
    mkdir data
fi

echo ""
echo "========================================="
echo "Setup completado!"
echo "========================================="
echo ""
echo "Para iniciar:"
echo "1. Abre otra terminal y ejecuta: ollama serve"
echo "2. Ejecuta en esta terminal: python app.py"
echo "3. Abre frontend/index.html en tu navegador"
echo ""
