# change_configuration_menu.py

"""
Menu para cambiar la configuración del entorno de detonación. 
"""

import time

from utils import cli_utils, config, messages as msg
from core import file_handler

def change_configuration_menu():
    """Muestra el submenú para cambiar la configuración."""
    while True:
        cli_utils.clear_screen()
        msg.title("Modificar Configuración")
        # Mostramos los parámetros para facilitar la elección
        msg.options("Opciones:")
        msg.item(f"0. Nombre del snapshot:  {config.SNAPSHOT_NAME}")
        msg.item(f"1. Nombre de la VM:      {config.VM_NAME}")
        msg.item(f"2. Usuario (Guest):      {config.GUEST_USER}")
        msg.item(f"3. Contraseña (Guest):   {config.GUEST_PASS}")
        msg.item(f"4. Clave del ZIP:        {config.COMPRESS_KEY}")
        msg.item(f"5. Archivo ZIP:          {config.ZIP_FILENAME}")
        msg.item(f"6. Payload EXE:          {config.PAYLOAD_EXE_NAME}")
        msg.item(f"7. Espera Arranque VM:   {config.WAIT_START_TIME}s")
        msg.item(f"8. Espera Análisis Malware:     {config.WAIT_MALWARE_TIME}s")
        msg.item(f"9. Espera Escritura Resultados: {config.WAIT_WRITE_FILES_TIME}s")
        msg.item("b. Volver al menú principal")
        
        choice = input("\nElige el número del parámetro a modificar (o 'b' para volver): ").lower()
        
        updates = {}
        try:
            if choice == '0': updates['SNAPSHOT_NAME'] = input("   Nuevo Nombre del Snapshot: ")
            elif choice == '1': updates['VM_NAME'] = input("   Nuevo Nombre de la VM: ")
            elif choice == '2': updates['GUEST_USER'] = input("   Nuevo Usuario (Guest): ")
            elif choice == '3': updates['GUEST_PASS'] = input("   Nueva Contraseña (Guest): ")
            elif choice == '4': updates['COMPRESS_KEY'] = input("   Nueva Clave del ZIP: ")
            elif choice == '5': updates['ZIP_FILENAME'] = input("   Nuevo Archivo ZIP: ")
            elif choice == '6': updates['PAYLOAD_EXE_NAME'] = input("   Nuevo Payload EXE: ")
            elif choice == '7': updates['WAIT_START_TIME'] = int(input("   Nuevo Tiempo de Arranque (s): "))
            elif choice == '8': updates['WAIT_MALWARE_TIME'] = int(input("   Nuevo Tiempo de Análisis (s): "))
            elif choice == '9': updates['WAIT_WRITE_FILES_TIME'] = int(input("   Nuevo Tiempo de Escritura (s): "))
            elif choice == 'b': break
            else:
                msg.error("Opción no válida.")
                time.sleep(1)
                continue
        except ValueError:
            msg.error("Debes introducir un número entero para los tiempos de espera.")
            time.sleep(2)
            continue
            
        if updates:
            file_handler.update_config_file(updates)
            # Después de actualizar, salimos del submenú para ver los cambios en el menú principal
            break