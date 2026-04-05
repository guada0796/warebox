"""
Módulo de utilidades para la interfaz de línea de comandos (CLI) del proyecto WAREBOX.
"""

import os
from datetime import datetime

def clear_screen():
    """Limpia la pantalla de la consola."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_current_timestamp():
    """Devuelve la fecha y hora actual en un formato para nombres de archivo."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")