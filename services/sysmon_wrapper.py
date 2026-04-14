# services/sysmon_wrapper.py
"""
Módulo dedicado a controlar y extraer logs de Sysmon en la máquina virtual.
A diferencia de ProcMon, Sysmon se ejecuta como servicio desde el arranque, 
por lo que solo necesitamos exportar y extraer sus resultados al finalizar.
"""
from utils import config, cli_utils as cli
from services import vbox_manager as vbox
from core import file_handler as file

# Ruta temporal en el guest para guardar el log exportado sin bloqueos de archivo
# GUEST_SYSMON_LOG = r"C:\Users\Public\sysmon_export.evtx"

def copy_from_guest(vm_name, vm_guest_user, vm_guest_pass):
    """
    Exporta el log de Sysmon usando herramientas nativas de Windows 
    y lo transfiere al directorio de evidencias en el Host.
    
    Retorna la ruta del archivo extraído en el Host o None si falla.
    """
    # 1. Exportar el registro (evita el error de "File in use")
    # Utilizamos el cmd estándar que ya tienes configurado en vbox_manager
    export_cmd = f"wevtutil epl Microsoft-Windows-Sysmon/Operational {config.GUEST_SYSMON_LOG}"
    if not vbox.run_command_in_guest(export_cmd, f"Obteniendo monitoreo de {vm_name}"):
        return None
    
    file.copy_from_guest(vm_name, vm_guest_user, vm_guest_pass, config.GUEST_SYSMON_LOG, config.HOST_EVIDENCE_DIR)
    return
    