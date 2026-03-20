# menu_principal.py
"""
Interfaz de usuario en consola para gestionar y ejecutar el sandbox de análisis.
"""
import time
import importlib
import os

# Importamos nuestros módulos existentes
import config
import main as sandbox_main
import snapshot_manager 
import manual_analyzer # Importamos el nuevo módulo

def clear_screen():
    """Limpia la pantalla de la consola."""
    os.system('cls' if os.name == 'nt' else 'clear')

# Añadimos la función clear_screen a config para que sea accesible desde otros módulos
config.clear_screen = clear_screen

def update_config_file(updates):
    """
    Lee el archivo config.py, actualiza las claves especificadas y lo reescribe.
    """
    config_path = "config.py"
    lines = []
    with open(config_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(config_path, 'w', encoding='utf-8') as f:
        for line in lines:
            found_key = next((key for key in updates if line.strip().startswith(key)), None)
            
            if found_key:
                new_value = updates[found_key]
                if isinstance(new_value, str):
                    f.write(f"{found_key} = \"{new_value}\"\n")
                else: # Para números
                    f.write(f"{found_key} = {new_value}\n")
            else:
                f.write(line)
    
    importlib.reload(config)
    print("\n✅ ¡Configuración guardada!")
    time.sleep(1.5)

def show_main_menu():
    """Muestra el menú principal y maneja las opciones del usuario."""
    while True:
        clear_screen()
        print("--- Panel de Control del Sandbox de Análisis ---")
        
        # --- Parámetros Editables ---
        print("\n📋 Configuración Modificable:")
        print(f"   - Nombre de la VM:      {config.VM_NAME}")
        print(f"   - Snapshot:             {config.SNAPSHOT_NAME}")
        print(f"   - Usuario (Guest):      {config.GUEST_USER}")
        print(f"   - Archivo ZIP:          {config.ZIP_FILENAME}")
        
        print("\n▶️  Opciones Principales:")
        print("   d. Detonar la muestra actual (Automático)")
        print("   a. Analizar resultados (Manual)")
        print("   c. Cambiar configuración")
        print("   g. Gestionar Snapshots")
        print("   s. Salir")
        
        choice = input("\nSeleccione una opción: ").lower()

        if choice == 'd':
            print("\n🚀 Iniciando detonación automática...")
            time.sleep(1)
            sandbox_main.run_analysis()
            input("\n--- Análisis finalizado. Presione Enter para volver al menú. ---")
        
        elif choice == 'a':
            manual_analyzer.show_analysis_menu()

        elif choice == 'c':
            change_configuration_menu()

        elif choice == 'g':
            snapshot_manager.show_snapshot_menu()

        elif choice == 's':
            print("Saliendo...")
            break
        else:
            print("❌ Opción no válida. Inténtelo de nuevo.")
            time.sleep(1)

def change_configuration_menu():
    """Muestra el submenú para cambiar la configuración."""
    while True:
        clear_screen()
        print("--- Modificar Configuración ---")
        print(f"   1. Nombre de la VM:      {config.VM_NAME}")
        print(f"   2. Snapshot:             {config.SNAPSHOT_NAME}")
        print(f"   3. Usuario (Guest):      {config.GUEST_USER}")
        print(f"   4. Contraseña (Guest):   {config.GUEST_PASS}")
        print(f"   5. Clave del ZIP:        {config.COMPRESS_KEY}")
        print(f"   6. Archivo ZIP:          {config.ZIP_FILENAME}")
        print(f"   7. Payload EXE:          {config.PAYLOAD_EXE_NAME}")
        print(f"   8. Espera (Arranque):    {config.WAIT_START_TIME}s")
        print(f"   9. Espera (Análisis):    {config.WAIT_MALWARE_TIME}s")
        print(f"  10. Espera (Escritura):   {config.WAIT_WRITE_FILES_TIME}s")
        print("   b. Volver al menú principal")
        
        choice = input("\nElige el número del parámetro a modificar (o 'b' para volver): ").lower()
        
        updates = {}
        try:
            if choice == '1': updates['VM_NAME'] = input("   Nuevo Nombre de la VM: ")
            elif choice == '2': updates['SNAPSHOT_NAME'] = input("   Nuevo Nombre del Snapshot: ")
            elif choice == '3': updates['GUEST_USER'] = input("   Nuevo Usuario (Guest): ")
            elif choice == '4': updates['GUEST_PASS'] = input("   Nueva Contraseña (Guest): ")
            elif choice == '5': updates['COMPRESS_KEY'] = input("   Nueva Clave del ZIP: ")
            elif choice == '6': updates['ZIP_FILENAME'] = input("   Nuevo Archivo ZIP: ")
            elif choice == '7': updates['PAYLOAD_EXE_NAME'] = input("   Nuevo Payload EXE: ")
            elif choice == '8': updates['WAIT_START_TIME'] = int(input("   Nuevo Tiempo de Arranque (s): "))
            elif choice == '9': updates['WAIT_MALWARE_TIME'] = int(input("   Nuevo Tiempo de Análisis (s): "))
            elif choice == '10': updates['WAIT_WRITE_FILES_TIME'] = int(input("   Nuevo Tiempo de Escritura (s): "))
            elif choice == 'b': break
            else:
                print("❌ Opción no válida.")
                time.sleep(1)
                continue
        except ValueError:
            print("❌ Error: Debes introducir un número entero para los tiempos de espera.")
            time.sleep(2)
            continue
            
        if updates:
            update_config_file(updates)
            break

if __name__ == "__main__":
    show_main_menu()