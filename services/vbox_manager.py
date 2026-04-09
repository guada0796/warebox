# vbox_manager.py
"""
Módulo para gestionar las operaciones de la máquina virtual con VBoxManage.
"""
import subprocess
from utils.config import VM_NAME, GUEST_USER, GUEST_PASS, GUEST_CMD_PATH, GUEST_POWERSHELL_PATH, HOST_EVIDENCE_DIR, SNAPSHOT_NAME
from datetime import datetime
from utils import messages as msg

def run_vbox_command(command, description):
    """Función genérica para ejecutar comandos de VBoxManage."""
    msg.processing(f"{description}")
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        msg.info(f"Comando '{description}' completado")

        return True
    except subprocess.CalledProcessError as e:
        msg.error(f"Error al ejecutar '{description}': {e.stderr.strip()}")
        return False

def restore_start_vm(vm_name, snapshot_name):
    """Restaura a un snapshot y enciende la VM en modo headless."""
    if not run_vbox_command(["VBoxManage", "snapshot", vm_name, "restore", snapshot_name], f"Restaurando VM a '{snapshot_name}'"):
        return False
    if not run_vbox_command(["VBoxManage", "startvm", vm_name, "--type", "headless"], "Iniciando VM"):
        return False
    return True

def restore_start_vm_gui(vm_name, snapshot_name):
    """Restaura a un snapshot y enciende la VM en normal."""
    if not run_vbox_command(["VBoxManage", "snapshot", vm_name, "restore", snapshot_name], f"Restaurando VM a '{snapshot_name}'"):
        return False
    if not run_vbox_command(["VBoxManage", "startvm", vm_name], "Iniciando VM en modo gráfico"):
        return False
    return True

def start_vm_gui(vm_name):
    """Inicia la VM en modo normal (con interfaz gráfica)."""
    command = ["VBoxManage", "startvm", vm_name]
    return run_vbox_command(command, "Iniciando VM en modo gráfico")

def stop_vm(vm_name):
    """Apaga la máquina virtual."""
    return run_vbox_command(["VBoxManage", "controlvm", vm_name, "poweroff"], "Apagando la VM")

def run_command_in_guest(command, description):
    """Ejecuta un comando dentro de la VM invitada usando cmd.exe."""
    full_command = ["VBoxManage", "guestcontrol", VM_NAME, "run", "--username", GUEST_USER, "--password", GUEST_PASS, "--exe", GUEST_CMD_PATH, "--", "/c", command]
    return run_vbox_command(full_command, description)

def run_powershell_command(command, description):
    """Ejecuta un comando de PowerShell en la VM."""
    full_command = ["VBoxManage", "guestcontrol", VM_NAME, "run", "--username", GUEST_USER, "--password", GUEST_PASS, "--exe", GUEST_POWERSHELL_PATH, "--", "-Command", command]
    return run_vbox_command(full_command, description)

# --- Grabación de pantalla nativa de VirtualBox (VBoxManage 7.2.6) ---
def _get_recording_filename():
    """Genera el nombre de archivo para la grabación según el formato solicitado."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{VM_NAME}-{SNAPSHOT_NAME}-{timestamp}.webm"
    return HOST_EVIDENCE_DIR / filename

def start_vm_recording(vm_name):
    """Configura y activa la grabación de pantalla de la VM (debe llamarse cuando la VM ya está corriendo)."""
    output_path = _get_recording_filename()
    HOST_EVIDENCE_DIR.mkdir(exist_ok=True)
    # 1. Configurar el nombre del archivo
    cmd_filename = ["VBoxManage", "controlvm", vm_name, "recording", "filename", str(output_path)]
    if not run_vbox_command(cmd_filename, f"Configurando archivo de grabación: {output_path}"):
        return False
    # 2. (Opcional) Configurar otras opciones aquí si se desea (resolución, fps, etc)
    # 3. Activar la grabación
    cmd_on = ["VBoxManage", "controlvm", vm_name, "recording", "start"]
    return run_vbox_command(cmd_on, "Grabacion ON")

def stop_vm_recording(vm_name):
    """Detiene la grabación de pantalla de la VM con VBoxManage."""
    cmd_off = ["VBoxManage", "controlvm", vm_name, "recording", "stop"]
    return run_vbox_command(cmd_off, "Grabacion OFF")