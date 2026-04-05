# snapshot_manager.py
"""
Módulo para gestionar las operaciones de snapshots de la máquina virtual.
"""
import subprocess
from utils import config
from services import vbox_manager as vbox

def create_snapshot():
    """Pide un nombre y crea un snapshot."""
    name = input("Introduce el nombre para el nuevo snapshot: ")
    if not name:
        print("❌ El nombre no puede estar vacío.")
        return
    
    command = ["VBoxManage", "snapshot", config.VM_NAME, "take", name]
    if vbox.run_vbox_command(command, f"Creando snapshot '{name}'"):
        print(f"✅ ¡Éxito! Snapshot '{name}' creado.")

def restore_snapshot():
    """Pide un nombre y restaura a ese snapshot."""
    name = input("Introduce el nombre del snapshot a restaurar: ")
    if not name:
        print("❌ El nombre no puede estar vacío.")
        return
        
    command = ["VBoxManage", "snapshot", config.VM_NAME, "restore", name]
    if vbox.run_vbox_command(command, f"Restaurando al snapshot '{name}'"):
        print(f"✅ ¡Éxito! VM restaurada al estado de '{name}'.")

def delete_snapshot():
    """Pide un nombre y elimina ese snapshot."""
    name = input("Introduce el nombre del snapshot a ELIMINAR: ")
    if not name:
        print("❌ El nombre no puede estar vacío.")
        return
        
    confirmation = input(f"¿Estás seguro de que quieres eliminar permanentemente el snapshot '{name}'? (s/N): ")
    if confirmation.lower() != 's':
        print("Operación cancelada.")
        return

    command = ["VBoxManage", "snapshot", config.VM_NAME, "delete", name]
    if vbox.run_vbox_command(command, f"Eliminando snapshot '{name}'"):
        print(f"✅ ¡Éxito! Snapshot '{name}' eliminado.")

def list_snapshots():
    """Muestra una lista de todos los snapshots para la VM."""
    print(f"\n📑 Buscando snapshots para la VM '{config.VM_NAME}'...")

    command = ["VBoxManage", "snapshot", config.VM_NAME, "list"]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        print("--- Snapshots existentes ---")
        if result.stdout:
            print(result.stdout.strip())
        else:
            print("No se encontraron snapshots para esta VM.")
        print("--------------------------")

    except subprocess.CalledProcessError as e:
        if "Could not find a snapshot" in e.stderr:
             print("\nNo se encontraron snapshots para esta VM.")
        else:
            print(f"❌ Error al buscar los snapshots: {e.stderr.strip()}")
