# config.py
"""
Archivo de configuración central para el proyecto WAREBOX.
"""
from pathlib import Path

# --- Nombre del Aplicativo ---
PROJECT_NAME = "WAREBOX"

# --- Configuración de las Máquinas Virtuales ---
VM_NAME = "W10PRO"
SNAPSHOT_NAME = "warebox-v11"
NETWORK_VM_NAME = "DebiaNet"
NETWORK_SNAPSHOT_NAME = "fake-network-v3"

# --- Credenciales del Guest (Windows) ---
GUEST_USER = "ucjc"
GUEST_PASS = "ucjc"

# --- Credenciales del Guest (Debian) ---
NETWORK_GUEST_USER = "ucjc"
NETWORK_GUEST_PASS = "ucjc"

# --- Rutas de Herramientas en el Guest ---
GUEST_TOOLS_DIR = "C:\\Tools"
GUEST_PAYLOAD_PATH_TEMPLATE = f"{GUEST_TOOLS_DIR}\\{{payload_name}}"
GUEST_PROCMON_PATH = f"{GUEST_TOOLS_DIR}\\Procmon.exe"
GUEST_POWERSHELL_PATH = f"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
GUEST_CMD_PATH = f"C:\\Windows\\System32\\cmd.exe"
GUEST_LOG_DIR = f"C:\\Users\\{GUEST_USER}\\Desktop\\Logs"
GUEST_PROCMON_LOG = f"{GUEST_LOG_DIR}\\procmon_$fch$.pml"
GUEST_SYSMON_LOG = f"{GUEST_LOG_DIR}\\sysmon_$fch$.evtx"

# --- Rutas de Herramientas en la red Debian ---
NETWORK_TCPDUMP_LOG = "/home/ucjc/warebox-capture.pcap"

# --- Rutas en el Host (Ubuntu) ---
HOST_DIR = Path.home() / "warebox-workspace"
HOST_MALWARE_DIR = HOST_DIR / "Malware_Reports"
HOST_TEMP_DIR = HOST_DIR / "Malware_Temp"
HOST_EVIDENCE_DIR = HOST_DIR / "Malware_Evidence"

# --- Clave para descomprimir archivos ---
COMPRESS_KEY = "infected"

# --- Muestra a Analizar ---
ZIP_FILENAME = "0b1f13853ca89b0f902a13bb80f12c9a97c666b3a8adc8f062f8622e7a63cbd9.zip"
PAYLOAD_EXE_NAME = "0b1f13853ca89b0f902a13bb80f12c9a97c666b3a8adc8f062f8622e7a63cbd9.exe"

# --- Tiempo de espera en segundos para que arranque la VM --
WAIT_START_TIME = 40
# --- Tiempo de espera en segundos para que actúe el malware --
WAIT_MALWARE_TIME = 10
# --- Tiempo de espera en segundos para que se escriban los resultados --
WAIT_WRITE_FILES_TIME = 10

#sudo tcpdump -i enp0s3 -n -w /home/ucjc/captura_malware.pcap