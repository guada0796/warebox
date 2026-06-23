import time

from utils import config, cli_utils, messages as msg
from core import file_handler as file
from services import hayabusa_wrapper as hayabusa
from cli import main_menu
from services import report_generator

def hayabusa_analysis():
    cli_utils.clear_screen()
    msg.title("Análisis Automático con Hayabusa")
    evtx_path = file.get_timestamp_signature_file_name(config.HOST_SYSMON_LOG_DIR)
    # 3. Análisis con Inteligencia de Amenazas (Hayabusa)
    if evtx_path:
        resultados = hayabusa.analyze_evtx(evtx_path, config.HOST_EVIDENCE_DIR)
        
        # 4. Presentación de Resultados
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
            for alerta in resultados['alertas_medias'][:5]: # Mostramos max 5 para no saturar
                msg.pin(f"[{alerta['timestamp']}] {alerta['regla']}")

        msg.line_break(2)
        msg.options("Opciones")
        msg.item("g. Generar Informe")
        msg.item("b. Volver al Menú Principal")
        
        choice = input("\nSeleccione una opción: ").lower()

        if choice == 'b':
            return

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
