"""
Menu que permite la gestión de los snapshots de la máquina virtual.
"""

from utils import config, cli_utils, messages as msg
from services import snapshot_manager as sm

def show_snapshot_menu():
    """Muestra el menú de gestión de snapshots."""
    while True:
        # --- CORRECCIÓN: Llamamos a la función desde 'config' ---
        cli_utils.clear_screen()
        msg.title("Gestión de Snapshots")
        msg.done(f"VM actual: {config.VM_NAME}")
        msg.options("Opciones:")
        msg.item(f"1. Listar snapshots existentes")
        msg.item(f"2. Crear un snapshot")
        msg.item(f"3. Restaurar un snapshot")
        msg.item(f"4. Eliminar un snapshot")
        msg.item(f"b. Volver al menú principal")
        
        choice = input("\nElige una opción: ").lower()
        
        if choice == '1':
            sm.list_snapshots()
        elif choice == '2':
            sm.create_snapshot()
        elif choice == '3':
            sm.restore_snapshot()
        elif choice == '4':
            sm.delete_snapshot()
        elif choice == 'b':
            break
        else:
            msg.error("Opción no válida. Inténtelo de nuevo.")
        
        if choice in ['1', '2', '3', '4']:
            msg.wait_key()