import customtkinter as ctk

class CustomMessageBox(ctk.CTkToplevel):
    def __init__(self, title, message, type="info", master=None):
        super().__init__(master=master)
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Center the window
        self.update_idletasks()
        if master:
            x = master.winfo_rootx() + (master.winfo_width() // 2) - (400 // 2)
            y = master.winfo_rooty() + (master.winfo_height() // 2) - (200 // 2)
        else:
            x = (self.winfo_screenwidth() // 2) - (400 // 2)
            y = (self.winfo_screenheight() // 2) - (200 // 2)
        self.geometry(f"+{x}+{y}")

        self.result = None

        self.label = ctk.CTkLabel(self, text=message, wraplength=350, font=ctk.CTkFont(size=14))
        self.label.pack(expand=True, pady=20, padx=20)

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=15)

        if type == "askyesno":
            self.btn_yes = ctk.CTkButton(self.btn_frame, text="Sí", command=self.on_yes, width=100)
            self.btn_yes.pack(side="left", padx=10)
            self.btn_no = ctk.CTkButton(self.btn_frame, text="No", command=self.on_no, width=100, fg_color="gray", hover_color="#555555")
            self.btn_no.pack(side="left", padx=10)
        else:
            # Color adjustments based on type
            btn_color = "#1f538d"
            hover_color = "#14375d"
            if type == "error":
                btn_color = "#8b0000"
                hover_color = "#5c0000"
            elif type == "warning":
                btn_color = "#8b8000"
                hover_color = "#665c00"

            self.btn_ok = ctk.CTkButton(self.btn_frame, text="Aceptar", command=self.on_ok, width=100, fg_color=btn_color, hover_color=hover_color)
            self.btn_ok.pack()

        # Make it modal
        self.grab_set()
        self.wait_window()

    def on_yes(self):
        self.result = True
        self.destroy()

    def on_no(self):
        self.result = False
        self.destroy()
        
    def on_ok(self):
        self.result = True
        self.destroy()

def showinfo(title, message, master=None):
    msg = CustomMessageBox(title, message, "info", master)
    return msg.result

def showwarning(title, message, master=None):
    msg = CustomMessageBox(title, message, "warning", master)
    return msg.result

def showerror(title, message, master=None):
    msg = CustomMessageBox(title, message, "error", master)
    return msg.result

def askyesno(title, message, master=None):
    msg = CustomMessageBox(title, message, "askyesno", master)
    return msg.result
