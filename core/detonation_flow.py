# main.py
"""
Script final que recolecta los logs en bruto: un log de ProcMon.
"""
import time
from utils import config, messages as msg, cli_utils
from services import vbox_manager as vbox, procmon_wrapper as procmon, sysmon_wrapper as sysmon
from core import file_handler as file
from services import tcpdum_wrapper as tcpw

def run_analysis():
    """Ejecuta el flujo completo de análisis de una muestra."""
    cli_utils.clear_screen()
    msg.title("Detonación de Malware - WAREBOX")

    file.setSignature()

    record = True if input("¿Desea grabar la sesión? esto reduce el consumo de recursos del HOST (s/N): ").lower() == "s" else False
    auto_detonation = True if input("¿Desea detonar automaticamente la muestra? (s/N): ").lower() == "s" else False

    #Crea el directorio de evidencia si no existe
    config.HOST_EVIDENCE_DIR.mkdir(exist_ok=True)

    payload_path = decompress_malware()

    start_vms()

    start_tcpdump()

    #Deshabilitado temporalmente por generación de ruido en log de sysmon.
    #start_procmon()

    if record:
        start_recording()

    detonation(payload_path, auto_detonation)

    if record:
        stop_recording()

    #Deshabilitado temporalmente por generación de ruido en log de sysmon.
    #stop_procmon()
    #copy_procmon_log()

    copy_sysmon_log()

    stop_tcpdump()

    copy_tcpdump_log()
    
    stop_sandbox()
    msg.line_break(2)
    msg.finishing("¡Análisis del malware completado!")
    msg.info(f"Los archivos de evidencia se encuentran en: {config.HOST_EVIDENCE_DIR}")
    msg.wait_key()

def decompress_malware():
    #Descomprime la muestra en el host para luego copiarla a la VM
    msg.decompressing("Descomprimiendo la muestra")
    zip_path = config.HOST_MALWARE_DIR / config.ZIP_FILENAME
    payload_path = file.decompress_sample_on_host(zip_path, config.COMPRESS_KEY, config.HOST_TEMP_DIR, config.PAYLOAD_NAME)
    if not payload_path: return

    return payload_path

def start_vms():
    """ Función que arranca las máquinas virtuales necesarias"""
    #Arrancar la VM de DEBIAN
    if not vbox.restore_start_vm(config.NETWORK_VM_NAME, config.NETWORK_SNAPSHOT_NAME): return
    msg.starting(f"Se ha iniciado la máquina virtual de red")

    #Restaura el snapshot y arranca la VM WINDOWS
    if not vbox.restore_start_vm_gui(config.VM_NAME, config.SNAPSHOT_NAME): return
    msg.starting(f"Se ha iniciado la máquina sandbox principal")
    msg.waiting(f"Esperando {config.WAIT_START_TIME} segundos para el arranque completo")
    time.sleep(config.WAIT_START_TIME)

def start_tcpdump():
    tcpw.start_tcpdump(config.NETWORK_VM_NAME, config.NETWORK_GUEST_USER, config.NETWORK_GUEST_PASS, 10000)
    msg.done("Se ha iniciado la captura de paquetes TCPDUMP.")

def start_recording():
    # Iniciar grabación de pantalla (la VM ya debe estar corriendo)
    msg.recording("Iniciando grabación de pantalla de la VM")
    if not vbox.start_vm_recording(config.VM_NAME):
        stop_sandbox()
        return

def start_procmon():
    # Iniciar Monitoreo
    if not procmon.start_capture():
        vbox.stop_vm_recording(config.VM_NAME)
        stop_sandbox()
        return
    
def detonation(payload_path, auto_detonation):
    # Despliegue y Detonación
    guest_payload_path = config.GUEST_PAYLOAD_PATH_TEMPLATE.format(payload_name=config.PAYLOAD_NAME)
    if not file.copy_to_guest(payload_path, guest_payload_path):
        vbox.stop_vm_recording(config.VM_NAME)
        stop_sandbox()
        return
    file.remove_from_host(payload_path)

    if auto_detonation:
        if not vbox.run_command_in_guest(guest_payload_path, f"Detonando payload '{config.PAYLOAD_NAME}'"):
            msg.warning("La detonación del payload podría haber fallado, se procederá a recolectar los logs")

        msg.waiting(f"Esperando {config.WAIT_MALWARE_TIME} segundos para que el malware actúe")
        time.sleep(config.WAIT_MALWARE_TIME)

    else:
        msg.line_break(1)
        msg.separation_specific_line("virus")
        print("La muestra se encuentra en el Escritorio de la VM, ejecute y realice las pruebas." \
            "\nCuando haya terminado vuelva a este terminal y presione cualquier tecla para continuar.")
        msg.separation_specific_line("virus")
        msg.wait_key()

def stop_procmon():
    # Detener Monitoreo
    if not procmon.stop_capture():
        stop_sandbox()
        return

    msg.waiting(f"Esperando {config.WAIT_WRITE_FILES_TIME} segundos para que los archivos de log se escriban")
    time.sleep(config.WAIT_WRITE_FILES_TIME)

def copy_procmon_log():
    if not file.copy_from_guest(config.VM_NAME, config.GUEST_USER, config.GUEST_PASS, config.GUEST_PROCMON_LOG, config.HOST_EVIDENCE_DIR):
        stop_sandbox()
        return

def copy_sysmon_log():
    sysmon.copy_from_guest(config.VM_NAME, config.GUEST_USER, config.GUEST_PASS)

def stop_tcpdump():
    tcpw.stop_tcpdump(config.NETWORK_VM_NAME, config.NETWORK_GUEST_USER, config.NETWORK_GUEST_PASS)

def copy_tcpdump_log():
    if not file.copy_from_guest(config.NETWORK_VM_NAME, config.NETWORK_GUEST_USER, config.NETWORK_GUEST_PASS, config.NETWORK_TCPDUMP_LOG, config.HOST_EVIDENCE_DIR):
        stop_sandbox()
        return
    file.rename_tcpdump_log()

def stop_recording():
    msg.recording("Deteniendo grabación de pantalla de la VM")
    vbox.stop_vm_recording(config.VM_NAME)

def stop_sandbox():
    """ Función que detiene todas las máquinas virtuales"""
    vbox.stop_vm(config.VM_NAME)
    vbox.stop_vm(config.NETWORK_VM_NAME)

if __name__ == "__main__":
    run_analysis()