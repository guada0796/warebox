import customtkinter as ctk
import subprocess
import threading
from utils import config
from services import vbox_manager as vbox

class SnapshotView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.title_label = ctk.CTkLabel(self, text="Gestión de Snapshots", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(20, 10), padx=20, anchor="w")

        # Info de la VM actual
        self.info_label = ctk.CTkLabel(self, text=f"Máquina Virtual seleccionada: {config.VM_NAME}", text_color="gray")
        self.info_label.pack(anchor="w", padx=20)

        # Controles
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(fill="x", padx=20, pady=20)

        self.snap_name_var = ctk.StringVar()
        self.snap_entry = ctk.CTkEntry(self.controls_frame, textvariable=self.snap_name_var, placeholder_text="Nombre del Snapshot...", width=200)
        self.snap_entry.grid(row=0, column=0, padx=10)

        self.btn_create = ctk.CTkButton(self.controls_frame, text="Crear", fg_color="green", hover_color="darkgreen", command=self.create_snapshot)
        self.btn_create.grid(row=0, column=1, padx=10)

        self.btn_restore = ctk.CTkButton(self.controls_frame, text="Restaurar", command=self.restore_snapshot)
        self.btn_restore.grid(row=0, column=2, padx=10)

        self.btn_delete = ctk.CTkButton(self.controls_frame, text="Eliminar", fg_color="darkred", hover_color="#8b0000", command=self.delete_snapshot)
        self.btn_delete.grid(row=0, column=3, padx=10)

        self.btn_list = ctk.CTkButton(self.controls_frame, text="Listar Snapshots", fg_color="gray", hover_color="darkgray", command=self.list_snapshots)
        self.btn_list.grid(row=0, column=4, padx=10)

        # Consola
        self.console_text = ctk.CTkTextbox(self, state="disabled", fg_color="black", text_color="green", font=ctk.CTkFont(family="Consolas", size=12))
        self.console_text.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        
        self.list_snapshots()

    def log(self, message):
        self.console_text.configure(state="normal")
        self.console_text.insert("end", message + "\n")
        self.console_text.see("end")
        self.console_text.configure(state="disabled")

    def create_snapshot(self):
        name = self.snap_name_var.get()
        if not name:
            self.log("❌ Error: Debes introducir un nombre para el snapshot.")
            return
        
        self.log(f"⏳ Creando snapshot '{name}'...")
        threading.Thread(target=self._run_vbox_cmd, args=(["VBoxManage", "snapshot", config.VM_NAME, "take", name], f"Snapshot '{name}' creado exitosamente."), daemon=True).start()

    def restore_snapshot(self):
        name = self.snap_name_var.get()
        if not name:
            self.log("❌ Error: Debes introducir un nombre para el snapshot.")
            return
        
        self.log(f"⏳ Restaurando snapshot '{name}'...")
        threading.Thread(target=self._run_vbox_cmd, args=(["VBoxManage", "snapshot", config.VM_NAME, "restore", name], f"VM restaurada al snapshot '{name}'."), daemon=True).start()

    def delete_snapshot(self):
        name = self.snap_name_var.get()
        if not name:
            self.log("❌ Error: Debes introducir un nombre para el snapshot.")
            return
        
        self.log(f"⏳ Eliminando snapshot '{name}'...")
        threading.Thread(target=self._run_vbox_cmd, args=(["VBoxManage", "snapshot", config.VM_NAME, "delete", name], f"Snapshot '{name}' eliminado permanentemente."), daemon=True).start()

    def _run_vbox_cmd(self, command, success_msg):
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
            self.log(f"✅ {success_msg}")
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Error de VirtualBox: {e.stderr.strip()}")
            
    def list_snapshots(self):
        self.log(f"🔍 Buscando snapshots para la VM '{config.VM_NAME}'...")
        command = ["VBoxManage", "snapshot", config.VM_NAME, "list"]
        
        def _list():
            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
                if result.stdout:
                    self.log(result.stdout.strip())
                else:
                    self.log("⚠️ No se encontraron snapshots.")
            except subprocess.CalledProcessError as e:
                if "Could not find a snapshot" in e.stderr:
                    self.log("⚠️ No se encontraron snapshots.")
                else:
                    self.log(f"❌ Error al listar: {e.stderr.strip()}")
                    
        threading.Thread(target=_list, daemon=True).start()
