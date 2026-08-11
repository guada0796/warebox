import customtkinter as ctk
import sys
import threading
import os
from utils import config, messages as msg
from core import file_handler, detonation_flow

class ThreadSafeConsole:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.after(0, self._append, text)

    def _append(self, text):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", text)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def flush(self):
        pass

class DetonationView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.title_label = ctk.CTkLabel(self, text="Panel de Detonación", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(20, 10), padx=20, anchor="w")

        # Configuración de Muestra
        self.setup_frame = ctk.CTkFrame(self)
        self.setup_frame.pack(fill="x", padx=20, pady=10)

        # Selección de archivo ZIP
        self.zip_label = ctk.CTkLabel(self.setup_frame, text="Muestra (.zip):", font=ctk.CTkFont(weight="bold"))
        self.zip_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        self.zips = [f for f in os.listdir(config.HOST_MALWARE_DIR) if f.lower().endswith(".zip")] if os.path.exists(config.HOST_MALWARE_DIR) else []
        self.zip_combo = ctk.CTkComboBox(self.setup_frame, values=self.zips if self.zips else ["No hay muestras"], width=200)
        self.zip_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        if self.zips and config.ZIP_FILENAME in self.zips:
            self.zip_combo.set(config.ZIP_FILENAME)
        elif self.zips:
            self.zip_combo.set(self.zips[0])

        self.refresh_btn = ctk.CTkButton(self.setup_frame, text="↻", width=30, fg_color="gray", hover_color="darkgray", command=self.refresh_zips)
        self.refresh_btn.grid(row=0, column=2, padx=(0, 10), pady=10, sticky="w")

        # Selección de extensión
        self.ext_label = ctk.CTkLabel(self.setup_frame, text="Extensión final:", font=ctk.CTkFont(weight="bold"))
        self.ext_label.grid(row=0, column=3, padx=10, pady=10, sticky="e")
        
        self.ext_combo = ctk.CTkComboBox(self.setup_frame, values=["exe", "dll", "bin", "vbs", "ps1", "bat"], width=100)
        self.ext_combo.grid(row=0, column=4, padx=10, pady=10, sticky="w")
        
        # Opciones booleanas
        self.record_var = ctk.BooleanVar(value=False)
        self.record_switch = ctk.CTkSwitch(self.setup_frame, text="Grabar sesión", variable=self.record_var)
        self.record_switch.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        self.auto_var = ctk.BooleanVar(value=False)
        self.auto_switch = ctk.CTkSwitch(self.setup_frame, text="Detonación automática", variable=self.auto_var)
        self.auto_switch.grid(row=1, column=3, columnspan=2, padx=10, pady=10, sticky="w")

        # Botón Iniciar
        self.start_btn = ctk.CTkButton(self.setup_frame, text="¡INICIAR DETONACIÓN!", fg_color="green", hover_color="darkgreen", font=ctk.CTkFont(weight="bold"), command=self.start_detonation)
        self.start_btn.grid(row=0, column=5, rowspan=2, padx=20, pady=10, sticky="nsew")

        # Consola Virtual
        self.console_label = ctk.CTkLabel(self, text="Logs del Sistema:", font=ctk.CTkFont(weight="bold"))
        self.console_label.pack(anchor="w", padx=20, pady=(10, 0))

        self.console_text = ctk.CTkTextbox(self, state="disabled", fg_color="black", text_color="green", font=ctk.CTkFont(family="Consolas", size=12))
        self.console_text.pack(fill="both", expand=True, padx=20, pady=(5, 20))

    def refresh_zips(self):
        self.zips = [f for f in os.listdir(config.HOST_MALWARE_DIR) if f.lower().endswith(".zip")] if os.path.exists(config.HOST_MALWARE_DIR) else []
        self.zip_combo.configure(values=self.zips if self.zips else ["No hay muestras"])
        if self.zips and config.ZIP_FILENAME in self.zips:
            self.zip_combo.set(config.ZIP_FILENAME)
        elif self.zips:
            self.zip_combo.set(self.zips[0])
        else:
            self.zip_combo.set("No hay muestras")

    def start_detonation(self):
        # Deshabilitar UI
        self.start_btn.configure(state="disabled", text="DETONANDO...")
        self.zip_combo.configure(state="disabled")
        self.ext_combo.configure(state="disabled")
        
        # Limpiar consola
        self.console_text.configure(state="normal")
        self.console_text.delete("1.0", "end")
        self.console_text.configure(state="disabled")

        # Actualizar config con el zip seleccionado
        selected_zip = self.zip_combo.get()
        selected_ext = self.ext_combo.get()
        if selected_zip != "No hay muestras":
            updates = {
                'ZIP_FILENAME': selected_zip,
                'PAYLOAD_NAME': selected_zip.replace(".zip", "." + selected_ext)
            }
            file_handler.update_config_file(updates)

        # Iniciar Hilo
        record = self.record_var.get()
        auto_detonation = self.auto_var.get()
        
        t = threading.Thread(target=self.detonation_worker, args=(record, auto_detonation))
        t.daemon = True
        t.start()

    def detonation_worker(self, record, auto_detonation):
        # Redirigir stdout a la consola gráfica
        original_stdout = sys.stdout
        sys.stdout = ThreadSafeConsole(self.console_text)

        try:
            msg.starting("Iniciando proceso de detonación desde Interfaz Gráfica")
            detonation_flow.run_analysis(record=record, auto_detonation=auto_detonation)
            msg.done("Proceso finalizado. Puedes revisar los reportes")
        except Exception as e:
            msg.error(f"Error grave durante la detonación: {e}")
        finally:
            # Restaurar stdout y UI
            sys.stdout = original_stdout
            self.start_btn.after(0, lambda: self.start_btn.configure(state="normal", text="¡INICIAR DETONACIÓN!"))
            self.zip_combo.after(0, lambda: self.zip_combo.configure(state="normal"))
            self.ext_combo.after(0, lambda: self.ext_combo.configure(state="normal"))
