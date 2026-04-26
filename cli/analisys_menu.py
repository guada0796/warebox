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
        print(f"   1. Nuevo Análisis de la Última Detonación (desde el snapshot base). Firma: <{config.TIMESTAMP_SIGNATURE}>")
        print("   2. Abrir Análisis Guardado (desde un snapshot existente)")
        print("   b. Volver al menú principal")

        choice = input("\nSeleccione una opción: ").lower()

        if choice == '1':
            ma.new_analysis()
        elif choice == '2':
            ma.open_analysis()
        elif choice == 'b':
            break
        else:
            print("❌ Opción no válida. Inténtelo de nuevo."); time.sleep(1)