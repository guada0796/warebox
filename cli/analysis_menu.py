"""
Menu de análisis manual para seleccionar el modo de revisión de resultados. 
"""

import time

from utils import cli_utils, messages as msg, config
from core import manual_analyzer as ma

def show_analysis_menu():
    """Muestra el menú principal de análisis manual."""
    while True:
        
        cli_utils.clear_screen()
        msg.title("Menú de Análisis Manual")
        msg.options("Opciones:")
        msg.item(f"1. Nuevo Análisis de la Última Detonación (desde el snapshot base). Firma: <{config.TIMESTAMP_SIGNATURE}>")
        msg.item(f"2. Abrir Análisis Guardado (desde un snapshot existente)")
        msg.item(f"b. Volver al menú principal")

        choice = input("\nSeleccione una opción: ").lower()

        if choice == 'b':
            return

        if choice == '1':
            if ma.setup_new_analysis():
                input("\n--- Presione Enter aquí cuando haya finalizado su análisis en la VM. ---")
                save = input("\n¿Desea guardar el estado actual de su análisis como un nuevo snapshot? (s/N): ").lower()
                if save == 's':
                    from services import snapshot_manager
                    snapshot_manager.create_snapshot()
                
                from services import vbox_manager as vbox
                vbox.stop_vm(config.VM_NAME)
                msg.done("Análisis finalizado")
                time.sleep(2)
        elif choice == '2':
            from services import snapshot_manager, vbox_manager as vbox
            snapshot_manager.list_snapshots()
            snapshot_to_open = input("\nIntroduce el nombre exacto del snapshot de análisis que deseas abrir: ")
            if not snapshot_to_open:
                msg.error("El nombre no puede estar vacío")
                time.sleep(2)
                continue
                
            if ma.restore_analysis(snapshot_to_open):
                msg.info("Presione Enter aquí cuando haya finalizado su análisis en la VM")
                msg.line_break(1)
                input()
                
                save = input("\n¿Desea guardar los cambios (actualizar el timestamp del snapshot)? (s/N): ").lower()
                if save == 's':
                    base_name = snapshot_to_open.rsplit('_', 1)[0]
                    final_snapshot_name = f"{base_name}_{cli_utils.get_current_timestamp()}"
                    vbox.run_vbox_command(["VBoxManage", "snapshot", config.VM_NAME, "take", final_snapshot_name], f"Creando snapshot actualizado '{final_snapshot_name}'")

                vbox.stop_vm(config.VM_NAME)
                msg.done("Análisis finalizado")
                time.sleep(2)
        else:
            msg.error("Opción no válida. Inténtelo de nuevo."); time.sleep(1)