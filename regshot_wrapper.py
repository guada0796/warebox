# regshot_wrapper.py
"""
Módulo dedicado a controlar RegShot usando PowerShell para ser consistente
con la lógica funcional.
"""
from config import GUEST_REGSHOT_PATH, GUEST_REGSHOT_HIVE_1, GUEST_REGSHOT_HIVE_2
import vbox_manager as vbox

def take_snapshot_1():
    """Toma la primera foto y la guarda en un archivo .hive."""
    regshot_cmd = f'& "{GUEST_REGSHOT_PATH}" /s "{GUEST_REGSHOT_HIVE_1}"'
    return vbox.run_powershell_command(regshot_cmd, "Tomando 1er snapshot con RegShot")

def take_snapshot_2():
    """Toma la segunda foto y la guarda en un archivo .hive."""
    regshot_cmd = f'& "{GUEST_REGSHOT_PATH}" /s "{GUEST_REGSHOT_HIVE_2}"'
    return vbox.run_powershell_command(regshot_cmd, "Tomando 2do snapshot con RegShot")