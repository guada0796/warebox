# services/report_generator.py
from fpdf import FPDF
from datetime import datetime
from pathlib import Path
import textwrap
import re
from utils import messages as msg

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
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("helvetica", "B", 12)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(52, 73, 94)
        self.cell(0, 8, f"  {title}", fill=True, ln=True)
        self.ln(4)

def write_safe_lines(pdf, text, max_chars=95):
    """
    El AS en la manga: Reemplazamos la función defectuosa de FPDF2.
    Nosotros calculamos el salto de línea, fpdf2 solo imprime de forma segura.
    """
    if not text: 
        text = "N/A"
        
    # Sanitización estricta
    texto_limpio = str(text).encode('latin-1', 'ignore').decode('latin-1')
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
    
    # Textwrap rompe palabras largas (Base64) sin importar qué contengan
    lineas = textwrap.wrap(texto_limpio, width=max_chars, break_long_words=True)
    
    if not lineas:
        pdf.cell(0, 5, "N/A", ln=True)
    else:
        for linea in lineas:
            # cell() con ln=True es mecánicamente infalible
            pdf.cell(0, 5, linea, ln=True)

def generate_pdf(sample_name, hayabusa_results, output_dir):
    """
    Orquesta la creación del PDF usando exclusivamente funciones seguras.
    """
    pdf = DFIRReport()
    pdf.add_page()
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. RESUMEN EJECUTIVO
    pdf.section_title("1. Resumen Ejecutivo")
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    resumen = (
        f"Fecha de Analisis: {fecha_actual} | "
        f"Muestra: {sample_name} | "
        f"Tacticas MITRE detectadas: {len(hayabusa_results['tacticas_mitre'])} | "
        f"Alertas Altas: {len(hayabusa_results['alertas_criticas_altas'])} | "
        f"Alertas Medias: {len(hayabusa_results['alertas_medias'])}"
    )
    write_safe_lines(pdf, resumen)
    pdf.ln(5)

    # 2. ENTORNO
    pdf.section_title("2. Entorno de Analisis (Sandbox)")
    pdf.set_font("helvetica", "", 10)
    write_safe_lines(pdf, "Plataforma Host: Linux | Hipervisor: VirtualBox | Telemetria: Sysmon | Inteligencia: Hayabusa")
    pdf.ln(5)

    # 3. MITRE
    pdf.section_title("3. Mapeo de Amenazas (MITRE ATT&CK)")
    pdf.set_font("helvetica", "", 10)
    if hayabusa_results['tacticas_mitre']:
        for t in hayabusa_results['tacticas_mitre']:
            write_safe_lines(pdf, f"* {t}")
    else:
        write_safe_lines(pdf, "No se detectaron tacticas catalogadas.")
    pdf.ln(5)

    # 4. CRÍTICAS
    pdf.section_title("4. Linea de Tiempo - Eventos Criticos y Altos")
    if hayabusa_results['alertas_criticas_altas']:
        for alerta in hayabusa_results['alertas_criticas_altas']:
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(192, 57, 43)
            write_safe_lines(pdf, f"[{alerta.get('timestamp')}] REGLA: {alerta.get('regla')}")
            
            pdf.set_font("helvetica", "", 9)
            pdf.set_text_color(50, 50, 50)
            write_safe_lines(pdf, f"Detalle: {alerta.get('detalles')}")
            pdf.ln(3)
    else:
        pdf.set_font("helvetica", "", 10)
        write_safe_lines(pdf, "No se registraron eventos criticos o altos.")
        pdf.ln(3)

    # 5. MEDIAS
    pdf.section_title("5. Eventos de Severidad Media")
    if hayabusa_results['alertas_medias']:
        for alerta in hayabusa_results['alertas_medias']:
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(211, 84, 0)
            write_safe_lines(pdf, f"[{alerta.get('timestamp')}] REGLA: {alerta.get('regla')}")
            
            pdf.set_font("helvetica", "", 9)
            pdf.set_text_color(50, 50, 50)
            write_safe_lines(pdf, f"Detalle: {alerta.get('detalles')}")
            pdf.ln(3)
    else:
        pdf.set_font("helvetica", "", 10)
        write_safe_lines(pdf, "No se registraron eventos de severidad media.")

    # Guardar archivo
    output_path = Path(output_dir) / f"Reporte_Tecnico_{sample_name}.pdf"
    pdf.output(str(output_path))
    msg.info(f"Reporte DFIR generado exitosamente en: {output_path}")
    
    return output_path