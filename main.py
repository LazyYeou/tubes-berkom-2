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

'''
@doxigen
'''

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class CashierApp(ctk.CTk):
    """_summary_

    Args:
        ctk (_type_): _description_
    """    
    def __init__(self):
        super().__init__()

        self.title("CASHIER APP")
        self.geometry("1280x720")

        self.productFile = "products.csv"
        self.salesHistoryFile = "sales_history.csv"
        self.cart = []

    def sideBar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=10)
        self.sidebar.grid(row=5, column=5, sticky="nsew")

if __name__ == "__main__":
    app = CashierApp()
    app.mainloop()