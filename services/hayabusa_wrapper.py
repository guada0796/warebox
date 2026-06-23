"""
Módulo para automatizar el escaneo de archivos .evtx utilizando Hayabusa.
"""
import subprocess
import json
import re
from pathlib import Path
from utils import messages as msg

# Asegúrate de definir la ruta correcta a tu binario en utils/config.py
from utils.config import HAYABUSA_BIN_PATH 

# Importamos los diccionarios y el orden de MITRE desde nuestro nuevo archivo de configuración
from utils.mitre_config import MITRE_MAPPING, MITRE_ORDER

def analyze_evtx(evtx_path, output_dir):
    """
    Ejecuta Hayabusa en modo JSON y extrae la inteligencia estructurada.
    """
    evtx_file = Path(evtx_path)
    output_json = Path(output_dir) / f"{evtx_file.stem}_hayabusa.json"

    # Validar si el archivo .json ya existe, preguntar por sobrescribir
    if output_json.exists():
        overwrite = True if input(f"El archivo {output_json} ya existe. ¿Desea sobrescribirlo? (s/N): ").lower() == 's' else False
        if not overwrite:
            msg.line_break(1)
            msg.info("Análisis cancelado por el usuario.")
            return None
        
        # Eliminar el archivo existente antes de ejecutar Hayabusa
        try:
            output_json.unlink()
            msg.info(f"Archivo existente {output_json} eliminado.")
        except Exception as e:
            msg.error(f"No se pudo eliminar el archivo existente: {e}")
            return None

    comando = [
        str(HAYABUSA_BIN_PATH), "json-timeline",
        "-f", str(evtx_file),
        "-o", str(output_json),
        "--profile", "super-verbose"  
    ]

    msg.processing(f"Ejecutando motor de reglas Sigma (Hayabusa) sobre {evtx_file.name}...")
    
    try:
        subprocess.run(comando, check=True)
        msg.info("Análisis de Hayabusa completado")
        
        return _parse_results(output_json)
        
    except subprocess.CalledProcessError as e:
        msg.error(f"Fallo al ejecutar Hayabusa (Código de salida: {e.returncode})")
        return None

def _parse_results(json_path):
    """
    Lee un archivo de objetos JSON concatenados y devuelve un resumen útil.
    """
    resumen = {
        "alertas_criticas_altas": [],
        "alertas_medias": [],
        "tacticas_mitre": set(),
        "tecnicas_mitre": set() # <-- NUEVA LISTA PARA LOS CÓDIGOS Txxxx
    }

    try:
        with open(json_path, 'r', encoding='utf-8', errors='ignore') as f:
            contenido = f.read()

        decoder = json.JSONDecoder()
        posicion = 0
        longitud = len(contenido)

        while posicion < longitud:
            while posicion < longitud and contenido[posicion].isspace():
                posicion += 1
            if posicion >= longitud:
                break
                
            try:
                evento, nueva_posicion = decoder.raw_decode(contenido, posicion)
                posicion = nueva_posicion
            except json.JSONDecodeError:
                posicion += 1
                continue

            if not isinstance(evento, dict):
                continue
            
            nivel = evento.get("Level", "").lower()
            
            # --- TRADUCTOR DE TÁCTICAS MITRE ---
            # 1. Buscamos en el campo explícito 'MitreTactics' y traducimos
            mitre_tactics = evento.get("MitreTactics", [])
            if isinstance(mitre_tactics, list):
                for t in mitre_tactics:
                    t_lower = str(t).lower()
                    tactica_oficial = MITRE_MAPPING.get(t_lower, str(t))
                    resumen["tacticas_mitre"].add(tactica_oficial)
            elif isinstance(mitre_tactics, str):
                t_lower = mitre_tactics.lower()
                tactica_oficial = MITRE_MAPPING.get(t_lower, mitre_tactics)
                resumen["tacticas_mitre"].add(tactica_oficial)

            # 2. Buscamos en 'Tags' o 'MitreTags' por los códigos Txxxx o attack.xxx
            for tag_field in ["Tags", "MitreTags"]:
                tags = evento.get(tag_field, [])
                if isinstance(tags, list):
                    for tag in tags:
                        tag_str = str(tag)
                        tag_lower = tag_str.lower()
                        
                        # A. Capturamos códigos exactos Txxxx o Txxxx.xxx (Ej. T1055, T1053.005)
                        if re.match(r'^T\d{4}(\.\d+)?$', tag_str, re.IGNORECASE):
                            resumen["tecnicas_mitre"].add(tag_str.upper())
                        
                        # B. Capturamos si vienen como attack.t1055
                        elif tag_lower.startswith("attack.t") and re.match(r'^attack\.t\d{4}(\.\d+)?$', tag_lower):
                            t_code = tag_lower.replace("attack.", "").upper()
                            resumen["tecnicas_mitre"].add(t_code)
                            
                        # C. Capturamos nombres completos (ej. attack.defense_evasion)
                        elif tag_lower.startswith("attack."):
                            tactica_limpia = tag_lower.replace("attack.", "").replace("_", " ").title()
                            resumen["tacticas_mitre"].add(tactica_limpia)
            # -----------------------------------

            if nivel in ["critical", "crit", "high", "medium", "med"]:
                alerta = {
                    "timestamp": evento.get("Timestamp"),
                    "regla": evento.get("RuleTitle"),
                    "detalles": evento.get("Details", "")
                }
                if nivel in ["critical", "crit", "high"]:
                    resumen["alertas_criticas_altas"].append(alerta)
                else:
                    resumen["alertas_medias"].append(alerta)

        # Convertimos los sets a listas
        tacticas_lista = list(resumen["tacticas_mitre"])
        tecnicas_lista = list(resumen["tecnicas_mitre"])
        
        # Ordenamos las Tácticas usando el índice de MITRE_ORDER
        resumen["tacticas_mitre"] = sorted(tacticas_lista, key=lambda x: MITRE_ORDER.index(x) if x in MITRE_ORDER else 99)
        
        # Ordenamos los códigos Txxxx alfabéticamente
        resumen["tecnicas_mitre"] = sorted(tecnicas_lista)
        
        return resumen

    except Exception as e:
        msg.error(f"Error parseando resultados de Hayabusa: {e}")
        return None