# warebox.py
"""
Inicio del entorno Warebox.
"""

from cli import menu_principal

# Añadimos la función clear_screen a config para que sea accesible desde otros módulos si es necesario
#config.clear_screen = clear_screen

if __name__ == "__main__":
    menu_principal.show_main_menu()
