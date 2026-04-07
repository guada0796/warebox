# warebox.py
"""
Inicio del entorno Warebox.
"""

from cli import main_menu

# Añadimos la función clear_screen a config para que sea accesible desde otros módulos si es necesario
#config.clear_screen = clear_screen

if __name__ == "__main__":
    main_menu.show_main_menu()
