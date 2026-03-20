#!/bin/bash

# ============================
# CONFIGURACIÓN
# ============================
SDK_DIR="/opt/virtualbox-sdk"
VENV_DIR="$HOME/Documentos/ucjc/clases-ciberseguridad/tfm/waretine/venv"

echo "🧹 Iniciando desinstalación de VirtualBox SDK y entorno virtual..."

# ============================
# ELIMINAR SDK
# ============================
if [ -d "$SDK_DIR" ]; then
    echo "📁 Eliminando SDK en $SDK_DIR..."
    sudo rm -rf "$SDK_DIR"
else
    echo "ℹ️ No se encontró el directorio SDK en $SDK_DIR"
fi

# ============================
# ELIMINAR ENTORNO VIRTUAL
# ============================
if [ -d "$VENV_DIR" ]; then
    echo "🐍 Eliminando entorno virtual en $VENV_DIR..."
    rm -rf "$VENV_DIR"
else
    echo "ℹ️ No se encontró el entorno virtual en $VENV_DIR"
fi

# ============================
# ELIMINAR VARIABLE DE ENTORNO
# ============================
if grep -q "VBOX_SDK_PATH" ~/.bashrc; then
    echo "🔧 Eliminando VBOX_SDK_PATH de ~/.bashrc..."
    sed -i '/VBOX_SDK_PATH/d' ~/.bashrc
else
    echo "ℹ️ La variable VBOX_SDK_PATH no está definida en ~/.bashrc"
fi

echo ""
echo "✅ Desinstalación completa"
echo "🔁 Recarga tu terminal con: source ~/.bashrc"

