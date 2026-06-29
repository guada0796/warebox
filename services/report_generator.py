"""
Módulo para la generación de reportes técnicos DFIR en formato PDF.
"""
from fpdf import FPDF
from datetime import datetime
from pathlib import Path
import textwrap
import re
from utils import messages as msg, config

class DFIRReport(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 16)
        self.set_text_color(41, 128, 185)
        self.cell(0, 10, "WAREBOX - INFORME TECNICO DE ANALISIS DFIR", align="C", ln=True)
        
        self.set_font("helvetica", "I", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Universidad Camilo Jose Cela - Master en Ciberseguridad", align="C", ln=True)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("helvetica", "B", 12)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(52, 73, 94)
        self.cell(0, 8, f"  {title}", fill=True, ln=True)
        self.ln(4)

def write_safe_lines(pdf, text, max_chars=95):
    """
    Imprime líneas de texto de forma segura calculando los saltos de línea.
    """
    if not text: 
        text = "N/A"
        
    texto_limpio = str(text).encode('latin-1', 'ignore').decode('latin-1')
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
    
    lineas = textwrap.wrap(texto_limpio, width=max_chars, break_long_words=True)
    
    if not lineas:
        pdf.cell(0, 5, "N/A", ln=True)
    else:
        for linea in lineas:
            pdf.cell(0, 5, linea, ln=True)

def print_formatted_details(pdf, detalles):
    """
    Toma el diccionario crudo de detalles y lo formatea como una lista
    elegante de viñetas para el reporte.
    """
    pdf.set_font("helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    
    if isinstance(detalles, dict):
        for key, value in detalles.items():
            # Ignoramos valores vacíos para ahorrar espacio
            if value and str(value).strip():
                # Acortamos valores inmensos (como base64 o rutas larguísimas)
                val_str = str(value)
                if len(val_str) > 250:
                    val_str = val_str[:247] + "..."
                write_safe_lines(pdf, f"    • {key}: {val_str}", max_chars=90)
    else:
        # Si por alguna razón es un string puro
        write_safe_lines(pdf, f"    • Detalles: {detalles}")

def generate_pdf(sample_name, hayabusa_results, output_dir):
    """
    Orquesta la creación del PDF formateado.
    """
    pdf = DFIRReport()
    pdf.add_page()
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Asumimos que el nombre de la muestra suele ser el SHA256
    hash_sha256 = config.ZIP_FILENAME.replace(".zip", "").replace(".ZIP", "") if len(config.ZIP_FILENAME) >= 64 else "Desconocido"

    # ==========================================
    # 1. RESUMEN EJECUTIVO (Refinado)
    # ==========================================
    pdf.section_title("1. Resumen Ejecutivo")
    
    # Datos de la Muestra
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(50, 50, 50)
    write_safe_lines(pdf, "[ Información de la Muestra ]")
    pdf.set_font("helvetica", "", 10)
    write_safe_lines(pdf, f"  • Archivo Analizado : {config.ZIP_FILENAME}")
    write_safe_lines(pdf, f"  • Hash SHA256     : {config.PAYLOAD_SHA256}")
    write_safe_lines(pdf, f"  • Fecha Análisis    : {fecha_actual}")
    pdf.ln(3)
    
    # Resultados Globales
    pdf.set_font("helvetica", "B", 10)
    write_safe_lines(pdf, "[ Resultados del Análisis Automático ]")
    pdf.set_font("helvetica", "", 10)
    write_safe_lines(pdf, f"  • Tácticas MITRE Detectadas : {len(hayabusa_results.get('tacticas_mitre', []))}")
    write_safe_lines(pdf, f"  • Alertas Críticas / Altas     : {len(hayabusa_results.get('alertas_criticas_altas', []))}")
    write_safe_lines(pdf, f"  • Alertas de Severidad Media : {len(hayabusa_results.get('alertas_medias', []))}")
    pdf.ln(5)

    # ==========================================
    # 2. ENTORNO (Refinado)
    # ==========================================
    pdf.section_title("2. Entorno de Análisis (Sandbox)")
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    write_safe_lines(pdf, "  • Plataforma Host   : Linux Mint (Ubuntu base)")
    write_safe_lines(pdf, "  • Plataforma Guest  : Windows 10 (VirtualBox)")
    write_safe_lines(pdf, "  • Motor Telemetría  : Sysmon (Configuración Sandbox Permisiva)")
    write_safe_lines(pdf, "  • Motor Inteligencia: Hayabusa (Reglas Sigma)")
    write_safe_lines(pdf, "  • Capa de Red       : INetSim + TCPDump")
    pdf.ln(5)

    # ==========================================
    # 3. MITRE ATT&CK
    # ==========================================
    pdf.section_title("3. Mapeo de Amenazas (MITRE ATT&CK)")
    tactics_count = 0
    if hayabusa_results.get('tacticas_mitre'):
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(50, 50, 50)
        write_safe_lines(pdf, "[ Tácticas Identificadas - Ciclo de Ataque ]")
        pdf.set_font("helvetica", "", 10)
        for t in hayabusa_results['tacticas_mitre']:
            tactics_count += 1
            write_safe_lines(pdf, f"  * {t}")
    else:
        write_safe_lines(pdf, "No se detectaron tácticas catalogadas.")
    pdf.ln(3)
    
    if hayabusa_results.get('tecnicas_mitre') and tactics_count > 0:
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(50, 50, 50)
        write_safe_lines(pdf, "[ Técnicas Específicas (IDs) ]")
        pdf.set_font("helvetica", "", 10)
        tecnicas_str = ", ".join(hayabusa_results['tecnicas_mitre'])
        write_safe_lines(pdf, f"  {tecnicas_str}")
    pdf.ln(5)

    # ==========================================
    # 4. ALERTAS CRÍTICAS Y ALTAS
    # ==========================================
    pdf.section_title("4. Línea de Tiempo - Eventos Críticos y Altos")
    if hayabusa_results.get('alertas_criticas_altas'):
        for alerta in hayabusa_results['alertas_criticas_altas']:
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(192, 57, 43)
            write_safe_lines(pdf, f"[{alerta.get('timestamp')}] REGLA: {alerta.get('regla')}")
            
            # Usamos la nueva función para imprimir los detalles limpios
            print_formatted_details(pdf, alerta.get('detalles'))
            pdf.ln(3)
    else:
        pdf.set_font("helvetica", "", 10)
        write_safe_lines(pdf, "No se registraron eventos críticos o altos.")
        pdf.ln(3)

    # ==========================================
    # 5. ALERTAS MEDIAS
    # ==========================================
    pdf.section_title("5. Eventos de Severidad Media")
    if hayabusa_results.get('alertas_medias'):
        for alerta in hayabusa_results['alertas_medias']:
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(211, 84, 0)
            write_safe_lines(pdf, f"[{alerta.get('timestamp')}] REGLA: {alerta.get('regla')}")
            
            # Usamos la nueva función para imprimir los detalles limpios
            print_formatted_details(pdf, alerta.get('detalles'))
            pdf.ln(3)
    else:
        pdf.set_font("helvetica", "", 10)
        write_safe_lines(pdf, "No se registraron eventos de severidad media.")

    # Guardar archivo
    output_path = Path(output_dir) / f"Reporte_Tecnico_{sample_name}.pdf"
    pdf.output(str(output_path))
    msg.info(f"Reporte DFIR generado exitosamente en: {output_path}")
    
    return output_path