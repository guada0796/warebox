import customtkinter as ctk
from utils import config
from core import file_handler

class ConfigView(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.title_label = ctk.CTkLabel(self, text="Configuración del Sandbox", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="w")

        # Variables de control
        self.vm_name_var = ctk.StringVar(value=config.VM_NAME)
        self.snapshot_name_var = ctk.StringVar(value=config.SNAPSHOT_NAME)
        self.guest_user_var = ctk.StringVar(value=config.GUEST_USER)
        self.guest_pass_var = ctk.StringVar(value=config.GUEST_PASS)
        
        self.compress_key_var = ctk.StringVar(value=config.COMPRESS_KEY)
        self.wait_start_var = ctk.IntVar(value=config.WAIT_START_TIME)
        self.wait_malware_var = ctk.IntVar(value=config.WAIT_MALWARE_TIME)

        # Campos de entrada
        self.create_entry("Nombre de la VM:", self.vm_name_var, 1)
        self.create_entry("Nombre del Snapshot:", self.snapshot_name_var, 2)
        self.create_entry("Usuario Guest:", self.guest_user_var, 3)
        self.create_entry("Contraseña Guest:", self.guest_pass_var, 4, show="*")
        
        self.create_entry("Clave ZIP Malware:", self.compress_key_var, 5)
        self.create_entry("Espera Arranque VM (s):", self.wait_start_var, 6)
        self.create_entry("Espera Malware (s):", self.wait_malware_var, 7)

        # Botón Guardar
        self.save_btn = ctk.CTkButton(self, text="Guardar Configuración", fg_color="green", hover_color="darkgreen", command=self.save_settings)
        self.save_btn.grid(row=8, column=0, columnspan=2, pady=30)
        
        self.status_label = ctk.CTkLabel(self, text="", text_color="green")
        self.status_label.grid(row=9, column=0, columnspan=2)

    def create_entry(self, label_text, variable, row, show=""):
        label = ctk.CTkLabel(self, text=label_text, font=ctk.CTkFont(weight="bold"))
        label.grid(row=row, column=0, pady=10, padx=20, sticky="e")
        
        entry = ctk.CTkEntry(self, textvariable=variable, width=300, show=show)
        entry.grid(row=row, column=1, pady=10, padx=20, sticky="w")

    def save_settings(self):
        updates = {
            "VM_NAME": self.vm_name_var.get(),
            "SNAPSHOT_NAME": self.snapshot_name_var.get(),
            "GUEST_USER": self.guest_user_var.get(),
            "GUEST_PASS": self.guest_pass_var.get(),
            "COMPRESS_KEY": self.compress_key_var.get(),
            "WAIT_START_TIME": self.wait_start_var.get(),
            "WAIT_MALWARE_TIME": self.wait_malware_var.get()
        }
        
        try:
            file_handler.update_config_file(updates)
            self.status_label.configure(text="¡Configuración guardada correctamente!", text_color="green")
        except Exception as e:
            self.status_label.configure(text=f"Error al guardar: {e}", text_color="red")
        
        # Limpiar mensaje después de 3 segundos
        self.after(3000, lambda: self.status_label.configure(text=""))
