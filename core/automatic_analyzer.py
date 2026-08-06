import time

from utils import config, cli_utils, messages as msg
from core import file_handler as file
from services import hayabusa_wrapper as hayabusa
from services import suricata_wrapper as suricata  # <-- NUEVO IMPORT
from cli import main_menu
from services import report_generator

def hayabusa_analysis():
    repeat = True
    while repeat:
        repeat = False
        cli_utils.clear_screen()
        msg.title("Análisis Automático Multi-Capa (Endpoint + Red)")
        
        # 1. Obtenemos las rutas de las evidencias (Endpoint y Red)
        evtx_path = file.get_timestamp_signature_file_name(config.HOST_SYSMON_LOG_DIR)
        pcap_path = file.get_timestamp_signature_file_name(config.HOST_TCPDUMP_LOG_DIR)
        
        # 2. Análisis con Inteligencia de Amenazas
        if evtx_path:
            resultados = hayabusa.analyze_evtx(evtx_path, config.HOST_EVIDENCE_DIR)
            
            # --- NUEVA LÓGICA DE SURICATA ---
            if config.ENABLE_SURICATA and pcap_path:
                msg.line_break(1)
                resultados_red = suricata.analyze_pcap(pcap_path, config.HOST_EVIDENCE_DIR)
                
                if resultados_red:
                    # Fusionamos las listas de alertas de red con las del endpoint
                    resultados['alertas_criticas_altas'].extend(resultados_red['alertas_criticas_altas'])
                    resultados['alertas_medias'].extend(resultados_red['alertas_medias'])
                    
                    # ORDEN CRONOLÓGICO: Magia pura para la línea de tiempo del PDF
                    resultados['alertas_criticas_altas'] = sorted(
                        resultados['alertas_criticas_altas'], 
                        key=lambda x: x.get('timestamp', '')
                    )
                    resultados['alertas_medias'] = sorted(
                        resultados['alertas_medias'], 
                        key=lambda x: x.get('timestamp', '')
                    )
            elif config.ENABLE_SURICATA:
                msg.warning("No se encontró archivo .pcap para análisis de red.")
            # --------------------------------
            
            # 3. Presentación de Resultados
            if resultados:
                msg.line_break(2)
                msg.separation_specific_line("radioactive")
                msg.info("Reporte de Inteligencia WAREBOX")
                msg.separation_specific_line("radioactive")
                msg.line_break(1)
                
                msg.warning("Tácticas MITRE ATT&CK detectadas")
                for tactica in resultados['tacticas_mitre']:
                    msg.pin(f"{tactica}")
                
                msg.line_break(1)
                msg.alarm(f"Alertas Críticas/Altas: {len(resultados['alertas_criticas_altas'])}")
                for alerta in resultados['alertas_criticas_altas']:
                    msg.pin(f"[{alerta['timestamp']}] {alerta['regla']}")
                    
                msg.line_break(1)
                msg.alarm(f"Alertas Medias: {len(resultados['alertas_medias'])}")
                for alerta in resultados['alertas_medias'][:5]: 
                    msg.pin(f"[{alerta['timestamp']}] {alerta['regla']}")

                msg.line_break(2)
                msg.options("Opciones")
                msg.item("g. Generar Informe")
                msg.item("h. Volver a Analizar")
                msg.item("b. Volver al Menú Principal")
                
                while True:
                    choice = input("\nSeleccione una opción: ").lower()

                    if choice == 'b':
                        return
                    
                    if choice == 'h':
                        repeat = True
                        break

                    if choice == 'g':
                        if resultados:                
                            payload = config.ZIP_FILENAME.replace(".zip", "_")
                            report_name = f"{payload}{config.TIMESTAMP_SIGNATURE}"
                            pdf_path = report_generator.generate_pdf(
                                sample_name=report_name, 
                                hayabusa_results=resultados, 
                                output_dir=config.HOST_EVIDENCE_DIR
                            )
                            msg.line_break(1)
                            msg.done(f"Análisis finalizado. Revisa el documento en {pdf_path}")
                            msg.wait_key()
                            return
                    else:
                        msg.error("Opción no válida. Inténtelo de nuevo"); time.sleep(1)
            
            if repeat:
                continue
            msg.wait_key()