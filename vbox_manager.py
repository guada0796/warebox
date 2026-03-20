# vbox_manager.py
"""
Módulo para gestionar las operaciones de la máquina virtual con VBoxManage.
"""
import subprocess
from config import VM_NAME, GUEST_USER, GUEST_PASS, GUEST_CMD_PATH, GUEST_POWERSHELL_PATH

def run_vbox_command(command, description):
    """Función genérica para ejecutar comandos de VBoxManage."""
    print(f"⚙️  {description}...")
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        print("✅ ¡Éxito!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: {e.stderr.strip()}")
        return False

def start_vm(snapshot_name):
    """Restaura a un snapshot y enciende la VM en modo headless."""
    if not run_vbox_command(["VBoxManage", "snapshot", VM_NAME, "restore", snapshot_name], f"Restaurando VM a '{snapshot_name}'"):
        return False
    if not run_vbox_command(["VBoxManage", "startvm", VM_NAME, "--type", "headless"], "Iniciando VM"):
        return False
    return True

def stop_vm():
    """Apaga la máquina virtual."""
    return run_vbox_command(["VBoxManage", "controlvm", VM_NAME, "poweroff"], "Apagando la VM")

def run_command_in_guest(command, description):
    """Ejecuta un comando dentro de la VM invitada usando cmd.exe."""
    full_command = ["VBoxManage", "guestcontrol", VM_NAME, "run", "--username", GUEST_USER, "--password", GUEST_PASS, "--exe", GUEST_CMD_PATH, "--", "/c", command]
    return run_vbox_command(full_command, description)

def run_powershell_command(command, description):
    """Ejecuta un comando de PowerShell en la VM."""
    full_command = ["VBoxManage", "guestcontrol", VM_NAME, "run", "--username", GUEST_USER, "--password", GUEST_PASS, "--exe", GUEST_POWERSHELL_PATH, "--", "-Command", command]
    return run_vbox_command(full_command, description)

def start_vm_gui():
    """Inicia la VM en modo normal (con interfaz gráfica)."""
    command = ["VBoxManage", "startvm", VM_NAME]
    return run_vbox_command(command, "Iniciando VM en modo gráfico")