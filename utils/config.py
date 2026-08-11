# config.py
"""
Archivo de configuración central para el proyecto WAREBOX.
"""
from pathlib import Path
import json

# --- Nombre del Aplicativo ---
PROJECT_NAME = "WAREBOX"

SETTINGS_FILE = Path(__file__).resolve().parent / "settings.json"

def load_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

_settings = load_settings()

# --- Configuración de las Máquinas Virtuales ---
VM_NAME = _settings.get("VM_NAME", "W10PRO")
SNAPSHOT_NAME = _settings.get("SNAPSHOT_NAME", "warebox-v18")
NETWORK_VM_NAME = _settings.get("NETWORK_VM_NAME", "DEBIANET")
NETWORK_SNAPSHOT_NAME = _settings.get("NETWORK_SNAPSHOT_NAME", "fake-network-v3")

# --- Credenciales del Guest (Windows) ---
GUEST_USER = _settings.get("GUEST_USER", "ucjc")
GUEST_PASS = _settings.get("GUEST_PASS", "ucjc")

# --- Credenciales del Guest (Debian) ---
NETWORK_GUEST_USER = _settings.get("NETWORK_GUEST_USER", "ucjc")
NETWORK_GUEST_PASS = _settings.get("NETWORK_GUEST_PASS", "ucjc")

# --- Rutas de Herramientas en el Guest ---
GUEST_TOOLS_DIR = "C:\\Tools"
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

HAYABUSA_BIN_PATH = Path(__file__).resolve().parent.parent / "dependencies" / "hayabusa" / "hayabusa-3.8.1-lin-x64-gnu"

# --- Feature Flags ---
ENABLE_PROCMON = False
ENABLE_SURICATA = False

# --- Clave para descomprimir archivos ---
COMPRESS_KEY = _settings.get("COMPRESS_KEY", "infected")

# --- Muestra a Analizar ---
ZIP_FILENAME = _settings.get("ZIP_FILENAME", "rufus.zip")
PAYLOAD_NAME = _settings.get("PAYLOAD_NAME", "rufus.exe")
PAYLOAD_SHA256 = _settings.get("PAYLOAD_SHA256", "9fcad316c82ba3d0c3130c9f43fb0fe147e9eb62e1bf830716a0bbb6c58d24ee")

# --- Tiempos de espera ---
WAIT_START_TIME = _settings.get("WAIT_START_TIME", 30)
WAIT_MALWARE_TIME = _settings.get("WAIT_MALWARE_TIME", 10)
WAIT_WRITE_FILES_TIME = _settings.get("WAIT_WRITE_FILES_TIME", 10)

# --- Firma de tiempo ---
TIMESTAMP_SIGNATURE = _settings.get("TIMESTAMP_SIGNATURE", "20260805_233108")