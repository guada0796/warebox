import customtkinter as ctk

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
        
        self.current_frame = None
        self.show_dashboard()

    def _clear_main_frame(self):
        if self.current_frame is not None:
            self.current_frame.destroy()

    def show_dashboard(self):
        self._clear_main_frame()
        from gui.views.dashboard_view import DashboardView
        self.current_frame = DashboardView(self.main_frame, self.show_detonation, fg_color="transparent")
        self.current_frame.pack(fill="both", expand=True)

    def show_detonation(self):
        self._clear_main_frame()
        from gui.views.detonation_view import DetonationView
        self.current_frame = DetonationView(self.main_frame, fg_color="transparent")
        self.current_frame.pack(fill="both", expand=True)

    def show_snapshots(self):
        self._clear_main_frame()
        from gui.views.snapshot_view import SnapshotView
        self.current_frame = SnapshotView(self.main_frame, fg_color="transparent")
        self.current_frame.pack(fill="both", expand=True)

    def show_config(self):
        self._clear_main_frame()
        from gui.views.config_view import ConfigView
        self.current_frame = ConfigView(self.main_frame, fg_color="transparent")
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
