import customtkinter as ctk
from utils import config
import os

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, navigate_to_detonation, **kwargs):
        super().__init__(master, **kwargs)
        
        self.navigate_to_detonation = navigate_to_detonation

        # Contenedor central para que todo se centre al maximizar
        self.center_container = ctk.CTkFrame(self, fg_color="transparent")
        self.center_container.pack(expand=True)

        self.title_label = ctk.CTkLabel(self.center_container, text="Dashboard de WAREBOX", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.pack(pady=(20, 40))

        # Tarjetas de Información
        self.cards_frame = ctk.CTkFrame(self.center_container, fg_color="transparent")
        self.cards_frame.pack(pady=10)
        
        self.create_info_card(self.cards_frame, "Sandbox VM", config.VM_NAME, config.SNAPSHOT_NAME, 0)
        self.create_info_card(self.cards_frame, "Network VM", config.NETWORK_VM_NAME, config.NETWORK_SNAPSHOT_NAME, 1)
        
        # Muestra actual (si existe)
        malware_count = len([f for f in os.listdir(config.HOST_MALWARE_DIR) if f.lower().endswith(".zip")]) if os.path.exists(config.HOST_MALWARE_DIR) else 0
        self.create_info_card(self.cards_frame, "Muestras Pendientes", str(malware_count), "", 2)

        # Call to Action
        self.cta_frame = ctk.CTkFrame(self.center_container, corner_radius=15, fg_color="#2b2b2b")
        self.cta_frame.pack(pady=50, fill="x")
        
        cta_label = ctk.CTkLabel(self.cta_frame, text="¿Listo para analizar una nueva muestra?", font=ctk.CTkFont(size=20))
        cta_label.pack(pady=(20, 10))
        
        self.btn_start = ctk.CTkButton(self.cta_frame, text="Iniciar Nueva Detonación", font=ctk.CTkFont(weight="bold", size=16), 
                                       fg_color="#1f538d", hover_color="#14375d", height=40, command=self.navigate_to_detonation)
        self.btn_start.pack(pady=(0, 20))

    def create_info_card(self, parent, title, value, subtitle, col):
        card = ctk.CTkFrame(parent, corner_radius=10, width=220, height=110)
        card.grid(row=0, column=col, padx=10)
        card.grid_propagate(False)
        
        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="gray")
        title_label.place(relx=0.5, rely=0.25, anchor="center")
        
        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"))
        value_label.place(relx=0.5, rely=0.55, anchor="center")

        if subtitle:
            subtitle_label = ctk.CTkLabel(card, text=f"({subtitle})", font=ctk.CTkFont(size=12), text_color="lightgray")
            subtitle_label.place(relx=0.5, rely=0.8, anchor="center")
