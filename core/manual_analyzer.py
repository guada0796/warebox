# manual_analyzer.py
"""
Módulo para gestionar el análisis manual de las evidencias recolectadas.
Adaptado para entornos gráficos (GUI), no bloqueante.
"""
from pathlib import Path
import time
from utils import config
from services import vbox_manager as vbox
from core import file_handler as file

def setup_new_analysis(status_callback=None):
    """
    Prepara un entorno limpio con las evidencias para un nuevo análisis manual.
    Utiliza status_callback(mensaje, color) para notificar a la GUI.
    """
    def notify(msg, color="white"):
        if status_callback:
            status_callback(msg, color)
            
    notify("Restaurando snapshot base y arrancando VM (GUI)...", "yellow")
    if not vbox.restore_start_vm_gui(config.VM_NAME, config.SNAPSHOT_NAME):
        notify("Fallo al restaurar o arrancar la VM.", "red")
        return False
    
    notify(f"Esperando {config.WAIT_START_TIME} segundos para el arranque completo...", "yellow")
    # Para no bloquear totalmente, dividimos el sleep en iteraciones pequeñas
    # Aunque lo ideal es que este método corra en un thread
    for i in range(config.WAIT_START_TIME):
        time.sleep(1)
    
    notify("Creando directorio de logs en la VM...", "yellow")
    mkdir_cmd = f"New-Item -Path '{config.GUEST_LOG_DIR}' -ItemType Directory -Force"
    if not vbox.run_powershell_command(mkdir_cmd, f"Creando directorio de logs en la VM"):
        notify("Fallo al crear directorio de logs en la VM.", "red")
        return False

    notify("Copiando archivos de evidencia a la VM...", "yellow")
    evidence_files = [config.HOST_SYSMON_LOG_DIR, config.HOST_TCPDUMP_LOG_DIR]
    if config.ENABLE_PROCMON:
        evidence_files.insert(0, config.HOST_PROCMON_LOG_DIR)
    
    for file_path in evidence_files:
        filename = file_path.name.replace("$fch$", config.TIMESTAMP_SIGNATURE)
        host_file = file_path.with_name(filename)
        
        if host_file.exists():
            notify(f"Copiando {filename}...", "gray")
            file.copy_to_guest(host_file, f"{config.GUEST_LOG_DIR}\\{filename}")
        else:
            notify(f"Advertencia: No se encontró la evidencia '{host_file.name}'", "orange")

    notify("Entorno listo para el análisis manual.", "green")
    return True

def restore_analysis(snapshot_to_open, status_callback=None):
    """
    Restaura un snapshot de un análisis guardado previamente.
    """
    def notify(msg, color="white"):
        if status_callback:
            status_callback(msg, color)
            
    notify(f"Restaurando el análisis guardado: {snapshot_to_open}...", "yellow")
    
    if not vbox.restore_start_vm_gui(config.VM_NAME, snapshot_to_open):
        notify("Fallo al restaurar el snapshot.", "red")
        return False

    notify("Entorno de análisis restaurado con éxito.", "green")
    return True
