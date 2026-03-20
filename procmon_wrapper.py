# procmon_wrapper.py
"""
Módulo dedicado a controlar Process Monitor (ProcMon) usando PowerShell.
"""
from config import GUEST_PROCMON_PATH, GUEST_LOG_DIR, GUEST_PROCMON_LOG
import vbox_manager as vbox

def start_capture():
    """Prepara el directorio de logs e inicia la captura con ProcMon."""
    mkdir_cmd = f"New-Item -Path '{GUEST_LOG_DIR}' -ItemType Directory -Force"
    if not vbox.run_powershell_command(mkdir_cmd, f"Creando directorio de logs en la VM"):
        return False
    
    procmon_args = f"'/accepteula /quiet /backingfile \"{GUEST_PROCMON_LOG}\"'"
    procmon_cmd = f"Start-Process -FilePath '{GUEST_PROCMON_PATH}' -ArgumentList {procmon_args}"
    return vbox.run_powershell_command(procmon_cmd, "Iniciando captura con ProcMon")

def stop_capture():
    """Detiene la captura de ProcMon."""
    procmon_cmd = f'& "{GUEST_PROCMON_PATH}" /terminate'
    return vbox.run_powershell_command(procmon_cmd, "Deteniendo captura de ProcMon")