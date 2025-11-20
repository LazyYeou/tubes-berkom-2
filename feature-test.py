import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import pandas as pd
import cv2
from pyzbar.pyzbar import decode
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from datetime import datetime
import time

# --- Configuration ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- Data Structure: Segment Tree (Kept for Inventory Value Analysis) ---
class SegmentTree:
    def __init__(self, size):
        self.size = size
        self.tree = [0] * (4 * size)

    def update(self, node, start, end, idx, val):
        if start == end:
            self.tree[node] = val
            return
        mid = (start + end) // 2
        if idx <= mid:
            self.update(2 * node, start, mid, idx, val)
        else:
            self.update(2 * node + 1, mid + 1, end, idx, val)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def update_value(self, idx, val):
        self.update(1, 0, self.size - 1, idx, val)

    def get_total_sum(self):
        return self.tree[1]

# --- Main Application ---
class ModernCashierApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Nexus POS - Modern Register")
        self.geometry("1200x750")
        
        # Data Initialization
        self.products_file = "products.csv"
        self.history_file = "sales_history.csv"
        self.cart = [] # Temporary cart for current transaction
        self.load_data()
        
        # Segment Tree Init
        self.seg_tree = SegmentTree(1000)
        self.rebuild_segment_tree()

        # Camera State
        self.cap = None
        self.scanning_active = False
        self.last_scan_time = 0

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_pages()
        self.show_frame("inventory")

    def load_data(self):
        if os.path.exists(self.products_file):
            self.df_products = pd.read_csv(self.products_file)
        else:
            self.df_products = pd.DataFrame(columns=["name", "price", "category", "qrImgUrl"])

        if os.path.exists(self.history_file):
            self.df_history = pd.read_csv(self.history_file)
        else:
            self.df_history = pd.DataFrame(columns=["product_name", "price", "qty", "total", "timestamp"])

    def rebuild_segment_tree(self):
        for idx, row in self.df_products.iterrows():
            self.seg_tree.update_value(idx, row['price'])

    def save_data(self):
        self.df_products.to_csv(self.products_file, index=False)
        self.df_history.to_csv(self.history_file, index=False)

    # --- UI Construction ---
    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="NEXUS POS", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_inv = ctk.CTkButton(self.sidebar, text="Inventory", command=lambda: self.show_frame("inventory"))
        self.btn_inv.grid(row=1, column=0, padx=20, pady=10)

        self.btn_scan = ctk.CTkButton(self.sidebar, text="Cashier (Scan)", command=lambda: self.show_frame("scan"))
        self.btn_scan.grid(row=2, column=0, padx=20, pady=10)

        self.btn_stats = ctk.CTkButton(self.sidebar, text="Analytics", command=lambda: self.show_frame("stats"))
        self.btn_stats.grid(row=3, column=0, padx=20, pady=10)

    def create_pages(self):
        self.frames = {}
        self.frames["inventory"] = self.create_inventory_frame()
        self.frames["scan"] = self.create_scan_frame()
        self.frames["stats"] = self.create_stats_frame()

    def show_frame(self, page_name):
        # Cleanup Camera if leaving scan page
        if hasattr(self, 'cap') and self.cap is not None:
            self.scanning_active = False
            self.cap.release()
            self.cap = None
            
        frame = self.frames[page_name]
        frame.grid(row=0, column=1, sticky="nsew")
        frame.tkraise()
        
        if page_name == "scan":
            self.start_camera()
        if page_name == "stats":
            self.update_stats()

    # --- 1. Inventory (Same as before) ---
    def create_inventory_frame(self):
        frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        
        input_frame = ctk.CTkFrame(frame)
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

        self.tree_inv = ttk.Treeview(frame, columns=("Name", "Price", "Category", "QR"), show="headings")
        self.tree_inv.heading("Name", text="Name")
        self.tree_inv.heading("Price", text="Price")
        self.tree_inv.heading("Category", text="Category")
        self.tree_inv.heading("QR", text="QR Data")
        self.tree_inv.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.refresh_inventory_ui()
        return frame

    def add_product(self):
        try:
            price = float(self.entry_price.get())
            new_row = {"name": self.entry_name.get(), "price": price, "category": self.entry_cat.get(), "qrImgUrl": self.entry_qr.get()}
            self.df_products = pd.concat([self.df_products, pd.DataFrame([new_row])], ignore_index=True)
            self.seg_tree.update_value(len(self.df_products) - 1, price)
            self.refresh_inventory_ui()
            self.save_data()
        except ValueError:
            messagebox.showerror("Error", "Invalid Price")

    def delete_product(self):
        selected = self.tree_inv.selection()
        for item in selected:
            val = self.tree_inv.item(item, 'values')
            self.df_products = self.df_products[self.df_products['name'] != val[0]]
        self.refresh_inventory_ui()
        self.save_data()

    def refresh_inventory_ui(self):
        for i in self.tree_inv.get_children(): self.tree_inv.delete(i)
        for _, row in self.df_products.iterrows():
            self.tree_inv.insert("", "end", values=(row['name'], row['price'], row['category'], row['qrImgUrl']))

    # --- 2. SCAN & CART LOGIC (Major Update) ---
    def create_scan_frame(self):
        frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1) # Camera
        frame.grid_columnconfigure(1, weight=1) # Cart
        frame.grid_rowconfigure(0, weight=1)

        # -- Left Side: Camera --
        cam_frame = ctk.CTkFrame(frame)
        cam_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(cam_frame, text="Scan Product QR", font=("Arial", 16, "bold")).pack(pady=10)
        self.lbl_camera = tk.Label(cam_frame, bg="black")
        self.lbl_camera.pack(expand=True, fill="both", padx=10, pady=10)
        self.lbl_status = ctk.CTkLabel(cam_frame, text="Ready to Scan", text_color="gray")
        self.lbl_status.pack(pady=10)

        # -- Right Side: Cart / Catalogue --
        cart_frame = ctk.CTkFrame(frame)
        cart_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(cart_frame, text="Current Cart", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Cart Treeview
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        self.tree_cart = ttk.Treeview(cart_frame, columns=("Product", "Price", "Qty", "Subtotal"), show="headings")
        self.tree_cart.heading("Product", text="Product")
        self.tree_cart.heading("Price", text="Price")
        self.tree_cart.heading("Qty", text="Qty")
        self.tree_cart.heading("Subtotal", text="Subtotal")
        self.tree_cart.column("Product", width=100)
        self.tree_cart.column("Price", width=60)
        self.tree_cart.column("Qty", width=50)
        self.tree_cart.column("Subtotal", width=80)
        self.tree_cart.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Checkout Section
        self.lbl_total = ctk.CTkLabel(cart_frame, text="Total: $0.00", font=("Arial", 20, "bold"))
        self.lbl_total.pack(pady=10)
        
        self.btn_checkout = ctk.CTkButton(cart_frame, text="CHECKOUT", fg_color="green", height=50, command=self.checkout)
        self.btn_checkout.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(cart_frame, text="Clear Cart", fg_color="red", command=self.clear_cart).pack(pady=5)

        return frame

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.scanning_active = True
        self.update_camera()

    def update_camera(self):
        if self.cap is not None and self.scanning_active:
            ret, frame = self.cap.read()
            if ret:
                # 1. Detect QR
                decoded_objs = decode(frame)
                
                # 2. Process Detection (with cooldown)
                current_time = time.time()
                if decoded_objs and (current_time - self.last_scan_time > 2.0):
                    qr_data = decoded_objs[0].data.decode('utf-8')
                    self.handle_scan(qr_data)
                
                # 3. Update UI Image
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.lbl_camera.imgtk = imgtk
                self.lbl_camera.configure(image=imgtk)
            
            self.lbl_camera.after(20, self.update_camera)

    def handle_scan(self, qr_data):
        # Pause Camera Logic
        self.scanning_active = False
        
        # Find Product
        product = self.df_products[self.df_products['qrImgUrl'] == qr_data]
        
        if not product.empty:
            p_name = product.iloc[0]['name']
            p_price = product.iloc[0]['price']
            
            # Ask for Quantity
            dialog = ctk.CTkInputDialog(text=f"Product Detected: {p_name}\nPrice: ${p_price}\n\nEnter Quantity:", title="Add to Cart")
            qty_str = dialog.get_input()
            
            if qty_str and qty_str.isdigit():
                qty = int(qty_str)
                if qty > 0:
                    subtotal = p_price * qty
                    self.add_to_cart(p_name, p_price, qty, subtotal)
                    self.lbl_status.configure(text=f"Added {qty} x {p_name}", text_color="green")
                else:
                    self.lbl_status.configure(text="Quantity must be > 0", text_color="orange")
            else:
                self.lbl_status.configure(text="Scan Cancelled", text_color="yellow")
        else:
            messagebox.showwarning("Unknown", f"Product not found: {qr_data}")
            self.lbl_status.configure(text="Product Not Found", text_color="red")
            
        # Resume Camera Logic
        self.last_scan_time = time.time()
        self.scanning_active = True
        self.update_camera()

    def add_to_cart(self, name, price, qty, subtotal):
        # Add to internal list
        self.cart.append({
            "product_name": name,
            "price": price,
            "qty": qty,
            "total": subtotal,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.update_cart_ui()

    def update_cart_ui(self):
        # Clear tree
        for i in self.tree_cart.get_children():
            self.tree_cart.delete(i)
        
        grand_total = 0
        for item in self.cart:
            self.tree_cart.insert("", "end", values=(item["product_name"], item["price"], item["qty"], item["total"]))
            grand_total += item["total"]
            
        self.lbl_total.configure(text=f"Total: ${grand_total:.2f}")

    def clear_cart(self):
        self.cart = []
        self.update_cart_ui()

    def checkout(self):
        if not self.cart:
            messagebox.showinfo("Empty", "Cart is empty!")
            return
            
        # Add cart items to history dataframe
        new_sales = pd.DataFrame(self.cart)
        self.df_history = pd.concat([self.df_history, new_sales], ignore_index=True)
        
        # Save
        self.save_data()
        
        # Feedback
        total = sum(item['total'] for item in self.cart)
        messagebox.showinfo("Success", f"Transaction Completed!\nTotal Revenue: ${total:.2f}")
        
        self.clear_cart()

    # --- 3. Analytics (Updated) ---
    def create_stats_frame(self):
        frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.stats_text = ctk.CTkTextbox(frame, height=100)
        self.stats_text.pack(fill="x", padx=20, pady=10)
        self.chart_frame = ctk.CTkFrame(frame)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
        return frame

    def update_stats(self):
        total_revenue = self.df_history['total'].sum() if 'total' in self.df_history.columns else 0
        total_inv = self.seg_tree.get_total_sum()
        
        self.stats_text.delete("0.0", "end")
        self.stats_text.insert("0.0", f"Total Revenue: ${total_revenue:.2f}\nInventory Value: ${total_inv:.2f}")
        
        for w in self.chart_frame.winfo_children(): w.destroy()
        
        if not self.df_history.empty:
            fig, ax = plt.subplots(figsize=(5,4))
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#2b2b2b')
            self.df_history.groupby('product_name')['qty'].sum().plot(kind='bar', ax=ax, color='#1f538d')
            ax.tick_params(colors='white')
            ax.set_title("Items Sold", color='white')
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    app = ModernCashierApp()
    app.mainloop()