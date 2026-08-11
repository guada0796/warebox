import customtkinter as ctk
import subprocess
import threading
from utils import config
from services import vbox_manager as vbox

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
        
        self.btn_yes = ctk.CTkButton(btn_frame, text="Sí, Eliminar", fg_color="darkred", hover_color="#8b0000", command=self.on_yes)
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

class SnapshotView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.title_label = ctk.CTkLabel(self, text="Gestión de Snapshots", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(20, 10), padx=20, anchor="w")

        # Info de la VM actual
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20)
        
        self.info_label = ctk.CTkLabel(self.header_frame, text=f"Máquina Virtual: {config.VM_NAME}", text_color="gray")
        self.info_label.pack(side="left")
        
        self.current_state_label = ctk.CTkLabel(self.header_frame, text="Estado Actual: Buscando...", font=ctk.CTkFont(weight="bold", size=16), text_color="#2fa572")
        self.current_state_label.pack(side="right")

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
        # Se remueve el state="disabled" inicial para permitir la selección de texto
        self.console_text = ctk.CTkTextbox(self, fg_color="black", text_color="green", font=ctk.CTkFont(family="Consolas", size=12))
        self.console_text.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        
        # Bloquear la escritura manual pero permitir atajos como Ctrl+C
        self.console_text.bind("<KeyPress>", self.prevent_typing)
        
        self.list_snapshots()

    def prevent_typing(self, event):
        # Permite Ctrl+C (Windows/Linux) o Command+C (Mac) para copiar texto seleccionado
        if (event.state & 0x0004 or event.state & 0x0008) and event.keysym.lower() in ['c', 'a']:
            return None # Permite el evento (copiar o seleccionar todo)
        # Bloquear cualquier otro tipo de inserción o modificación
        return "break"

    def clear_console(self):
        self.console_text.delete("1.0", "end")

    def log(self, message):
        # Ya no necesitamos cambiar el estado ya que se bloquea con los eventos
        self.console_text.insert("end", message + "\n")
        self.console_text.see("end")

    def create_snapshot(self):
        name = self.snap_name_var.get()
        if not name:
            self.clear_console()
            self.log("❌ Error: Debes introducir un nombre para el snapshot.")
            return
        
        self.clear_console()
        self.log(f"⏳ Creando snapshot '{name}'...")
        # Pasamos 'name' como restore_name para que actualice la configuración
        threading.Thread(target=self._run_vbox_cmd_and_list, args=(["VBoxManage", "snapshot", config.VM_NAME, "take", name], f"Snapshot '{name}' creado exitosamente.", name), daemon=True).start()

    def restore_snapshot(self):
        name = self.snap_name_var.get()
        if not name:
            self.clear_console()
            self.log("❌ Error: Debes introducir un nombre para el snapshot.")
            return
        
        self.clear_console()
        self.log(f"⏳ Restaurando snapshot '{name}'...")
        threading.Thread(target=self._run_vbox_cmd_and_list, args=(["VBoxManage", "snapshot", config.VM_NAME, "restore", name], f"VM restaurada al snapshot '{name}'.", name), daemon=True).start()

    def delete_snapshot(self):
        name = self.snap_name_var.get()
        if not name:
            self.clear_console()
            self.log("❌ Error: Debes introducir un nombre para el snapshot.")
            return
            
        dialog = CTkConfirmDialog(self, "Confirmar Eliminación", f"¿Estás seguro de que quieres eliminar permanentemente el snapshot '{name}'?")
        confirm = dialog.get_input()
        if not confirm:
            self.log("⚠️ Eliminación cancelada.")
            return
        
        self.clear_console()
        self.log(f"⏳ Eliminando snapshot '{name}'...")
        # Pasamos "AUTO_DETECT" como restore_name para indicar que busque y guarde el estado actual después de eliminar
        threading.Thread(target=self._run_vbox_cmd_and_list, args=(["VBoxManage", "snapshot", config.VM_NAME, "delete", name], f"Snapshot '{name}' eliminado permanentemente.", "AUTO_DETECT"), daemon=True).start()

    def _run_vbox_cmd_and_list(self, command, success_msg, restore_name=None):
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
            self.log(f"✅ {success_msg}")
            
            if restore_name and restore_name != "AUTO_DETECT":
                from core import file_handler
                file_handler.update_config_file({"SNAPSHOT_NAME": restore_name})
                self.log(f"✅ Configuración actualizada: El snapshot a detonar ahora es '{restore_name}'")
                
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Error de VirtualBox: {e.stderr.strip()}")
            
        self.log("\n--- Actualizando lista de Snapshots ---\n")
        # Volvemos a llamar a list_snapshots en segundo plano para que refresque la pantalla
        # Pasamos True si se requiere autodetección
        self._execute_list(auto_update_config=(restore_name == "AUTO_DETECT"))

    def list_snapshots(self):
        self.clear_console()
        threading.Thread(target=self._execute_list, daemon=True).start()

    def _execute_list(self, auto_update_config=False):
        self.log(f"🔍 Buscando snapshots para la VM '{config.VM_NAME}'...\n")
        command = ["VBoxManage", "snapshot", config.VM_NAME, "list"]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if result.stdout:
                import re
                current_snap = "Desconocido (Estado Modificado)"
                for line in result.stdout.split('\n'):
                    if '*' in line:
                        match = re.search(r'Name:\s+(.+?)\s+\(', line)
                        if match:
                            current_snap = match.group(1).strip()
                        else:
                            current_snap = "Sin Nombre"
                        break
                
                self.after(0, lambda snap=current_snap: self.current_state_label.configure(text=f"Estado Actual: {snap}"))
                self.log(result.stdout.strip())
                
                if auto_update_config and current_snap not in ["Desconocido (Estado Modificado)", "Sin Nombre"]:
                    from core import file_handler
                    file_handler.update_config_file({"SNAPSHOT_NAME": current_snap})
                    self.log(f"\n✅ Configuración actualizada automáticamente a: '{current_snap}'")
                    
            else:
                self.after(0, lambda: self.current_state_label.configure(text="Estado Actual: Ninguno"))
                self.log("⚠️ No se encontraron snapshots.")
        except subprocess.CalledProcessError as e:
            self.after(0, lambda: self.current_state_label.configure(text="Estado Actual: Error"))
            if "Could not find a snapshot" in e.stderr:
                self.log("⚠️ No se encontraron snapshots.")
            else:
                self.log(f"❌ Error al listar: {e.stderr.strip()}")
