"""
Módulo para automatizar el escaneo de tráfico de red (.pcap) utilizando Suricata.
"""
import subprocess
import json
from pathlib import Path
from utils import config

def analyze_pcap(pcap_path, output_dir):
    """
    Ejecuta Suricata sobre un archivo PCAP y extrae alertas estructuradas de eve.json.
    """
    pcap_file = Path(pcap_path)
    # Suricata genera el archivo eve.json por defecto en el directorio de salida
    eve_json_path = Path(output_dir) / "eve.json"

    # Limpiamos el eve.json previo para no mezclar eventos de distintas detonaciones
    if eve_json_path.exists():
        try:
            eve_json_path.unlink()
        except Exception as e:
            raise RuntimeError(f"No se pudo eliminar el archivo eve.json anterior: {e}")

    # -k none ignora los errores de checksum (muy común en tráfico capturado en entornos virtuales)
    comando = [
        "suricata",
        "-r", str(pcap_file),
        "-l", str(output_dir),
        "-k", "none" 
    ]

    try:
        # Usamos capture_output para mantener la consola limpia de logs del motor
        subprocess.run(comando, capture_output=True, text=True, check=True)
        
        eve_json = _parse_eve_json(eve_json_path)
        return eve_json

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Fallo al ejecutar Suricata: {e.stderr}")

def _parse_eve_json(eve_path):
    """
    Lee el log estructurado de Suricata y lo formatea para el generador de reportes.
    """
    resumen = {
        "alertas_criticas_altas": [],
        "alertas_medias": []
    }

    if not eve_path.exists():
        return resumen

    try:
        with open(eve_path, 'r', encoding='utf-8') as f:
            for linea in f:
                try:
                    evento = json.loads(linea)
                except json.JSONDecodeError:
                    continue

                if evento.get("event_type") == "alert":
                    # Formateo de timestamp (De "2026-06-29T14:40:59.490-0500" a "2026-06-29 14:40:59")
                    # Esto asegura que encaje perfecto con el formato de Hayabusa en el PDF
                    raw_ts = evento.get("timestamp", "")
                    clean_ts = raw_ts.split('.')[0].replace('T', ' ') if raw_ts else "Desconocido"

                    # Agregamos la etiqueta [RED] para diferenciarlo de Sysmon en el reporte
                    alerta = {
                        "timestamp": clean_ts,
                        "regla": f"[RED] {evento['alert'].get('signature', 'Firma Desconocida')}",
                        "detalles": {
                            "Categoría": evento["alert"].get("category", "N/A"),
                            "IP Origen": evento.get("src_ip", "N/A"),
                            "Puerto Origen": evento.get("src_port", "N/A"),
                            "IP Destino": evento.get("dest_ip", "N/A"),
                            "Puerto Destino": evento.get("dest_port", "N/A"),
                            "Protocolo": evento.get("proto", "N/A")
                        }
                    }

                    # Suricata maneja severidades del 1 (Alto) al 4 (Info)
                    severidad = evento["alert"].get("severity", 3)
                    
                    if severidad == 1:
                        resumen["alertas_criticas_altas"].append(alerta)
                    elif severidad == 2:
                        resumen["alertas_medias"].append(alerta)

        return resumen

    except Exception as e:
        raise RuntimeError(f"Error parseando resultados de Suricata: {e}")