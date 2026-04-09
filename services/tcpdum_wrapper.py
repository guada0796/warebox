from . import vbox_manager as vbox

def start_tcpdump(vm_name, user, password, packet_limit=10000):
    guest_path = "/home/ucjc/warebox-capture.pcap"

    command = [
        "VBoxManage", "guestcontrol", vm_name, "run",
        "--username", user,
        "--password", password,
        "--exe", "/usr/bin/tcpdump", "--",
        "-i", "enp0s3",     # interfaz de red
        "-n",               # no resolver DNS
        "-U",               # escritura en tiempo real
        "-c", str(packet_limit),  # límite de paquetes
        "-w", guest_path    # archivo de salida
    ]

    import subprocess
    return subprocess.Popen(command)

def stop_tcpdump(vm_name, user, password):
    command = [
        "VBoxManage", "guestcontrol", vm_name, "run",
        "--username", user,
        "--password", password,
        "--exe", "/usr/bin/pkill",
        "--",
        "-SIGINT",
        "tcpdump"
    ]
    vbox.run_vbox_command(command, "Deteniendo captura de paquetes de red")