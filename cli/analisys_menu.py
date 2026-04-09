"""
Menu de análisis manual para seleccionar el modo de revisión de resultados. 
"""

import time

from utils import cli_utils, messages as msg
from core import manual_analyzer as ma

def show_analysis_menu():
    """Muestra el menú principal de análisis manual."""
    while True:
        
        cli_utils.clear_screen()
        msg.title("Menú de Análisis Manual")
        print("   1. Iniciar un Nuevo Análisis (desde el snapshot base)")
        print("   2. Abrir un Análisis Guardado (desde un snapshot existente)")
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