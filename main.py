"""
@file main.py
@brief main application for the kasir app
"""
import customtkinter as ctk
from data_manager import DataManager

# import ui modules
from inventory_ui import InventoryFrame
from scanner_ui import ScannerFrame
from analytic_ui import AnalyticsFrame

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CashierApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TUBES - CASHIER APP")
        self.geometry("1200x750")
        
        # init data
        self.data_manager = DataManager()

        #setup layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_pages()
        
        #inventory_ui as main page
        self.show_frame("inventory")

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="TUBES BERKOM2", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=20)

        ctk.CTkButton(self.sidebar, text="Inventory", command=lambda: self.show_frame("inventory")).grid(row=1, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar, text="Scan QR / CheckOut", command=lambda: self.show_frame("scan")).grid(row=2, column=0, padx=20, pady=10)
        ctk.CTkButton(self.sidebar, text="Analytics", command=lambda: self.show_frame("stats")).grid(row=3, column=0, padx=20, pady=10)

    def create_pages(self):
        self.frames = {}
        
        self.frames["inventory"] = InventoryFrame(self, self.data_manager)
        self.frames["scan"] = ScannerFrame(self, self.data_manager)
        self.frames["stats"] = AnalyticsFrame(self, self.data_manager)

        for frame in self.frames.values():
            frame.grid(row=0, column=1, sticky="nsew")

    def show_frame(self, page_name):
        # camera handler
        scanner = self.frames["scan"]
        if page_name != "scan":
            scanner.stop_scanning()
            
        # request frame
        frame = self.frames[page_name]
        frame.tkraise()
        
        # page logic handler
        if page_name == "scan":
            scanner.start_scanning()
        elif page_name == "stats":
            self.frames["stats"].update_stats()

if __name__ == "__main__":
    app = CashierApp()
    app.mainloop()