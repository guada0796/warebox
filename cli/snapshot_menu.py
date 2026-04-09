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
        print(f"VM actual: {config.VM_NAME}")
        print("   1. Listar snapshots existentes")
        print("   2. Crear un snapshot")
        print("   3. Restaurar un snapshot")
        print("   4. Eliminar un snapshot")
        print("   b. Volver al menú principal")
        
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
            print("❌ Opción no válida. Inténtelo de nuevo.")
        
        if choice in ['1', '2', '3', '4']:
            input("\n--- Presione Enter para continuar ---")