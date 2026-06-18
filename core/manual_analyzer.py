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

def new_analysis():
    """Prepara un entorno limpio con las evidencias para un nuevo análisis manual."""
    cli_utils.clear_screen()
    msg.title("Nuevo Análisis Manual")
    
    if not vbox.restore_start_vm_gui(config.VM_NAME, config.SNAPSHOT_NAME): return
    
    msg.waiting(f"Esperando {config.WAIT_START_TIME} segundos para el arranque completo")
    time.sleep(config.WAIT_START_TIME)
    
    """Prepara el directorio de logs e inicia la captura con ProcMon."""
    mkdir_cmd = f"New-Item -Path '{config.GUEST_LOG_DIR}' -ItemType Directory -Force"
    if not vbox.run_powershell_command(mkdir_cmd, f"Creando directorio de logs en la VM"):
        return False

    msg.processing("Copiando archivos de evidencia a la VM")
    evidence_files = [config.HOST_PROCMON_LOG_DIR, config.HOST_SYSMON_LOG_DIR, config.HOST_TCPDUMP_LOG_DIR]
    for file_path in evidence_files:

        filename = file_path.name.replace("$fch$", config.TIMESTAMP_SIGNATURE)
        host_file = file_path.with_name(filename)
        
        if host_file.exists():
            file.copy_to_guest(host_file, f"{config.GUEST_LOG_DIR}\\{filename}")
        else:
            msg.warning(f"Advertencia: No se encontró el archivo de evidencia '{host_file.name}' en el host")

    msg.done("Entorno listo para el análisis manual")
    input("\n--- Presione Enter aquí cuando haya finalizado su análisis en la VM. ---")
    
    save = input("\n¿Desea guardar el estado actual de su análisis como un nuevo snapshot? (s/N): ").lower()
    if save == 's':
        snapshot_manager.create_snapshot()
    
    vbox.stop_vm(config.VM_NAME)
    msg.done("Análisis finalizado")
    time.sleep(2)

def open_analysis():
    """Restaura un snapshot de un análisis guardado previamente."""
    cli_utils.clear_screen()
    msg.title("Abrir Análisis Guardado")
    
    snapshot_manager.list_snapshots()
    snapshot_to_open = input("\nIntroduce el nombre exacto del snapshot de análisis que deseas abrir: ")
    if not snapshot_to_open:
        msg.error("El nombre no puede estar vacío"); time.sleep(2); return

    if not vbox.restore_start_vm_gui(config.VM_NAME, config.SNAPSHOT_NAME): return

    msg.line_break(1)
    msg.done("Entorno de análisis restaurado")
    msg.info("Presione Enter aquí cuando haya finalizado su análisis en la VM")
    msg.line_break(1)
    
    save = input("\n¿Desea guardar los cambios (actualizar el timestamp del snapshot)? (s/N): ").lower()
    if save == 's':
        base_name = snapshot_to_open.rsplit('_', 1)[0]
        final_snapshot_name = f"{base_name}_{cli_utils.get_current_timestamp()}"
        vbox.run_vbox_command(["VBoxManage", "snapshot", config.VM_NAME, "take", final_snapshot_name], f"Creando snapshot actualizado '{final_snapshot_name}'")

    vbox.stop_vm(config.VM_NAME)
    msg.done("Análisis finalizado")
    time.sleep(2)
