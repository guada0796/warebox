import customtkinter as ctk

from gui.views.dashboard_view import DashboardView
from gui.views.detonation_view import DetonationView
from gui.views.snapshot_view import SnapshotView
from gui.views.config_view import ConfigView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WAREBOX - Malware Sandbox")
        self.geometry("900x600")

        # Configurar la cuadrícula (1 fila, 2 columnas)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="WAREBOX", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard)
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        self.btn_detonation = ctk.CTkButton(self.sidebar_frame, text="Detonación", command=self.show_detonation)
        self.btn_detonation.grid(row=2, column=0, padx=20, pady=10)

        self.btn_snapshots = ctk.CTkButton(self.sidebar_frame, text="Snapshots", command=self.show_snapshots)
        self.btn_snapshots.grid(row=3, column=0, padx=20, pady=10)

        self.btn_config = ctk.CTkButton(self.sidebar_frame, text="Configuración", command=self.show_config)
        self.btn_config.grid(row=4, column=0, padx=20, pady=10)

        # --- Área Principal ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Instanciar las vistas una sola vez
        self.views = {
            "dashboard": DashboardView(self.main_frame, self.show_detonation, fg_color="transparent"),
            "detonation": DetonationView(self.main_frame, fg_color="transparent"),
            "snapshots": SnapshotView(self.main_frame, fg_color="transparent"),
            "config": ConfigView(self.main_frame, fg_color="transparent")
        }
        
        self.current_frame = None
        self.show_dashboard()

    def _hide_current_frame(self):
        if self.current_frame is not None:
            self.current_frame.pack_forget()

    def show_dashboard(self):
        self._hide_current_frame()
        self.current_frame = self.views["dashboard"]
        self.current_frame.pack(fill="both", expand=True)

    def show_detonation(self):
        self._hide_current_frame()
        self.current_frame = self.views["detonation"]
        self.current_frame.pack(fill="both", expand=True)

    def show_snapshots(self):
        self._hide_current_frame()
        self.current_frame = self.views["snapshots"]
        self.current_frame.pack(fill="both", expand=True)

    def show_config(self):
        self._hide_current_frame()
        self.current_frame = self.views["config"]
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
