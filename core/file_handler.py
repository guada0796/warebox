# file_handler.py
"""
Módulo para manejar la descompresión de muestras, transferencia y acciones de archivos en el HOST.
"""
from pathlib import Path
import subprocess, os, time, importlib
import hashlib
from utils import config, messages as msg, cli_utils as cli
from services import vbox_manager as vbox

def decompress_sample_on_host(zip_path, password, extract_dir, payload_name):
    """Descomprime un archivo .zip en el host usando 7z."""
    msg.processing(f"Descomprimiendo '{zip_path.name}' en el host con '7z'")
    extract_dir.mkdir(exist_ok=True)
    command = ["7z", "x", f"-p{password}", f"-o{str(extract_dir)}", str(zip_path), payload_name, "-y"]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        msg.done("Descompresión completada")
        return extract_dir / payload_name
    except Exception as e:
        msg.error(f"Error al descomprimir en el host: {e}")
        return None

def copy_to_guest(host_path, guest_path):
    """Copia un archivo desde el host a la VM."""
    command = ["VBoxManage", "guestcontrol", config.VM_NAME, "copyto", str(host_path), guest_path, "--username", config.GUEST_USER, "--password", config.GUEST_PASS]
    return vbox.run_vbox_command(command, f"Copiando '{host_path.name}' a la VM")

def remove_from_host(file_path):
    """Borra un archivo del host."""
    msg.cleaning(f"Borrando archivo temporal '{file_path.name}' del host")
    try:
        os.remove(file_path)
        msg.done("Archivo borrado del host")
    except OSError as e:
        msg.error(f"Error al borrar el archivo del host: {e}")

# --- CORRECCIÓN DEFINITIVA APLICADA AQUÍ ---
def copy_from_guest(vm_name, vm_guest_user, vm_guest_pass, guest_path, host_dir):
    """Copia un archivo desde la VM al host, especificando la ruta completa de destino."""
    
    # Normalizamos la ruta: reemplazamos las '\' de Windows por '/' para hacer el split de forma segura en ambos OS
    file_name = guest_path.replace('\\', '/').split('/')[-1]
    file_name = file_name.replace("$fch$", config.TIMESTAMP_SIGNATURE)
    
    # Construimos la ruta de destino completa en el host
    host_destination_path = Path(host_dir) / file_name
    
    command = [
        "VBoxManage", "guestcontrol", vm_name, "copyfrom",
        guest_path,
        str(host_destination_path), # Usamos la ruta completa y correcta
        "--username", vm_guest_user, "--password", vm_guest_pass
    ]
    return vbox.run_vbox_command(command, f"Descargando evidencia <{file_name}>")

def setSignature():
    """Función para establecer la firma de tiempo que se usará en los nombres de los logs."""
    signature = cli.get_current_timestamp()
    updates = {}
    updates['TIMESTAMP_SIGNATURE'] = signature
    update_config_file(updates)
    msg.done(f"Firma temporal establecida: {signature}")

def setSHA256(payload_path):
    """Función para establecer el SHA256 de la muestra."""
    sha256 = calculate_sha256(payload_path)
    updates = {}
    updates['PAYLOAD_SHA256'] = sha256
    update_config_file(updates)
    msg.done(f"SHA256 de la muestra descomprimida: {sha256}")

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

def rename_tcpdump_log():
    """Función para renombrar el archivo de log de tcpdump con la firma temporal."""
    original_path = config.HOST_TCPDUMP_OLD_LOG_DIR
    new_path_str = str(config.HOST_TCPDUMP_LOG_DIR)
    new_path_str = new_path_str.replace("$fch$", config.TIMESTAMP_SIGNATURE)
    new_path = Path(new_path_str)
    if original_path.exists():
        file_rename(original_path, new_path)
    else:
        msg.warning("El archivo de log de tcpdump no existe para renombrar.")

def file_rename(current_path, new_path):
    try:
        os.rename(current_path, new_path)
        print("Archivo renombrado correctamente.")
    except FileNotFoundError:
        print("El archivo no existe.")
    except FileExistsError:
        print("Ya existe un archivo con el nuevo nombre.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

def get_timestamp_signature_file_name(file_path):
    filename = file_path.name.replace("$fch$", config.TIMESTAMP_SIGNATURE)
    host_file = file_path.with_name(filename)
    return host_file

def calculate_sha256(file_path):
    """Calcula el hash SHA256 de un archivo."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()