"""
Menu de principal con todas las opciones para gestionar el entorno de detonación, análisis manual y configuración.
"""

import time
import os

from . import change_configuration_menu as ccm
from . import analisys_menu as am
from . import snapshot_menu as sm
from utils import messages as msg

from utils import cli_utils, config
from core import detonation_flow, automatic_analyzer as aa, file_handler

def show_main_menu():
    """Muestra el menú principal y maneja las opciones del usuario."""
    while True:
        cli_utils.clear_screen()
        msg.title(f"Panel de Control {config.PROJECT_NAME}")
        # --- Parámetros Editables ---
        msg.line_break(1)
        msg.list("Configuración Modificable:")
        msg.item(f"0. Nombre del snapshot:  {config.SNAPSHOT_NAME}")
        msg.item(f"1. Nombre de la VM:      {config.VM_NAME}")
        msg.item(f"2. Usuario (Guest):      {config.GUEST_USER}")
        msg.item(f"3. Contraseña (Guest):   {config.GUEST_PASS}")
        msg.item(f"4. Clave del ZIP:        {config.COMPRESS_KEY}")
        msg.item(f"5. Archivo ZIP:          {config.ZIP_FILENAME}")
        msg.item(f"6. Payload:              {config.PAYLOAD_NAME}")
        msg.item(f"7. Espera Arranque VM:   {config.WAIT_START_TIME}s")
        msg.item(f"8. Espera Análisis Malware:     {config.WAIT_MALWARE_TIME}s")
        msg.item(f"9. Espera Escritura Resultados: {config.WAIT_WRITE_FILES_TIME}s")
        
        # --- Parámetros Fijos (Solo Lectura) ---
        msg.line_break(1)
        msg.info("Valores por defecto (Solo Lectura):")
        msg.item(f"Directorio de Tools (Guest): {config.GUEST_TOOLS_DIR}")
        msg.item(f"Directorio de Logs (Guest):  {config.GUEST_LOG_DIR}")
        msg.item(f"Directorio de Malware (Host): {config.HOST_MALWARE_DIR}")
        msg.item(f"Directorio de Evidencia (Host): {config.HOST_EVIDENCE_DIR}")
        msg.item(f"Firma de Tiempo Actual: {config.TIMESTAMP_SIGNATURE}")

        msg.line_break(1)
        msg.options("Opciones:")
        msg.item("c. Cambiar configuración de análisis")
        msg.item("d. Detonar una muestra")
        msg.item("a. Analizar resultados (Manual)")
        msg.item("h. Analizar resultados (Automático)")
        msg.item("g. Gestionar Snapshots de la VM")
        msg.item("s. Salir")
        
        choice = input("\nSeleccione una opción: ").lower()

        if choice == 'd':
            current_payload = True if input(f"¿Desea detonar la muestra actual ({config.PAYLOAD_NAME})? (s/N): ").lower() == 's' else False

            if current_payload or select_payload():
                msg.line_break(1)
                msg.starting("Iniciando proceso de detonación automática")
                time.sleep(1)
                detonation_flow.run_analysis()
                msg.line_break(1)
                msg.done("Proceso de detonación automática finalizado")
                msg.separation_detault_line()
                
        
        elif choice == 'a':
            am.show_analysis_menu()

        elif choice == 'c':
            ccm.change_configuration_menu()

        elif choice == 'g':
            sm.show_snapshot_menu()

        elif choice == 'h':
            aa.hayabusa_analysis()

        elif choice == 's':
            msg.cleaning("Saliendo")
            break
        else:
            msg.error("Opción no válida. Inténtelo de nuevo")
            time.sleep(1)

def select_payload():
    # Obtener lista de archivos .zip
    zips = [f for f in os.listdir(config.HOST_MALWARE_DIR) if f.lower().endswith(".zip")]
    msg.line_break(1)
    if not zips:
        msg.error("No se encontraron archivos .zip en el directorio.")
        msg.wait_key()
        return False

    # Mostrar opciones
    msg.options("Muestras disponibles:")
    for i, archivo in enumerate(zips, start=1):
        msg.item(f"{i}. {archivo}")
    msg.item("b. Volver al menú principal")
    msg.line_break(1)
    # Pedir selección al usuario
    while True:
        try:
            choice = input("Elige la muestra: ")
            if choice == 'b':
                return False

            payloadNumber = int(choice)    
            if 1 <= payloadNumber <= len(zips):
                seleccionado = zips[payloadNumber - 1]
                extension = input("¿Qué extensión tiene la muestra (exe, bin, dll...)?: ").lower()
                updates = {}
                updates['ZIP_FILENAME'] = seleccionado
                updates['PAYLOAD_NAME'] = seleccionado.replace(".zip", "."+extension)
                file_handler.update_config_file(updates)
                return True
            else:
                msg.line_break(1)
                msg.error("Número fuera de rango. Intenta de nuevo.")
        except ValueError:
            msg.line_break(1)
            msg.error("Entrada inválida. Debes ingresar un número.")
