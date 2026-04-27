import time

from utils import config, cli_utils
from core import file_handler as file
from services import hayabusa_wrapper as hayabusa
from cli import main_menu

def hayabusa_analysis():
    cli_utils.clear_screen()
    evtx_path = file.get_timestamp_signature_file_name(config.HOST_SYSMON_LOG_DIR)
    # 3. Análisis con Inteligencia de Amenazas (Hayabusa)
    if evtx_path:
        resultados = hayabusa.analyze_evtx(evtx_path, config.HOST_EVIDENCE_DIR)
        
        # 4. Presentación de Resultados
        if resultados:
            print("\n" + "="*50)
            print("🛡️ REPORTE DE INTELIGENCIA WAREBOX")
            print("="*50)
            print(f"[*] Tácticas MITRE ATT&CK detectadas:")
            for tactica in resultados['tacticas_mitre']:
                print(f"    - {tactica}")
            
            print(f"\n[!] Alertas Críticas/Altas: {len(resultados['alertas_criticas_altas'])}")
            for alerta in resultados['alertas_criticas_altas']:
                print(f"    [{alerta['timestamp']}] {alerta['regla']}")
                
            print(f"\n[!] Alertas Medias: {len(resultados['alertas_medias'])}")
            for alerta in resultados['alertas_medias'][:5]: # Mostramos max 5 para no saturar
                print(f"    [{alerta['timestamp']}] {alerta['regla']}")

        print("\n\nb. Volver al menú principal")
        choice = input("\nSeleccione una opción: ").lower()

        if choice == 'b':
            main_menu.show_main_menu()
        else:
            print("❌ Opción no válida. Inténtelo de nuevo."); time.sleep(1)
