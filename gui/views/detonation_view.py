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

class CTkConfirmDialog(ctk.CTkToplevel):
    def __init__(self, master, title, message):
        super().__init__(master)
        self.title(title)
        self.geometry("400x200")
        self.attributes("-topmost", True)
        self.grab_set()
        self.focus()
        
        self.result = False
        
        self.label = ctk.CTkLabel(self, text=message, wraplength=350, font=ctk.CTkFont(size=14))
        self.label.pack(pady=(40, 30), padx=20)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        self.btn_yes = ctk.CTkButton(btn_frame, text="Sí, Forzar", fg_color="darkred", hover_color="#8b0000", command=self.on_yes)
        self.btn_yes.pack(side="left", padx=20)
        
        self.btn_no = ctk.CTkButton(btn_frame, text="Cancelar", fg_color="gray", hover_color="darkgray", command=self.on_no)
        self.btn_no.pack(side="right", padx=20)
        
    def on_yes(self):
        self.result = True
        self.destroy()
        
    def on_no(self):
        self.result = False
        self.destroy()

    def get_input(self):
        self.wait_window(self)
        return self.result

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

        # --- Panel de Acciones ---
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=20, pady=(10, 20))
        self.action_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Botón Iniciar
        self.start_btn = ctk.CTkButton(self.action_frame, text="¡INICIAR DETONACIÓN!", fg_color="green", hover_color="darkgreen", font=ctk.CTkFont(weight="bold", size=15), height=40, command=self.start_detonation)
        self.start_btn.grid(row=0, column=0, padx=10, sticky="ew")

        # Botón Continuar (Siempre visible, deshabilitado por defecto)
        self.continue_btn = ctk.CTkButton(self.action_frame, text="▶ CONTINUAR MANUAL", fg_color="#d4af37", hover_color="#b8860b", text_color="black", font=ctk.CTkFont(weight="bold", size=15), height=40, state="disabled", command=self.continue_detonation)
        self.continue_btn.grid(row=0, column=1, padx=10, sticky="ew")

        # Botón Forzar Detención
        self.abort_btn = ctk.CTkButton(self.action_frame, text="FORZAR DETENCIÓN", fg_color="darkred", hover_color="#8b0000", font=ctk.CTkFont(weight="bold", size=15), height=40, state="disabled", command=self.abort_detonation)
        self.abort_btn.grid(row=0, column=2, padx=10, sticky="ew")

        # --- Contenedor para Etiqueta de Consola y Botón Limpiar ---
        self.console_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.console_header_frame.pack(fill="x", padx=20, pady=(0, 0))

        self.console_label = ctk.CTkLabel(self.console_header_frame, text="Logs del Sistema:", font=ctk.CTkFont(weight="bold"))
        self.console_label.pack(side="left")

        self.clear_btn = ctk.CTkButton(self.console_header_frame, text="Limpiar Logs", width=100, fg_color="gray", hover_color="darkgray", font=ctk.CTkFont(size=12), command=self.clear_console)
        self.clear_btn.pack(side="right")

        self.console_text = ctk.CTkTextbox(self, state="disabled", fg_color="black", text_color="green", font=ctk.CTkFont(family="Consolas", size=12))
        self.console_text.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        
        self.manual_event = None
        self.abort_flag = False

    def clear_console(self):
        self.console_text.configure(state="normal")
        self.console_text.delete("1.0", "end")
        self.console_text.configure(state="disabled")

    def refresh_zips(self):
        self.zips = [f for f in os.listdir(config.HOST_MALWARE_DIR) if f.lower().endswith(".zip")] if os.path.exists(config.HOST_MALWARE_DIR) else []
        self.zip_combo.configure(values=self.zips if self.zips else ["No hay muestras"])
        if self.zips and config.ZIP_FILENAME in self.zips:
            self.zip_combo.set(config.ZIP_FILENAME)
        elif self.zips:
            self.zip_combo.set(self.zips[0])
        else:
            self.zip_combo.set("No hay muestras")

    def show_continue_btn(self):
        # Habilitar el botón existente en lugar de empaquetarlo
        self.after(0, lambda: self.continue_btn.configure(state="normal"))

    def continue_detonation(self):
        if self.manual_event:
            self.manual_event.set()
        self.continue_btn.configure(state="disabled")

    def abort_detonation(self):
        dialog = CTkConfirmDialog(self, "Forzar Detención", "¿Estás seguro de que quieres forzar la detención? Esto apagará las máquinas virtuales inmediatamente.")
        confirm = dialog.get_input()
        if not confirm:
            return
            
        self.abort_flag = True
        if hasattr(self, 'abort_event'):
            self.abort_event.set()
            
        self.console_text.configure(state="normal")
        self.console_text.insert("end", "\n[!] FORZANDO DETENCIÓN DE LAS MÁQUINAS VIRTUALES...\n")
        self.console_text.see("end")
        self.console_text.configure(state="disabled")
        
        # Ejecutar apagado forzado en un hilo rápido para no bloquear GUI
        def _force_stop():
            detonation_flow.stop_sandbox()
            # Si el hilo estaba esperando la interacción manual, destrabarlo
            if self.manual_event:
                self.manual_event.set()
        
        threading.Thread(target=_force_stop, daemon=True).start()

    def start_detonation(self):
        # Deshabilitar UI
        self.start_btn.configure(state="disabled", text="DETONANDO...")
        self.abort_btn.configure(state="normal")
        self.zip_combo.configure(state="disabled")
        self.ext_combo.configure(state="disabled")
        self.continue_btn.configure(state="disabled")
        self.abort_flag = False
        self.abort_event = threading.Event()
        
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
        self.manual_event = threading.Event()
        
        t = threading.Thread(target=self.detonation_worker, args=(record, auto_detonation, self.manual_event, self.abort_event))
        t.daemon = True
        t.start()

    def detonation_worker(self, record, auto_detonation, manual_event, abort_event):
        # Redirigir stdout a la consola gráfica
        original_stdout = sys.stdout
        sys.stdout = ThreadSafeConsole(self.console_text)

        try:
            msg.starting("Iniciando proceso de detonación desde Interfaz Gráfica")
            detonation_flow.run_analysis(record=record, auto_detonation=auto_detonation, manual_wait_callback=self.show_continue_btn, manual_event=manual_event, abort_event=abort_event)
            if not self.abort_flag:
                msg.done("Proceso finalizado. Puedes revisar los reportes")
        except detonation_flow.AbortAnalysisError:
            msg.warning("El proceso fue abortado por el usuario. El flujo se ha detenido.")
        except Exception as e:
            if self.abort_flag:
                msg.warning("El proceso fue abortado por el usuario. Las máquinas han sido apagadas.")
            else:
                msg.error(f"Error grave durante la detonación: {e}")
        finally:
            # Restaurar stdout y UI
            sys.stdout = original_stdout
            self.start_btn.after(0, lambda: self.start_btn.configure(state="normal", text="¡INICIAR DETONACIÓN!"))
            self.abort_btn.after(0, lambda: self.abort_btn.configure(state="disabled"))
            self.zip_combo.after(0, lambda: self.zip_combo.configure(state="normal"))
            self.ext_combo.after(0, lambda: self.ext_combo.configure(state="normal"))
