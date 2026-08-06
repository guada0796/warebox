# manual_analyzer.py
"""
Módulo para gestionar el análisis manual de las evidencias recolectadas,
reutilizando las funciones existentes de snapshot_manager.
"""
from pathlib import Path
import time
from utils import config, cli_utils, messages as msg
from services import vbox_manager as vbox
from core import file_handler as file
from services import snapshot_manager

def setup_new_analysis():
    """Prepara un entorno limpio con las evidencias para un nuevo análisis manual."""
    cli_utils.clear_screen()
    msg.title("Nuevo Análisis Manual")
    
    if not vbox.restore_start_vm_gui(config.VM_NAME, config.SNAPSHOT_NAME): return False
    
    msg.waiting(f"Esperando {config.WAIT_START_TIME} segundos para el arranque completo")
    time.sleep(config.WAIT_START_TIME)
    
    """Prepara el directorio de logs e inicia la captura con ProcMon."""
    mkdir_cmd = f"New-Item -Path '{config.GUEST_LOG_DIR}' -ItemType Directory -Force"
    if not vbox.run_powershell_command(mkdir_cmd, f"Creando directorio de logs en la VM"):
        return False

    msg.processing("Copiando archivos de evidencia a la VM")
    
    evidence_files = [config.HOST_SYSMON_LOG_DIR, config.HOST_TCPDUMP_LOG_DIR]
    if config.ENABLE_PROCMON:
        evidence_files.insert(0, config.HOST_PROCMON_LOG_DIR)
    
    for file_path in evidence_files:

        filename = file_path.name.replace("$fch$", config.TIMESTAMP_SIGNATURE)
        host_file = file_path.with_name(filename)
        
        if host_file.exists():
            file.copy_to_guest(host_file, f"{config.GUEST_LOG_DIR}\\{filename}")
        else:
            msg.warning(f"Advertencia: No se encontró el archivo de evidencia '{host_file.name}' en el host")

    msg.done("Entorno listo para el análisis manual")
    return True

def restore_analysis(snapshot_to_open):
    """Restaura un snapshot de un análisis guardado previamente."""
    cli_utils.clear_screen()
    msg.title("Abrir Análisis Guardado")
    
    if not vbox.restore_start_vm_gui(config.VM_NAME, snapshot_to_open): return False

    msg.line_break(1)
    msg.done("Entorno de análisis restaurado")
    return True
