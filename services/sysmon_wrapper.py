# services/sysmon_wrapper.py
"""
Módulo dedicado a controlar y extraer logs de Sysmon en la máquina virtual.
A diferencia de ProcMon, Sysmon se ejecuta como servicio desde el arranque, 
por lo que solo necesitamos exportar y extraer sus resultados al finalizar.
"""
from utils import config
from services import vbox_manager as vbox
from datetime import datetime

# Ruta temporal en el guest para guardar el log exportado sin bloqueos de archivo
# GUEST_SYSMON_LOG = r"C:\Users\Public\sysmon_export.evtx"

def extract_logs(sample_name="malware"):
    """
    Exporta el log de Sysmon usando herramientas nativas de Windows 
    y lo transfiere al directorio de evidencias en el Host.
    
    Retorna la ruta del archivo extraído en el Host o None si falla.
    """
    # 1. Exportar el registro (evita el error de "File in use")
    # Utilizamos el cmd estándar que ya tienes configurado en vbox_manager
    export_cmd = f"wevtutil epl Microsoft-Windows-Sysmon/Operational {config.GUEST_SYSMON_LOG}"
    if not vbox.run_command_in_guest(export_cmd, "Exportando logs de Sysmon en la VM"):
        return None
    
    # 2. Preparar el destino en el Host
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    host_output_file = config.HOST_EVIDENCE_DIR / f"sysmon_{sample_name}_{timestamp}.evtx"
    
    # Asegurar que el directorio en el host exista (Pathlib)
    if not config.HOST_EVIDENCE_DIR.exists():
        config.HOST_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    # 3. Extraer el archivo usando VBoxManage guestcontrol copyfrom
    # Armamos el comando manualmente ya que no existe un copyfrom en vbox_manager.py
    copy_cmd = [
        "VBoxManage", "guestcontrol", config.VM_NAME, "copyfrom",
        config.GUEST_SYSMON_LOG, str(host_output_file),
        "--username", config.GUEST_USER, "--password", config.GUEST_PASS
    ]
    
    if vbox.run_vbox_command(copy_cmd, f"Transfiriendo log de Sysmon a {host_output_file.name}"):
        return host_output_file
    
    return None