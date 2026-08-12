import customtkinter as ctk

from gui.views.dashboard_view import DashboardView
from gui.views.detonation_view import DetonationView
from gui.views.snapshot_view import SnapshotView
from gui.views.config_view import ConfigView
from gui.views.analysis_view import AnalysisView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

import tkinter as tk

# Removida clase DualScrollableFrame

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WAREBOX - Malware Sandbox")
        self.geometry("900x600")

        # Maximizar ventana (Soporte cruzado para Linux/Windows)
        try:
            self.state('zoomed')
        except:
            self.attributes('-zoomed', True)

        # Configurar la cuadrícula (1 fila, 2 columnas)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0) # Ancho dinámico ajustado al contenido
        self.grid_columnconfigure(1, weight=1) # Todo el espacio restante para el área principal

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1) # Empuja el contenido hacia los extremos

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="WAREBOX", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Separador visual debajo del logo
        self.logo_separator = ctk.CTkFrame(self.sidebar_frame, height=2, fg_color="gray30")
        self.logo_separator.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        # Botones de navegación (Estilo menú lateral)
        nav_font = ctk.CTkFont(size=14)
        
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="📊  Dashboard", font=nav_font, fg_color="transparent", text_color="gray80", hover_color="gray25", anchor="w", command=self.show_dashboard)
        self.btn_dashboard.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        self.btn_detonation = ctk.CTkButton(self.sidebar_frame, text="💣  Detonación", font=nav_font, fg_color="transparent", text_color="gray80", hover_color="gray25", anchor="w", command=self.show_detonation)
        self.btn_detonation.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        self.btn_analysis = ctk.CTkButton(self.sidebar_frame, text="🔍  Análisis", font=nav_font, fg_color="transparent", text_color="gray80", hover_color="gray25", anchor="w", command=self.show_analysis)
        self.btn_analysis.grid(row=4, column=0, padx=15, pady=5, sticky="ew")

        self.btn_snapshots = ctk.CTkButton(self.sidebar_frame, text="📸  Snapshots", font=nav_font, fg_color="transparent", text_color="gray80", hover_color="gray25", anchor="w", command=self.show_snapshots)
        self.btn_snapshots.grid(row=5, column=0, padx=15, pady=5, sticky="ew")

        self.btn_config = ctk.CTkButton(self.sidebar_frame, text="⚙️  Configuración", font=nav_font, fg_color="transparent", text_color="gray80", hover_color="gray25", anchor="w", command=self.show_config)
        self.btn_config.grid(row=6, column=0, padx=15, pady=5, sticky="ew")

        # --- Resumen de Configuración (Sidebar Inferior) ---
        self.config_summary = ctk.CTkScrollableFrame(self.sidebar_frame, fg_color="#1a1a1a", corner_radius=5, width=300)
        self.config_summary.grid(row=7, column=0, padx=15, pady=(20, 20), sticky="nsew")

        self.summary_title = ctk.CTkLabel(self.config_summary, text="ESTADO DE CONFIGURACIÓN", font=ctk.CTkFont(size=11, weight="bold"), text_color="#d4af37")
        self.summary_title.pack(pady=(10, 15))

        self.summary_labels = {}
        
        # --- Área Principal ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Instanciar las vistas una sola vez
        self.views = {
            "dashboard": DashboardView(self.main_frame, self.show_detonation, fg_color="transparent"),
            "detonation": DetonationView(self.main_frame, fg_color="transparent"),
            "analysis": AnalysisView(self.main_frame, fg_color="transparent"),
            "snapshots": SnapshotView(self.main_frame, fg_color="transparent"),
            "config": ConfigView(self.main_frame, fg_color="transparent")
        }
        
        self.current_frame = None
        self.show_dashboard()
        self.update_sidebar_config()

    def update_sidebar_config(self):
        import importlib
        from utils import config
        # Nos aseguramos de leer la versión más reciente en memoria
        # (file_handler se encarga de hacer reload de config si cambia)
        
        keys = [
            ("VM_NAME", "Sandbox VM"),
            ("SNAPSHOT_NAME", "Snapshot Actual"),
            ("GUEST_USER", "Usuario Guest"),
            ("GUEST_PASS", "Contraseña Guest"),
            ("COMPRESS_KEY", "Clave ZIP"),
            ("ZIP_FILENAME", "Muestra ZIP"),
            ("PAYLOAD_NAME", "Payload"),
            ("WAIT_START_TIME", "T. Arranque (s)"),
            ("WAIT_MALWARE_TIME", "T. Análisis (s)"),
            ("WAIT_WRITE_FILES_TIME", "T. Escritura (s)"),
            ("GUEST_TOOLS_DIR", "Dir Tools (Guest)"),
            ("GUEST_LOG_DIR", "Dir Logs (Guest)"),
            ("HOST_MALWARE_DIR", "Dir Malware (Host)"),
            ("HOST_EVIDENCE_DIR", "Dir Evidencia (Host)"),
            ("TIMESTAMP_SIGNATURE", "Firma Actual")
        ]

        for idx, (key, display_name) in enumerate(keys):
            val = getattr(config, key, "N/A")
            if key not in self.summary_labels:
                frame = ctk.CTkFrame(self.config_summary, fg_color="transparent")
                # Espacio amplio entre configuraciones distintas
                frame.pack(fill="x", pady=(0, 10))
                
                # Espacio mínimo entre el título y el valor
                lbl_name = ctk.CTkLabel(frame, text=display_name.upper(), font=ctk.CTkFont(size=10, weight="bold"), text_color="gray50")
                lbl_name.pack(side="top", anchor="w", pady=0, padx=10)
                
                # Aumentado a 270px de ancho (+50%)
                lbl_val = ctk.CTkLabel(frame, text=str(val), font=ctk.CTkFont(size=12), text_color="gray90", justify="left", wraplength=270)
                lbl_val.pack(side="top", anchor="w", padx=10, pady=0)
                
                self.summary_labels[key] = lbl_val
            else:
                self.summary_labels[key].configure(text=str(val))
                
        self.after(2000, self.update_sidebar_config)

    def _reset_nav_buttons(self):
        """Reinicia el estilo de todos los botones de navegación."""
        buttons = [self.btn_dashboard, self.btn_detonation, self.btn_analysis, self.btn_snapshots, self.btn_config]
        for btn in buttons:
            btn.configure(fg_color="transparent", text_color="gray80")

    def _set_active_btn(self, button):
        """Aplica estilo activo al botón seleccionado."""
        self._reset_nav_buttons()
        # Usa el color de acento por defecto (azul) para el fondo
        button.configure(fg_color=["#3B8ED0", "#1F6AA5"], text_color="white")

    def _hide_current_frame(self):
        if self.current_frame is not None:
            self.current_frame.pack_forget()

    def show_dashboard(self):
        self._hide_current_frame()
        self._set_active_btn(self.btn_dashboard)
        self.current_frame = self.views["dashboard"]
        self.current_frame.pack(fill="both", expand=True)

    def show_detonation(self):
        self._hide_current_frame()
        self._set_active_btn(self.btn_detonation)
        self.current_frame = self.views["detonation"]
        self.current_frame.pack(fill="both", expand=True)

    def show_analysis(self):
        self._hide_current_frame()
        self._set_active_btn(self.btn_analysis)
        self.current_frame = self.views["analysis"]
        self.current_frame.pack(fill="both", expand=True)

    def show_snapshots(self):
        self._hide_current_frame()
        self._set_active_btn(self.btn_snapshots)
        self.current_frame = self.views["snapshots"]
        self.current_frame.pack(fill="both", expand=True)

    def show_config(self):
        self._hide_current_frame()
        self._set_active_btn(self.btn_config)
        self.current_frame = self.views["config"]
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
