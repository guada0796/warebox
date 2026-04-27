#!/bin/bash

# ============================
# CONFIGURACIÓN
# ============================
VBOX_VERSION="7.2.6"
VBOX_BUILD="172322"
SDK_ZIP="VirtualBoxSDK-${VBOX_VERSION}-${VBOX_BUILD}.zip"
SDK_URL="https://download.virtualbox.org/virtualbox/${VBOX_VERSION}/${SDK_ZIP}"
SDK_TEMP_DIR="/tmp/virtualbox-sdk"
SDK_DEST_DIR="/opt/virtualbox-sdk"
VENV_DIR="$HOME/Documentos/universidades/ucjc/clases-ciberseguridad/tfm/warebox/venv"
PYTHON_BIN="python3"

# ============================
# DESCARGA Y DESCOMPRESIÓN
# ============================
echo "📥 Descargando VirtualBox SDK ${VBOX_VERSION} (${VBOX_BUILD})..."
wget -q --show-progress "$SDK_URL" -O "/tmp/${SDK_ZIP}" || {
    echo "❌ Error al descargar el SDK desde:"
    echo "$SDK_URL"
    exit 1
}

echo "📦 Descomprimiendo..."
rm -rf "$SDK_TEMP_DIR"
unzip -q "/tmp/${SDK_ZIP}" -d "$SDK_TEMP_DIR" || {
    echo "❌ Error al descomprimir el archivo ZIP"
    exit 1
}

# Detectar carpeta SDK real (por si cambia el nombre del ZIP)
EXTRACTED_SDK_DIR=$(find "$SDK_TEMP_DIR" -maxdepth 1 -type d -name "sdk*" | head -n1)
if [ ! -d "$EXTRACTED_SDK_DIR" ]; then
    echo "❌ No se encontró la carpeta SDK extraída"
    exit 1
fi

echo "📁 Instalando en ${SDK_DEST_DIR}..."
sudo rm -rf "$SDK_DEST_DIR"
sudo mv "$EXTRACTED_SDK_DIR" "$SDK_DEST_DIR"

# ============================
# CREAR setup.py PARA EL BINDING
# ============================
echo "🛠 Preparando archivo setup.py para instalación de bindings..."
SETUP_FILE="${SDK_DEST_DIR}/bindings/xpcom/python/setup.py"
cat << EOF | sudo tee "$SETUP_FILE" > /dev/null
from setuptools import setup, find_packages

setup(
    name='virtualbox',
    version='${VBOX_VERSION}',
    description='Python bindings for VirtualBox COM/XPCOM API',
    author='Oracle',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
EOF

# ============================
# CREAR Y CONFIGURAR ENTORNO VIRTUAL
# ============================
echo "🐍 Creando entorno virtual en $VENV_DIR..."
$PYTHON_BIN -m venv "$VENV_DIR" || {
    echo "❌ Error al crear el entorno virtual"
    exit 1
}

echo "📦 Instalando bindings dentro del entorno virtual..."
source "$VENV_DIR/bin/activate"
pip install "$SDK_DEST_DIR/bindings/xpcom/python"
deactivate

# ============================
# VARIABLE DE ENTORNO (opcional)
# ============================
if ! grep -q "VBOX_SDK_PATH" ~/.bashrc; then
    echo "export VBOX_SDK_PATH=${SDK_DEST_DIR}" >> ~/.bashrc
    echo "✅ Variable de entorno VBOX_SDK_PATH añadida a ~/.bashrc"
fi

echo ""
echo "✅ SDK de VirtualBox ${VBOX_VERSION} instalado correctamente"
echo "✅ Binding de Python instalado en entorno virtual:"
echo "   $VENV_DIR"
echo ""
echo "ℹ️ Para usar el binding en tus scripts, ejecuta:"
echo "   source \"$VENV_DIR/bin/activate\""
echo "   python tu_script.py"
echo ""
echo "🔁 Recarga tu terminal si quieres aplicar la variable VBOX_SDK_PATH:"
echo "   source ~/.bashrc"

