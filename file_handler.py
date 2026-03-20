# file_handler.py
"""
Módulo para manejar la descompresión de muestras y la transferencia de archivos.
"""
import subprocess
import os
from pathlib import Path
from config import VM_NAME, GUEST_USER, GUEST_PASS
import vbox_manager as vbox

def decompress_sample_on_host(zip_path, password, extract_dir, payload_name):
    """Descomprime un archivo .zip en el host usando 7z."""
    print(f"⚙️  Descomprimiendo '{zip_path.name}' en el host con '7z'...")
    extract_dir.mkdir(exist_ok=True)
    command = ["7z", "x", f"-p{password}", f"-o{str(extract_dir)}", str(zip_path), payload_name, "-y"]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("✅ ¡Éxito!")
        return extract_dir / payload_name
    except Exception as e:
        print(f"❌ ERROR al descomprimir en el host: {e}")
        return None

def copy_to_guest(host_path, guest_path):
    """Copia un archivo desde el host a la VM."""
    command = ["VBoxManage", "guestcontrol", VM_NAME, "copyto", str(host_path), guest_path, "--username", GUEST_USER, "--password", GUEST_PASS]
    return vbox.run_vbox_command(command, f"Copiando '{host_path.name}' a la VM")

def remove_from_host(file_path):
    """Borra un archivo del host."""
    print(f"⚙️  Borrando archivo temporal '{file_path.name}' del host...")
    try:
        os.remove(file_path)
        print("✅ ¡Éxito!")
    except OSError as e:
        print(f"❌ ERROR al borrar el archivo del host: {e}")

# --- CORRECCIÓN DEFINITIVA APLICADA AQUÍ ---
def copy_from_guest(guest_path, host_dir):
    """Copia un archivo desde la VM al host, especificando la ruta completa de destino."""
    # Extraemos solo el nombre del archivo de la ruta del guest.
    file_name = guest_path.split('\\')[-1]
    # Construimos la ruta de destino completa en el host.
    host_destination_path = host_dir / file_name
    
    command = [
        "VBoxManage", "guestcontrol", VM_NAME, "copyfrom",
        guest_path,
        str(host_destination_path), # Usamos la ruta completa y correcta
        "--username", GUEST_USER, "--password", GUEST_PASS
    ]
    return vbox.run_vbox_command(command, f"Descargando evidencia '{file_name}'")