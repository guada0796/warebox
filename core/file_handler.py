# file_handler.py
"""
Módulo para manejar la descompresión de muestras, transferencia y acciones de archivos en el HOST.
"""
import subprocess, os, time, importlib
#from pathlib import Path
from utils import config
from services import vbox_manager as vbox

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
    command = ["VBoxManage", "guestcontrol", config.VM_NAME, "copyto", str(host_path), guest_path, "--username", config.GUEST_USER, "--password", config.GUEST_PASS]
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
        "VBoxManage", "guestcontrol", config.VM_NAME, "copyfrom",
        guest_path,
        str(host_destination_path), # Usamos la ruta completa y correcta
        "--username", config.GUEST_USER, "--password", config.GUEST_PASS
    ]
    return vbox.run_vbox_command(command, f"Descargando evidencia '{file_name}'")

def update_config_file(updates):
    """
    Lee el archivo config.py, actualiza las claves especificadas y lo reescribe.
    """
    config_path = "utils/config.py"
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
