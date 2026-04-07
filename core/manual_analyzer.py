# manual_analyzer.py
"""
Módulo para gestionar el análisis manual de las evidencias recolectadas,
reutilizando las funciones existentes de snapshot_manager.
"""
import time
from utils import config, cli_utils
from services import vbox_manager as vbox
from core import file_handler as file
from services import snapshot_manager

def new_analysis():
    """Prepara un entorno limpio con las evidencias para un nuevo análisis manual."""
    cli_utils.clear_screen()
    print("--- Nuevo Análisis Manual ---")
    
    if not vbox.restore_start_vm_gui(config.VM_NAME, config.SNAPSHOT_NAME): return
    
    print("⏱️  Esperando 20 segundos para el arranque completo...")
    time.sleep(config.WAIT_START_TIME)
    
    """Prepara el directorio de logs e inicia la captura con ProcMon."""
    mkdir_cmd = f"New-Item -Path '{config.GUEST_LOG_DIR}' -ItemType Directory -Force"
    if not vbox.run_powershell_command(mkdir_cmd, f"Creando directorio de logs en la VM"):
        return False

    print("⚙️  Copiando archivos de evidencia a la VM...")
    evidence_files = [config.GUEST_PROCMON_LOG]
    for file_path in evidence_files:
        host_file = config.HOST_EVIDENCE_DIR / file_path.split('\\')[-1]
        if host_file.exists():
            file.copy_to_guest(host_file, file_path)
        else:
            print(f"⚠️  Advertencia: No se encontró el archivo de evidencia '{host_file.name}' en el host.")

    print("\n✅✅✅ Entorno listo para el análisis manual ✅✅✅")
    input("\n--- Presione Enter aquí cuando haya finalizado su análisis en la VM. ---")
    
    save = input("\n¿Desea guardar el estado actual de su análisis como un nuevo snapshot? (s/N): ").lower()
    if save == 's':
        snapshot_manager.create_snapshot()
    
    vbox.stop_vm(config.VM_NAME)
    print("\nAnálisis finalizado.")
    time.sleep(2)

def open_analysis():
    """Restaura un snapshot de un análisis guardado previamente."""
    cli_utils.clear_screen()
    print("--- Abrir Análisis Guardado ---")
    
    snapshot_manager.list_snapshots()
    snapshot_to_open = input("\nIntroduce el nombre exacto del snapshot de análisis que deseas abrir: ")
    if not snapshot_to_open:
        print("❌ El nombre no puede estar vacío."); time.sleep(2); return

    if not vbox.restore_start_vm_gui(config.VM_NAME, config.SNAPSHOT_NAME): return

    print("\n✅✅✅ Entorno de análisis restaurado ✅✅✅")
    input("\n--- Presione Enter aquí cuando haya finalizado su análisis en la VM. ---")
    
    save = input("\n¿Desea guardar los cambios (actualizar el timestamp del snapshot)? (s/N): ").lower()
    if save == 's':
        base_name = snapshot_to_open.rsplit('_', 1)[0]
        final_snapshot_name = f"{base_name}_{cli_utils.get_current_timestamp()}"
        vbox.run_vbox_command(["VBoxManage", "snapshot", config.VM_NAME, "take", final_snapshot_name], f"Creando snapshot actualizado '{final_snapshot_name}'")

    vbox.stop_vm(config.VM_NAME)
    print("\nAnálisis finalizado.")
    time.sleep(2)
