"""
@file inventory_ui.py
@brief ui for inventory page
"""
import customtkinter as ctk
from tkinter import ttk, messagebox

class InventoryFrame(ctk.CTkFrame):
    def __init__(self, parent, data_manager):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.data_manager = data_manager
        
        self._create_widgets()
        self.refresh_ui()

    def _create_widgets(self):
        # input area
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=20, pady=20)
        
        self.entry_name = ctk.CTkEntry(input_frame, placeholder_text="Product Name")
        self.entry_name.pack(side="left", padx=5, pady=10)
        self.entry_price = ctk.CTkEntry(input_frame, placeholder_text="Price", width=80)
        self.entry_price.pack(side="left", padx=5, pady=10)
        self.entry_cat = ctk.CTkEntry(input_frame, placeholder_text="Category")
        self.entry_cat.pack(side="left", padx=5, pady=10)
        self.entry_qr = ctk.CTkEntry(input_frame, placeholder_text="QR Data")
        self.entry_qr.pack(side="left", padx=5, pady=10)
        
        ctk.CTkButton(input_frame, text="Add", width=60, command=self.add_product).pack(side="left", padx=5)
        ctk.CTkButton(input_frame, text="Del", width=60, fg_color="red", command=self.delete_product).pack(side="left", padx=5)

        # products table
        self.tree_inv = ttk.Treeview(self, columns=("Name", "Price", "Category", "QR"), show="headings")
        self.tree_inv.heading("Name", text="Name")
        self.tree_inv.heading("Price", text="Price")
        self.tree_inv.heading("Category", text="Category")
        self.tree_inv.heading("QR", text="QR Data")
        self.tree_inv.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def add_product(self):
        '''
        @brief add product to inventory table
        '''
        try:
            price = float(self.entry_price.get())
            self.data_manager.add_product(
                self.entry_name.get(), 
                price, 
                self.entry_cat.get(), 
                self.entry_qr.get()
            )
            self.refresh_ui()
            
            self.entry_name.delete(0, 'end')
            self.entry_price.delete(0, 'end')
        except ValueError:
            messagebox.showerror("Error", "Invalid Price")

    def delete_product(self):
        '''
        @brief delete product from inventory table
        '''
        selected = self.tree_inv.selection()
        if not selected:
            return
        for item in selected:
            val = self.tree_inv.item(item, 'values')
            self.data_manager.delete_product_by_name(val[0])
        self.refresh_ui()

    def refresh_ui(self):
        '''
        @brief refresh inventory table data
        '''
        for i in self.tree_inv.get_children(): 
            self.tree_inv.delete(i)
        for _, row in self.data_manager.df_products.iterrows():
            self.tree_inv.insert("", "end", values=(row['name'], row['price'], row['category'], row['qr_data']))