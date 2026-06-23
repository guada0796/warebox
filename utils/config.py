# config.py
"""
Archivo de configuración central para el proyecto WAREBOX.
"""
from pathlib import Path

# --- Nombre del Aplicativo ---
PROJECT_NAME = "WAREBOX"

# --- Configuración de las Máquinas Virtuales ---
VM_NAME = "W10PRO"
SNAPSHOT_NAME = "warebox-v17"
NETWORK_VM_NAME = "DEBIANET"
NETWORK_SNAPSHOT_NAME = "fake-network-v3"

# --- Credenciales del Guest (Windows) ---
GUEST_USER = "ucjc"
GUEST_PASS = "ucjc"

# --- Credenciales del Guest (Debian) ---
NETWORK_GUEST_USER = "ucjc"
NETWORK_GUEST_PASS = "ucjc"

# --- Rutas de Herramientas en el Guest ---
GUEST_TOOLS_DIR = "C:\\Tools"
#GUEST_PAYLOAD_PATH_TEMPLATE = f"{GUEST_TOOLS_DIR}\\{{payload_name}}"
GUEST_PAYLOAD_PATH_TEMPLATE = f"C:\\Users\\{GUEST_USER}\\Desktop\\{{payload_name}}"
GUEST_PROCMON_PATH = f"{GUEST_TOOLS_DIR}\\Procmon.exe"
GUEST_POWERSHELL_PATH = f"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
GUEST_CMD_PATH = f"C:\\Windows\\System32\\cmd.exe"
GUEST_LOG_DIR = f"C:\\Users\\{GUEST_USER}\\Desktop\\Logs"
GUEST_PROCMON_LOG = f"{GUEST_LOG_DIR}\\procmon_$fch$.pml"
GUEST_SYSMON_LOG = f"{GUEST_LOG_DIR}\\sysmon_$fch$.evtx"

# --- Rutas de Herramientas en la red Debian ---
NETWORK_TCPDUMP_LOG = "/home/ucjc/warebox-capture.pcap"

# --- Rutas en el Host ---
HOST_DIR = Path.home() / "warebox-workspace"
HOST_MALWARE_DIR = HOST_DIR / "Malware_Reports"
HOST_TEMP_DIR = HOST_DIR / "Malware_Temp"
HOST_EVIDENCE_DIR = HOST_DIR / "Malware_Evidence"

HOST_TCPDUMP_OLD_LOG_DIR = HOST_EVIDENCE_DIR / "warebox-capture.pcap"
HOST_TCPDUMP_LOG_DIR = HOST_EVIDENCE_DIR / "tcpdump_$fch$.pcap"
HOST_PROCMON_LOG_DIR = HOST_EVIDENCE_DIR / "procmon_$fch$.pml"
HOST_SYSMON_LOG_DIR = HOST_EVIDENCE_DIR / "sysmon_$fch$.evtx"

HAYABUSA_BIN_PATH = Path.home() / "github/warebox/dependencies/hayabusa/hayabusa-3.8.1-lin-x64-gnu"

# --- Clave para descomprimir archivos ---
COMPRESS_KEY = "infected"

# --- Muestra a Analizar ---
ZIP_FILENAME = "9f844a78cc2cd8d8a426f050a3efe319930f723eb10be231de1c1f1600e82127.zip"
PAYLOAD_NAME = "9f844a78cc2cd8d8a426f050a3efe319930f723eb10be231de1c1f1600e82127.exe"

# --- Tiempo de espera en segundos para que arranque la VM --
WAIT_START_TIME = 30
# --- Tiempo de espera en segundos para que actúe el malware --
WAIT_MALWARE_TIME = 10
# --- Tiempo de espera en segundos para que se escriban los resultados --
WAIT_WRITE_FILES_TIME = 10

# --- Firma de tiempo que sirve para nombrar los resultados
TIMESTAMP_SIGNATURE = "20260623_134742"
#sudo tcpdump -i enp0s3 -n -w /home/ucjc/captura_malware.pcap