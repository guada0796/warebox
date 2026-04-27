# services/hayabusa_wrapper.py
"""
Módulo para automatizar el escaneo de archivos .evtx utilizando Hayabusa.
"""
import subprocess
import json
from pathlib import Path
from utils import messages as msg

# Asegúrate de definir la ruta correcta a tu binario en utils/config.py
# Ejemplo: HAYABUSA_BIN_PATH = Path("./tools/hayabusa/hayabusa-3.8.1-lin-x64-gnu")
from utils.config import HOST_HAYABUSA_BIN_PATH 

def analyze_evtx(evtx_path, output_dir):
    """
    Ejecuta Hayabusa en modo JSON y extrae la inteligencia estructurada.
    """
    evtx_file = Path(evtx_path)
    output_json = Path(output_dir) / f"{evtx_file.stem}_hayabusa.json"

    # Usamos json-timeline para que Python lo procese fácilmente
    comando = [
        str(HOST_HAYABUSA_BIN_PATH), "json-timeline",
        "-f", str(evtx_file),
        "-o", str(output_json),
        "-q" # Modo silencioso para no ensuciar la consola
    ]

    msg.processing(f"Ejecutando motor de reglas Sigma (Hayabusa) sobre {evtx_file.name}...")
    
    try:
        #subprocess.run(comando, check=True, capture_output=True, text=True)
        subprocess.run(comando, check=True)
        msg.info("Análisis de Hayabusa completado")
        
        return _parse_results(output_json)
        
    except subprocess.CalledProcessError as e:
        msg.error(f"Fallo al ejecutar Hayabusa: {e.stderr}")
        return None

import json

def _parse_results(json_path):
    resumen = {
        "alertas_criticas_altas": [],
        "alertas_medias": [],
        "tacticas_mitre": set()
    }

    with open(json_path, 'r', encoding='utf-8') as f:
        contenido = f.read()

    decoder = json.JSONDecoder()
    idx = 0
    length = len(contenido)

    while idx < length:
        # Saltar espacios
        while idx < length and contenido[idx].isspace():
            idx += 1

        if idx >= length:
            break

        try:
            evento, offset = decoder.raw_decode(contenido, idx)
            idx += offset
        except json.JSONDecodeError:
            break

        nivel = evento.get("Level", "").lower()

        for tactica in evento.get("MitreTactics", []):
            resumen["tacticas_mitre"].add(tactica)

        if nivel in ["critical", "high", "medium", "med"]:
            alerta = {
                "timestamp": evento.get("Timestamp"),
                "regla": evento.get("RuleTitle"),
                "detalles": evento.get("Details", "")
            }

            if nivel in ["critical", "high"]:
                resumen["alertas_criticas_altas"].append(alerta)
            else:
                resumen["alertas_medias"].append(alerta)

    resumen["tacticas_mitre"] = list(resumen["tacticas_mitre"])
    return resumen