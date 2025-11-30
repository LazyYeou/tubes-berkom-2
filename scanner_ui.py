"""
@file scanner_ui.py
@brief UI to handle qr scan and cart 
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from pyzbar.pyzbar import decode
from PIL import Image, ImageTk
import time
from datetime import datetime

class ScannerFrame(ctk.CTkFrame):
    """
    @brief UI for QR scanning and cart system
    """
    def __init__(self, parent, data_manager):
        """
        @brief constructor of scan dataframe
        """
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.data_manager = data_manager
        self.cart = []
        
        # camera state
        self.cap = None
        self.scanning_active = False
        self.last_scan_time = 0

        self._setup_layout()

    def _setup_layout(self):
        """
        @brief create and set the widgets layout of scanner UI
        """
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # qr scan part
        cam_frame = ctk.CTkFrame(self)
        cam_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(cam_frame, text="Scan Product QR", font=("Arial", 16, "bold")).pack(pady=10)
        self.lbl_camera = tk.Label(cam_frame, bg="black")
        self.lbl_camera.pack(expand=True, fill="both", padx=10, pady=10)
        self.lbl_status = ctk.CTkLabel(cam_frame, text="Ready to Scan", text_color="gray")
        self.lbl_status.pack(pady=10)

        # cart system part
        cart_frame = ctk.CTkFrame(self)
        cart_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(cart_frame, text="Current Cart", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.tree_cart = ttk.Treeview(cart_frame, columns=("Product", "Price", "Qty", "Subtotal"), show="headings")
        self.tree_cart.heading("Product", text="Product")
        self.tree_cart.heading("Price", text="Price")
        self.tree_cart.heading("Qty", text="Qty")
        self.tree_cart.heading("Subtotal", text="Subtotal")
        self.tree_cart.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.lbl_total = ctk.CTkLabel(cart_frame, text="Total: Rp0.00", font=("Arial", 20, "bold"))
        self.lbl_total.pack(pady=10)
        
        self.btn_checkout = ctk.CTkButton(cart_frame, text="CHECKOUT", fg_color="green", height=50, command=self.checkout)
        self.btn_checkout.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(cart_frame, text="Clear Cart", fg_color="red", command=self.clear_cart).pack(pady=5)

    def start_scanning(self):
        """
        @brief start camera and activate scanning
        """
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
        self.scanning_active = True
        self._update_camera_loop()

    def stop_scanning(self):
        """
        @brief stop scanning
        """
        self.scanning_active = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def _update_camera_loop(self):
        """
        @brief read a frame, decode QR codes
        """
        if self.cap is not None and self.scanning_active:
            ret, frame = self.cap.read()
            if ret:
                decoded_objs = decode(frame)
                current_time = time.time()
                
                if decoded_objs and (current_time - self.last_scan_time > 2.0):
                    qr_data = decoded_objs[0].data.decode('utf-8')
                    self._handle_scan(qr_data)
                
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.lbl_camera.imgtk = imgtk
                self.lbl_camera.configure(image=imgtk)
            
            #recursive call camera
            self.lbl_camera.after(20, self._update_camera_loop)

    def _handle_scan(self, qr_data):
        """
        @brief handle qr scan and search the product in prodcut dataframe

        @param qr_data the decoded QR string
        """
        self.scanning_active = False 
        
        product = self.data_manager.find_product_by_qr(qr_data)
        
        if product is not None:
            dialog = ctk.CTkInputDialog(
                text=f"Product: {product['name']}\nPrice: {product['price']}\nEnter Quantity:", 
                title="Add to Cart"
            )
            qty_str = dialog.get_input()
            
            if qty_str and qty_str.isdigit() and int(qty_str) > 0:
                qty = int(qty_str)
                self._add_to_cart(product, qty)
                self.lbl_status.configure(text=f"Added {qty} x {product['name']}", text_color="green")
            else:
                self.lbl_status.configure(text="Scan Cancelled / Invalid", text_color="yellow")
        else:
            self.lbl_status.configure(text="Product Not Found", text_color="red")
            
        self.last_scan_time = time.time()
        self.scanning_active = True
        self._update_camera_loop()

    def _add_to_cart(self, product, qty):
        """
        @brief add item into card

        @param product with dictionary datatype
        @param qty quantity to add 
        """
        subtotal = product['price'] * qty
        self.cart.append({
            "product_name": product['name'],
            "price": product['price'],
            "qty": qty,
            "total": subtotal,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self._refresh_cart_ui()

    def _refresh_cart_ui(self):
        """
        @brief refresh the cart UI and total label
        """
        for i in self.tree_cart.get_children(): self.tree_cart.delete(i)
        grand_total = 0
        for item in self.cart:
            self.tree_cart.insert("", "end", values=(item["product_name"], item["price"], item["qty"], item["total"]))
            grand_total += item["total"]
        self.lbl_total.configure(text=f"Total: Rp{grand_total:.2f}")

    def clear_cart(self):
        """
        @brief clear the current cart contents and update the UI
        """
        self.cart = []
        self._refresh_cart_ui()

    def checkout(self):
        """
        @brief send all of product in cart to transaction record
        """
        if not self.cart:
            messagebox.showinfo("Empty", "Cart is empty!")
            return
        total = self.data_manager.record_transaction(self.cart)
        messagebox.showinfo("Success", f"Checkout Complete!\nPrice: Rp{total:.2f}")
        self.clear_cart()