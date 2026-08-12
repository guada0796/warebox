import customtkinter as ctk
import threading
import time
import subprocess
import os
from pathlib import Path

from utils import config
from core import file_handler as file
from services import report_generator
from gui import custom_messagebox as messagebox
from services import hayabusa_wrapper as hayabusa
from services import suricata_wrapper as suricata

class AnalysisView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.resultados_actuales = None
        self.pdf_generado_path = None

        self.title_label = ctk.CTkLabel(self, text="Análisis de Resultados", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(20, 10), padx=20, anchor="w")

        # --- Controles Superiores ---
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(fill="x", padx=20, pady=10)

        self.btn_auto = ctk.CTkButton(self.controls_frame, text="⚡ Análisis Automático (Endpoint + Red)", font=ctk.CTkFont(weight="bold", size=14),
                                      fg_color="#006400", hover_color="#004d00", height=40, command=self.start_auto_analysis)
        self.btn_auto.pack(side="left", padx=(0, 10))

        self.btn_manual = ctk.CTkButton(self.controls_frame, text="🛠 Análisis Manual", font=ctk.CTkFont(weight="bold", size=14),
                                        fg_color="#8b8000", hover_color="#665c00", height=40, command=self.start_manual_analysis)
        self.btn_manual.pack(side="left", padx=10)

        self.btn_clear = ctk.CTkButton(self.controls_frame, text="🗑 Limpiar", font=ctk.CTkFont(weight="bold", size=14),
                                        fg_color="#8b0000", hover_color="#5c0000", height=40, width=100, command=self.clear_all_results)
        self.btn_clear.pack(side="left", padx=(10, 0))

        self.btn_open_folder = ctk.CTkButton(self.controls_frame, text="📁 Abrir Evidencias", font=ctk.CTkFont(weight="bold", size=14),
                                             fg_color="#333333", hover_color="#555555", height=40, width=130, command=self.open_evidence_folder)
        self.btn_open_folder.pack(side="right", padx=0)

        self.btn_open_pdf = ctk.CTkButton(self.controls_frame, text="👁 Abrir Reporte", font=ctk.CTkFont(weight="bold", size=14),
                                     fg_color="#800080", hover_color="#4d004d", height=40, width=130, state="disabled", command=self.open_pdf_report)
        self.btn_open_pdf.pack(side="right", padx=(0, 10))

        self.btn_pdf = ctk.CTkButton(self.controls_frame, text="📄 Generar Reporte", font=ctk.CTkFont(weight="bold", size=14),
                                     fg_color="#1f538d", hover_color="#14375d", height=40, width=130, state="disabled", command=self.generate_pdf)
        self.btn_pdf.pack(side="right", padx=(0, 10))

        # --- Panel de Información (Nuevo) ---
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(fill="x", padx=20, pady=(0, 5))
        
        self.lbl_info_file = ctk.CTkLabel(self.info_frame, text="Archivo en análisis: Ninguno", text_color="gray", font=ctk.CTkFont(size=12))
        self.lbl_info_file.pack(side="left", padx=10)

        self.lbl_info_timestamp = ctk.CTkLabel(self.info_frame, text="Firma de Tiempo: N/A", text_color="gray", font=ctk.CTkFont(size=12))
        self.lbl_info_timestamp.pack(side="left", padx=10)

        self.lbl_info_path = ctk.CTkLabel(self.info_frame, text=f"Directorio de Evidencias: {config.HOST_EVIDENCE_DIR}", text_color="gray", font=ctk.CTkFont(size=12))
        self.lbl_info_path.pack(side="left", padx=10)

        # --- Configuración de Reglas (Hayabusa) ---
        self.rules_frame = ctk.CTkFrame(self)
        self.rules_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(self.rules_frame, text="Configuración de Reglas Hayabusa:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10)
        
        self.profile_combo = ctk.CTkComboBox(self.rules_frame, values=["standard", "verbose", "super-verbose"], width=150)
        self.profile_combo.set("super-verbose")
        self.profile_combo.grid(row=0, column=1, padx=10, pady=10)

        self.var_deprecated = ctk.BooleanVar(value=False)
        self.chk_deprecated = ctk.CTkCheckBox(self.rules_frame, text="Incluir obsoletas", variable=self.var_deprecated)
        self.chk_deprecated.grid(row=0, column=2, padx=10, pady=10)

        self.var_unsupported = ctk.BooleanVar(value=False)
        self.chk_unsupported = ctk.CTkCheckBox(self.rules_frame, text="Incluir no soportadas", variable=self.var_unsupported)
        self.chk_unsupported.grid(row=0, column=3, padx=10, pady=10)

        self.var_noisy = ctk.BooleanVar(value=False)
        self.chk_noisy = ctk.CTkCheckBox(self.rules_frame, text="Incluir ruidosas", variable=self.var_noisy)
        self.chk_noisy.grid(row=0, column=4, padx=10, pady=10)

        self.var_sysmon = ctk.BooleanVar(value=True)
        self.chk_sysmon = ctk.CTkCheckBox(self.rules_frame, text="Incluir Sysmon", variable=self.var_sysmon)
        self.chk_sysmon.grid(row=0, column=5, padx=10, pady=10)

        # --- Área de Progreso y Mensajes ---
        self.status_label = ctk.CTkLabel(self, text="Preparado para iniciar análisis.", text_color="gray", font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", mode="indeterminate")
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.set(0)
        self.progress_bar.pack_forget() # Ocultar inicialmente

        # --- Área de Resultados ---
        self.results_frame = ctk.CTkScrollableFrame(self)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def set_ui_state(self, state):
        btn_state = "normal" if state == "normal" else "disabled"
        self.btn_auto.configure(state=btn_state)
        self.btn_manual.configure(state=btn_state)
        self.btn_clear.configure(state=btn_state)
        self.btn_open_folder.configure(state=btn_state)
        self.profile_combo.configure(state=btn_state)
        self.chk_deprecated.configure(state=btn_state)
        self.chk_unsupported.configure(state=btn_state)
        self.chk_noisy.configure(state=btn_state)
        self.chk_sysmon.configure(state=btn_state)

    def clear_all_results(self):
        self.clear_results()
        self.status_label.configure(text="Resultados limpiados. Preparado para iniciar análisis.", text_color="gray")
        self.lbl_info_file.configure(text="Archivo en análisis: Ninguno")
        self.lbl_info_timestamp.configure(text="Firma de Tiempo: N/A")
        self.btn_pdf.configure(state="disabled")
        self.btn_open_pdf.configure(state="disabled")
        self.pdf_generado_path = None
        self.resultados_actuales = None

    def open_evidence_folder(self):
        folder = config.HOST_EVIDENCE_DIR
        if os.path.exists(folder):
            try:
                subprocess.Popen(["xdg-open", folder])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{e}", master=self)
        else:
            messagebox.showwarning("No Encontrada", "La carpeta de evidencias no existe aún.", master=self)

    def open_pdf_report(self):
        if self.pdf_generado_path and os.path.exists(self.pdf_generado_path):
            try:
                subprocess.Popen(["xdg-open", self.pdf_generado_path])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el reporte:\n{e}", master=self)
        else:
            messagebox.showwarning("No Encontrado", "El archivo PDF ya no se encuentra en el disco.", master=self)

    def start_manual_analysis(self):
        messagebox.showinfo("Próximamente", "La interfaz de análisis manual está en desarrollo. ¡Pronto estará disponible!", master=self)

    def start_auto_analysis(self):
        evtx_path = file.get_timestamp_signature_file_name(config.HOST_SYSMON_LOG_DIR)
        if evtx_path:
            evtx_file = Path(evtx_path)
            output_json = Path(config.HOST_EVIDENCE_DIR) / f"{evtx_file.stem}_hayabusa.json"
            if output_json.exists():
                overwrite = messagebox.askyesno("Archivo Existente", f"El archivo {output_json.name} ya existe.\n¿Deseas sobrescribirlo?", master=self)
                if not overwrite:
                    return

        self.set_ui_state("disabled")
        self.btn_pdf.configure(state="disabled")
        self.btn_open_pdf.configure(state="disabled")
        self.pdf_generado_path = None
        self.clear_results()
        
        if evtx_path:
            self.lbl_info_file.configure(text=f"Archivo en análisis: {Path(evtx_path).name}")
            
        if config.TIMESTAMP_SIGNATURE:
            self.lbl_info_timestamp.configure(text=f"Firma de Tiempo: {config.TIMESTAMP_SIGNATURE}")
        
        options = {
            "profile": self.profile_combo.get(),
            "deprecated": self.var_deprecated.get(),
            "unsupported": self.var_unsupported.get(),
            "noisy": self.var_noisy.get(),
            "sysmon": self.var_sysmon.get()
        }
        
        self.status_label.configure(text="Buscando evidencias generadas...", text_color="yellow")
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.start()

        threading.Thread(target=self._auto_analysis_worker, args=(options,), daemon=True).start()

    def _auto_analysis_worker(self, options):
        evtx_path = file.get_timestamp_signature_file_name(config.HOST_SYSMON_LOG_DIR)
        pcap_path = file.get_timestamp_signature_file_name(config.HOST_TCPDUMP_LOG_DIR)

        if not evtx_path:
            self._update_status("No se encontró archivo de eventos (.evtx) para análisis (endpoint).", "red")
            self._finish_analysis()
            return

        self._update_status("Analizando eventos del Endpoint con Inteligencia de Amenazas...", "yellow")
        try:
            resultados = hayabusa.analyze_evtx(
                evtx_path, 
                config.HOST_EVIDENCE_DIR, 
                profile=options["profile"],
                include_deprecated=options["deprecated"],
                include_unsupported=options["unsupported"],
                include_noisy=options["noisy"],
                include_sysmon=options["sysmon"]
            )
        except Exception as e:
            self._update_status(f"Error en Hayabusa: {e}", "red")
            self._finish_analysis()
            return

        if config.ENABLE_SURICATA:
            if pcap_path:
                self._update_status("Analizando tráfico de Red con Suricata...", "yellow")
                try:
                    resultados_red = suricata.analyze_pcap(pcap_path, config.HOST_EVIDENCE_DIR)
                    if resultados_red:
                        resultados['alertas_criticas_altas'].extend(resultados_red['alertas_criticas_altas'])
                        resultados['alertas_medias'].extend(resultados_red['alertas_medias'])
                        
                        resultados['alertas_criticas_altas'] = sorted(
                            resultados['alertas_criticas_altas'], 
                            key=lambda x: x.get('timestamp', '')
                        )
                        resultados['alertas_medias'] = sorted(
                            resultados['alertas_medias'], 
                            key=lambda x: x.get('timestamp', '')
                        )
                except Exception as e:
                    self._update_status(f"Error en Suricata: {e}", "red")
            else:
                self.after(0, lambda: messagebox.showwarning("Advertencia de Red", "No se encontró archivo .pcap para análisis de red. Solo se analizó el endpoint.", master=self))

        self.resultados_actuales = resultados
        self._display_results(resultados)
        self._update_status("Análisis Automático completado exitosamente.", "green")
        
        self.after(0, lambda: self.btn_pdf.configure(state="normal"))
        self._finish_analysis()

    def _update_status(self, message, color):
        self.after(0, lambda m=message, c=color: self.status_label.configure(text=m, text_color=c))

    def _finish_analysis(self):
        self.after(0, self.progress_bar.stop)
        self.after(0, self.progress_bar.pack_forget)
        self.after(0, lambda: self.set_ui_state("normal"))

    def _display_results(self, resultados):
        if not resultados:
            self._update_status("No se generaron resultados validos del análisis.", "red")
            return
            
        def _render():
            tacticas_frame = ctk.CTkFrame(self.results_frame, fg_color="#1a1a1a")
            tacticas_frame.pack(fill="x", pady=(0, 10))
            
            tacticas_title = ctk.CTkLabel(tacticas_frame, text="Tácticas MITRE ATT&CK Detectadas:", font=ctk.CTkFont(weight="bold", size=16), text_color="#d4af37")
            tacticas_title.pack(anchor="w", padx=10, pady=(10, 5))
            
            for t in resultados.get('tacticas_mitre', []):
                ctk.CTkLabel(tacticas_frame, text=f"• {t}", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=2)

            criticas = resultados.get('alertas_criticas_altas', [])
            criticas_frame = ctk.CTkFrame(self.results_frame, fg_color="#2b0000")
            criticas_frame.pack(fill="x", pady=(10, 10))
            
            criticas_title = ctk.CTkLabel(criticas_frame, text=f"Alertas Críticas/Altas ({len(criticas)}):", font=ctk.CTkFont(weight="bold", size=16), text_color="#ff4c4c")
            criticas_title.pack(anchor="w", padx=10, pady=(10, 5))
            
            for a in criticas:
                text = f"[{a.get('timestamp', 'N/A')}] {a.get('regla', 'Desconocida')}"
                ctk.CTkLabel(criticas_frame, text=text, font=ctk.CTkFont(size=13), justify="left", wraplength=800).pack(anchor="w", padx=20, pady=2)

            medias = resultados.get('alertas_medias', [])
            medias_frame = ctk.CTkFrame(self.results_frame, fg_color="#2b2b00")
            medias_frame.pack(fill="x", pady=(10, 10))
            
            medias_title = ctk.CTkLabel(medias_frame, text=f"Alertas Medias (Mostrando primeras 5 de {len(medias)}):", font=ctk.CTkFont(weight="bold", size=16), text_color="#ffcc00")
            medias_title.pack(anchor="w", padx=10, pady=(10, 5))
            
            for a in medias[:5]:
                text = f"[{a.get('timestamp', 'N/A')}] {a.get('regla', 'Desconocida')}"
                ctk.CTkLabel(medias_frame, text=text, font=ctk.CTkFont(size=13), justify="left", wraplength=800).pack(anchor="w", padx=20, pady=2)

        self.after(0, _render)

    def generate_pdf(self):
        if not self.resultados_actuales:
            messagebox.showerror("Error", "No hay resultados para generar el PDF.", master=self)
            return
            
        self.status_label.configure(text="Generando reporte PDF...", text_color="yellow")
        self.btn_pdf.configure(state="disabled")
        self.btn_open_pdf.configure(state="disabled")
        
        threading.Thread(target=self._generate_pdf_worker, daemon=True).start()

    def _generate_pdf_worker(self):
        try:
            payload = config.ZIP_FILENAME.replace(".zip", "_")
            report_name = f"{payload}{config.TIMESTAMP_SIGNATURE}"
            pdf_path = report_generator.generate_pdf(
                sample_name=report_name, 
                hayabusa_results=self.resultados_actuales, 
                output_dir=config.HOST_EVIDENCE_DIR
            )
            if pdf_path:
                self.pdf_generado_path = pdf_path
                self.after(0, lambda: self._pdf_generation_success(pdf_path))
            else:
                self.after(0, lambda: self._pdf_generation_error("El generador no devolvió una ruta válida."))
        except Exception as e:
            self.after(0, lambda: self._pdf_generation_error(str(e)))

    def _pdf_generation_success(self, pdf_path):
        self.status_label.configure(text=f"Reporte generado exitosamente: {Path(pdf_path).name}", text_color="#00ff00")
        self.btn_pdf.configure(state="normal")
        self.btn_open_pdf.configure(state="normal")
        messagebox.showinfo("Reporte Generado", f"El reporte ha sido generado y guardado en:\n{pdf_path}", master=self)

    def _pdf_generation_error(self, error_msg):
        self.status_label.configure(text=f"Error al generar reporte PDF: {error_msg}", text_color="red")
        self.btn_pdf.configure(state="normal")
        messagebox.showerror("Error PDF", f"Error al generar reporte PDF:\n{error_msg}", master=self)
