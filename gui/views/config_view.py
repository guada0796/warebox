import customtkinter as ctk
from utils import config
from core import file_handler

class ConfigView(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Título ajustado a la izquierda
        self.title_label = ctk.CTkLabel(self, text="Configuración del Sandbox", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(anchor="w", padx=20, pady=(20, 30))

        # Contenedor principal para las dos columnas
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)

        # Columna Izquierda (Editables)
        self.left_col = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        # Columna Derecha (Solo lectura)
        self.right_col = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.right_col.grid(row=0, column=1, sticky="nsew", padx=(20, 0))

        # Variables de control
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

        # --- SECCIÓN EDITABLE (Izquierda) ---
        self.editable_title = ctk.CTkLabel(self.left_col, text="PARÁMETROS MODIFICABLES", font=ctk.CTkFont(size=14, weight="bold"), text_color="#3B8ED0")
        self.editable_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        self.create_entry(self.left_col, "Nombre de la VM:", self.vm_name_var, 1)
        self.create_entry(self.left_col, "Usuario Guest:", self.guest_user_var, 2)
        self.create_entry(self.left_col, "Contraseña Guest:", self.guest_pass_var, 3) 
        
        self.create_entry(self.left_col, "Clave ZIP Malware:", self.compress_key_var, 4)
        self.create_entry(self.left_col, "Archivo ZIP:", self.zip_filename_var, 5)
        self.create_entry(self.left_col, "Payload (Ej: malware.exe):", self.payload_name_var, 6)

        self.create_entry(self.left_col, "Espera Arranque VM (s):", self.wait_start_var, 7)
        self.create_entry(self.left_col, "Espera Análisis Malware (s):", self.wait_malware_var, 8)
        self.create_entry(self.left_col, "Espera Escritura Resultados (s):", self.wait_write_var, 9)

        # --- SECCIÓN SOLO LECTURA (Derecha) ---
        self.readonly_title = ctk.CTkLabel(self.right_col, text="VALORES DEL SISTEMA (Solo Lectura)", font=ctk.CTkFont(size=14, weight="bold"), text_color="gray60")
        self.readonly_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        self.create_readonly_entry(self.right_col, "Snapshot a Detonar:", str(config.SNAPSHOT_NAME), 1)
        self.create_readonly_entry(self.right_col, "Dir. Tools (Guest):", str(config.GUEST_TOOLS_DIR), 2)
        self.create_readonly_entry(self.right_col, "Dir. Logs (Guest):", str(config.GUEST_LOG_DIR), 3)
        self.create_readonly_entry(self.right_col, "Dir. Malware (Host):", str(config.HOST_MALWARE_DIR), 4)
        self.create_readonly_entry(self.right_col, "Dir. Evidencia (Host):", str(config.HOST_EVIDENCE_DIR), 5)
        self.create_readonly_entry(self.right_col, "Firma de Tiempo Actual:", str(config.TIMESTAMP_SIGNATURE), 6)

        # Contenedor para botones y estado (Parte inferior)
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=20, pady=30)

        # Botón Guardar ajustado a la izquierda para seguir la línea visual
        self.save_btn = ctk.CTkButton(self.bottom_frame, text="Guardar Configuración", font=ctk.CTkFont(weight="bold", size=14), height=40, fg_color="green", hover_color="darkgreen", command=self.save_settings)
        self.save_btn.pack(side="left", pady=(10, 10))
        
        self.status_label = ctk.CTkLabel(self.bottom_frame, text="", text_color="green", font=ctk.CTkFont(weight="bold"))
        self.status_label.pack(side="left", padx=20, pady=(10, 10))

    def create_entry(self, parent, label_text, variable, row):
        label = ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(weight="bold"))
        label.grid(row=row, column=0, pady=10, padx=(0, 15), sticky="w")
        
        entry = ctk.CTkEntry(parent, textvariable=variable, width=250)
        entry.grid(row=row, column=1, pady=10, sticky="w")

    def create_readonly_entry(self, parent, label_text, value, row):
        label = ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(weight="bold"), text_color="gray70")
        label.grid(row=row, column=0, pady=10, padx=(0, 15), sticky="w")
        
        entry = ctk.CTkEntry(parent, width=250, fg_color="#2b2b2b", text_color="gray60")
        entry.insert(0, value)
        entry.configure(state="readonly")
        entry.grid(row=row, column=1, pady=10, sticky="w")

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
