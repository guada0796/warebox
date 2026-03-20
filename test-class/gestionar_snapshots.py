# -*- coding: utf-8 -*-

"""
Script para gestionar los snapshots de una máquina virtual en VirtualBox.
Permite crear, restaurar, eliminar y listar snapshots de forma interactiva.
"""

import subprocess
import sys
from config import *

def ejecutar_comando(comando):
    """
    Ejecuta un comando de VBoxManage y maneja los posibles errores.
    Retorna True si tuvo éxito, False si falló.
    """
    try:
        subprocess.run(comando, check=True, capture_output=True, text=True)
        return True
    except FileNotFoundError:
        print("❌ Error: No se encontró el comando 'VBoxManage'.")
        print("Asegúrate de que VirtualBox está instalado y en el PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar el comando.")
        print("Detalles del error de VirtualBox:")
        print(e.stderr)
        return False

def crear_snapshot():
    """Pide un nombre y crea un snapshot."""
    nombre_snapshot = input("Introduce el nombre para el nuevo snapshot: ")
    if not nombre_snapshot:
        print("El nombre no puede estar vacío.")
        return
        
    print(f"\nCreando snapshot '{nombre_snapshot}' para la VM '{VM_NAME}'...")
    comando = ["VBoxManage", "snapshot", VM_NAME, "take", nombre_snapshot]
    
    if ejecutar_comando(comando):
        print(f"✅ ¡Éxito! Snapshot '{nombre_snapshot}' creado.")

def restaurar_snapshot():
    """Pide un nombre y restaura a ese snapshot."""
    nombre_snapshot = input("Introduce el nombre del snapshot a restaurar: ")
    if not nombre_snapshot:
        print("El nombre no puede estar vacío.")
        return
        
    print(f"\nRestaurando la VM '{VM_NAME}' al snapshot '{nombre_snapshot}'...")
    comando = ["VBoxManage", "snapshot", VM_NAME, "restore", nombre_snapshot]
    
    if ejecutar_comando(comando):
        print(f"✅ ¡Éxito! VM restaurada al estado de '{nombre_snapshot}'.")

def eliminar_snapshot():
    """Pide un nombre y elimina ese snapshot."""
    nombre_snapshot = input("Introduce el nombre del snapshot a ELIMINAR: ")
    if not nombre_snapshot:
        print("El nombre no puede estar vacío.")
        return
        
    confirmacion = input(f"¿Estás seguro de que quieres eliminar permanentemente el snapshot '{nombre_snapshot}'? (s/N): ")
    if confirmacion.lower() != 's':
        print("Operación cancelada.")
        return

    print(f"\nEliminando snapshot '{nombre_snapshot}' de la VM '{VM_NAME}'...")
    comando = ["VBoxManage", "snapshot", VM_NAME, "delete", nombre_snapshot]
    
    if ejecutar_comando(comando):
        print(f"✅ ¡Éxito! Snapshot '{nombre_snapshot}' eliminado.")

def listar_snapshots():
    """Muestra una lista de todos los snapshots para la VM."""
    print(f"\n📑 Buscando snapshots para la VM '{VM_NAME}'...")
    comando = ["VBoxManage", "snapshot", VM_NAME, "list"]
    
    try:
        # Para este comando, queremos mostrar la salida directamente.
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
        print("--- Snapshots existentes ---")
        if resultado.stdout:
            print(resultado.stdout)
        else:
            print("No se encontraron snapshots para esta VM.")
        print("--------------------------")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al listar los snapshots.")
        # VBoxManage a veces informa de que no hay snapshots a través de un error.
        if "Could not find a snapshot" in e.stderr:
             print("No se encontraron snapshots para esta VM.")
        else:
            print("Detalles del error de VirtualBox:")
            print(e.stderr)

def mostrar_menu():
    """Muestra el menú principal y gestiona la selección del usuario."""
    while True:
        print("\n--- Gestión de Snapshots ---")
        print(f"VM actual: {VM_NAME}")
        print("1. Crear un snapshot")
        print("2. Restaurar un snapshot")
        print("3. Eliminar un snapshot")
        print("4. Listar snapshots existentes")
        print("5. Salir")
        
        opcion = input("Elige una opción (1-5): ")
        
        if opcion == '1':
            crear_snapshot()
        elif opcion == '2':
            restaurar_snapshot()
        elif opcion == '3':
            eliminar_snapshot()
        elif opcion == '4':
            listar_snapshots()
        elif opcion == '5':
            print("Saliendo del programa.")
            sys.exit(0)
        else:
            print("Opción no válida. Por favor, elige de nuevo.")

if __name__ == "__main__":
    mostrar_menu()