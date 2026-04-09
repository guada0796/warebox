"""
Menu de principal con todas las opciones para gestionar el entorno de detonación, análisis manual y configuración.
"""

import time

from . import change_configuration_menu as ccm
from . import analisys_menu as am
from . import snapshot_menu as sm
from utils import messages as msg

from utils import cli_utils, config
from core import detonation_flow

def show_main_menu():
    """Muestra el menú principal y maneja las opciones del usuario."""
    while True:
        cli_utils.clear_screen()
        msg.title(f"Panel de Control {config.PROJECT_NAME}")
        # --- Parámetros Editables ---
        print("\n📋 Configuración Modificable:")
        print(f"   0. Nombre del snapshot:  {config.SNAPSHOT_NAME}")
        print(f"   1. Nombre de la VM:      {config.VM_NAME}")
        print(f"   2. Usuario (Guest):      {config.GUEST_USER}")
        print(f"   3. Contraseña (Guest):   {config.GUEST_PASS}")
        print(f"   4. Clave del ZIP:        {config.COMPRESS_KEY}")
        print(f"   5. Archivo ZIP:          {config.ZIP_FILENAME}")
        print(f"   6. Payload EXE:          {config.PAYLOAD_EXE_NAME}")
        print(f"   7. Espera Arranque VM:   {config.WAIT_START_TIME}s")
        print(f"   8. Espera Análisis Malware:     {config.WAIT_MALWARE_TIME}s")
        print(f"   9. Espera Escritura Resultados: {config.WAIT_WRITE_FILES_TIME}s")
        
        # --- Parámetros Fijos (Solo Lectura) ---
        print("\nℹ️  Valores por defecto (Solo Lectura):")
        print(f"   - Directorio de Tools (Guest): {config.GUEST_TOOLS_DIR}")
        print(f"   - Directorio de Logs (Guest):  {config.GUEST_LOG_DIR}")
        print(f"   - Directorio de Malware (Host): {config.HOST_MALWARE_DIR}")
        print(f"   - Directorio de Evidencia (Host): {config.HOST_EVIDENCE_DIR}")

        print("\n▶️  Opciones:")
        print("   c. Cambiar configuración de análisis")
        print("   d. Detonar la muestra actual")
        print("   a. Analizar resultados (Manual)")
        print("   g. Gestionar Snapshots de la VM")
        print("   s. Salir")
        
        choice = input("\nSeleccione una opción: ").lower()

        if choice == 'd':
            msg.line_break()
            msg.starting("Iniciando proceso de detonación automática")
            time.sleep(1)
            detonation_flow.run_analysis()
            msg.line_break()
            msg.done("Proceso de detonación automática finalizado")
            msg.separation_line()
        
        elif choice == 'a':
            am.show_analysis_menu()

        elif choice == 'c':
            ccm.change_configuration_menu()

        elif choice == 'g':
            sm.show_snapshot_menu()

        elif choice == 's':
            msg.cleaning("Saliendo")
            break
        else:
            msg.error("Opción no válida. Inténtelo de nuevo")
            time.sleep(1)
