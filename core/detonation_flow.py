# main.py
"""
Script final que recolecta los logs en bruto: un log de ProcMon.
"""
import time
from utils import config
from services import vbox_manager as vbox
from services import procmon_wrapper as procmon
from core import file_handler as file

def run_analysis():
    """Ejecuta el flujo completo de análisis de una muestra."""
    
    config.HOST_EVIDENCE_DIR.mkdir(exist_ok=True)
    zip_path = config.HOST_MALWARE_DIR / config.ZIP_FILENAME
    payload_path = file.decompress_sample_on_host(zip_path, config.COMPRESS_KEY, config.HOST_TEMP_DIR, config.PAYLOAD_EXE_NAME)
    if not payload_path: return

    if not vbox.restore_start_vm_gui(config.SNAPSHOT_NAME): return
    print(f"⏱️  Esperando {config.WAIT_START_TIME} segundos para el arranque completo...")
    time.sleep(config.WAIT_START_TIME)

    # Iniciar grabación de pantalla (la VM ya debe estar corriendo)
    if not vbox.start_vm_recording():
        vbox.stop_vm()
        return

    # --- Iniciar Monitoreo ---
    if not procmon.start_capture():
        vbox.stop_vm_recording()
        vbox.stop_vm()
        return

    # --- Despliegue y Detonación ---
    guest_payload_path = config.GUEST_PAYLOAD_PATH_TEMPLATE.format(payload_name=config.PAYLOAD_EXE_NAME)
    if not file.copy_to_guest(payload_path, guest_payload_path):
        vbox.stop_vm_recording()
        vbox.stop_vm()
        return
    file.remove_from_host(payload_path)

    if not vbox.run_command_in_guest(guest_payload_path, f"Detonando payload '{config.PAYLOAD_EXE_NAME}'"):
        print("⚠️  La detonación del payload podría haber fallado, se procederá a recolectar los logs.")

    print(f"⏳ Esperando {config.WAIT_MALWARE_TIME} segundos para que el malware actúe...")
    time.sleep(config.WAIT_MALWARE_TIME)

    # --- Detener Monitoreo ---
    if not procmon.stop_capture():
        vbox.stop_vm_recording()
        vbox.stop_vm()
        return

    print(f"⏱️  Esperando {config.WAIT_WRITE_FILES_TIME} segundos para que los archivos de log se escriban...")
    time.sleep(config.WAIT_WRITE_FILES_TIME)

    # --- Recolección de Evidencias en Bruto ---
    if not file.copy_from_guest(config.GUEST_PROCMON_LOG, config.HOST_EVIDENCE_DIR):
        vbox.stop_vm_recording()
        vbox.stop_vm()
        return

    vbox.stop_vm_recording()

    # --- Limpieza Final ---
    vbox.stop_vm()
    print("\n\n🎉 ¡Análisis del malware completado! 🎉")
    print(f"Los archivos de evidencia (.pml, .hivu y .txt) se encuentran en: {config.HOST_EVIDENCE_DIR}")

if __name__ == "__main__":
    run_analysis()