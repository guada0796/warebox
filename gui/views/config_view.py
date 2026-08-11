import customtkinter as ctk
from utils import config
from core import file_handler

class ConfigView(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Contenedor central para que todo se centre al maximizar
        self.center_container = ctk.CTkFrame(self, fg_color="transparent")
        self.center_container.pack(expand=True, pady=20)

        # Título centrado
        self.title_label = ctk.CTkLabel(self.center_container, text="Configuración del Sandbox", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20))

        # Variables de control (Editables)
        self.vm_name_var = ctk.StringVar(value=config.VM_NAME)
        self.snapshot_name_var = ctk.StringVar(value=config.SNAPSHOT_NAME)
        self.guest_user_var = ctk.StringVar(value=config.GUEST_USER)
        self.guest_pass_var = ctk.StringVar(value=config.GUEST_PASS)
        
        self.compress_key_var = ctk.StringVar(value=config.COMPRESS_KEY)
        self.zip_filename_var = ctk.StringVar(value=config.ZIP_FILENAME)
        self.payload_name_var = ctk.StringVar(value=config.PAYLOAD_NAME)

        self.wait_start_var = ctk.IntVar(value=config.WAIT_START_TIME)
        self.wait_malware_var = ctk.IntVar(value=config.WAIT_MALWARE_TIME)
        self.wait_write_var = ctk.IntVar(value=config.WAIT_WRITE_FILES_TIME)

        # SECCIÓN EDITABLE
        self.editable_title = ctk.CTkLabel(self.center_container, text="--- Parámetros Modificables ---", font=ctk.CTkFont(weight="bold"), text_color="lightgray")
        self.editable_title.grid(row=1, column=0, columnspan=2, pady=(10, 5))

        self.create_entry("Nombre de la VM:", self.vm_name_var, 2)
        self.create_entry("Usuario Guest:", self.guest_user_var, 3)
        self.create_entry("Contraseña Guest:", self.guest_pass_var, 4) 
        
        self.create_entry("Clave ZIP Malware:", self.compress_key_var, 5)
        self.create_entry("Archivo ZIP:", self.zip_filename_var, 6)
        self.create_entry("Payload (Ej: malware.exe):", self.payload_name_var, 7)

        self.create_entry("Espera Arranque VM (s):", self.wait_start_var, 8)
        self.create_entry("Espera Análisis Malware (s):", self.wait_malware_var, 9)
        self.create_entry("Espera Escritura Resultados (s):", self.wait_write_var, 10)

        # SECCIÓN SOLO LECTURA
        self.readonly_title = ctk.CTkLabel(self.center_container, text="--- Valores por defecto (Solo Lectura) ---", font=ctk.CTkFont(weight="bold"), text_color="lightgray")
        self.readonly_title.grid(row=11, column=0, columnspan=2, pady=(20, 5))

        self.create_readonly_entry("Nombre del Snapshot a Detonar:", str(config.SNAPSHOT_NAME), 12)
        self.create_readonly_entry("Directorio de Tools (Guest):", str(config.GUEST_TOOLS_DIR), 13)
        self.create_readonly_entry("Directorio de Logs (Guest):", str(config.GUEST_LOG_DIR), 14)
        self.create_readonly_entry("Directorio Malware (Host):", str(config.HOST_MALWARE_DIR), 15)
        self.create_readonly_entry("Directorio Evidencia (Host):", str(config.HOST_EVIDENCE_DIR), 16)
        self.create_readonly_entry("Firma de Tiempo Actual:", str(config.TIMESTAMP_SIGNATURE), 17)

        # Botón Guardar
        self.save_btn = ctk.CTkButton(self.center_container, text="Guardar Configuración", fg_color="green", hover_color="darkgreen", command=self.save_settings)
        self.save_btn.grid(row=18, column=0, columnspan=2, pady=(30, 10))
        
        self.status_label = ctk.CTkLabel(self.center_container, text="", text_color="green")
        self.status_label.grid(row=19, column=0, columnspan=2)

    def create_entry(self, label_text, variable, row):
        label = ctk.CTkLabel(self.center_container, text=label_text, font=ctk.CTkFont(weight="bold"))
        label.grid(row=row, column=0, pady=5, padx=20, sticky="e")
        
        entry = ctk.CTkEntry(self.center_container, textvariable=variable, width=300)
        entry.grid(row=row, column=1, pady=5, padx=20, sticky="w")

    def create_readonly_entry(self, label_text, value, row):
        label = ctk.CTkLabel(self.center_container, text=label_text, font=ctk.CTkFont(weight="bold"), text_color="gray")
        label.grid(row=row, column=0, pady=5, padx=20, sticky="e")
        
        entry = ctk.CTkEntry(self.center_container, width=300, fg_color="#2b2b2b", text_color="gray")
        entry.insert(0, value)
        entry.configure(state="readonly")
        entry.grid(row=row, column=1, pady=5, padx=20, sticky="w")

    def save_settings(self):
        updates = {
            "VM_NAME": self.vm_name_var.get(),
            "SNAPSHOT_NAME": self.snapshot_name_var.get(),
            "GUEST_USER": self.guest_user_var.get(),
            "GUEST_PASS": self.guest_pass_var.get(),
            "COMPRESS_KEY": self.compress_key_var.get(),
            "ZIP_FILENAME": self.zip_filename_var.get(),
            "PAYLOAD_NAME": self.payload_name_var.get(),
            "WAIT_START_TIME": self.wait_start_var.get(),
            "WAIT_MALWARE_TIME": self.wait_malware_var.get(),
            "WAIT_WRITE_FILES_TIME": self.wait_write_var.get()
        }
        
        try:
            file_handler.update_config_file(updates)
            self.status_label.configure(text="¡Configuración guardada correctamente!", text_color="green")
        except Exception as e:
            self.status_label.configure(text=f"Error al guardar: {e}", text_color="red")
        
        # Limpiar mensaje después de 3 segundos
        self.after(3000, lambda: self.status_label.configure(text=""))
