"""
@file analytics_ui.py
@brief analytic UI based on sales_history data
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
import pandas as pd 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from datetime import datetime
import custom_function as cf 

class AnalyticsFrame(ctk.CTkFrame):
    def __init__(self, parent, data_manager):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.data_manager = data_manager
        
        self.view_mode = "Day" 
        
        #load data
        self.full_data_list = self.load_data_as_dicts() 
        self.current_data = self.full_data_list.copy()

        # print(self.full_data_list)
        
        self._setup_styles()
        self._create_layout()
        
        # set initial date 
        if self.full_data_list:
            # sort by time stamp
            sorted_data = cf.new_sort(self.full_data_list, key=lambda x: x['timestamp'])
            min_date = sorted_data[0]['timestamp'].strftime('%Y-%m-%d')
            max_date = sorted_data[-1]['timestamp'].strftime('%Y-%m-%d')
            self.entry_start.insert(0, min_date)
            self.entry_end.insert(0, max_date)
            
        self.refresh_dashboard()

    def load_data_as_dicts(self):
        """
        load csv and converts immediately to a list of dictionaries.
        """
        filename = 'sales_history.csv'
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.to_pydatetime()
            return df.to_dict('records')
        return []

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Analytics.Treeview", rowheight=30, borderwidth=0, font=("Segoe UI", 11))
        style.configure("Analytics.Treeview.Heading", relief="flat", font=("Segoe UI", 11, "bold"))

    def _create_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1) 

        #header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="Sales Analytics", font=("Segoe UI", 24, "bold")).pack(side="left", padx=(0, 20))
        
        #filter
        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.pack(side="left")
        
        ctk.CTkLabel(filter_frame, text="From:").pack(side="left", padx=5)
        self.entry_start = ctk.CTkEntry(filter_frame, width=100, placeholder_text="YYYY-MM-DD")
        self.entry_start.pack(side="left", padx=5)
        
        ctk.CTkLabel(filter_frame, text="To:").pack(side="left", padx=5)
        self.entry_end = ctk.CTkEntry(filter_frame, width=100, placeholder_text="YYYY-MM-DD")
        self.entry_end.pack(side="left", padx=5)

        ctk.CTkButton(header_frame, text="Apply Filter", width=80, command=self.refresh_dashboard).pack(side="right", padx=10)

        #stat card
        self.stat_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stat_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        self.stat_frame.columnconfigure((0, 1, 2), weight=1)

        self.card_revenue = self.create_stat_card(self.stat_frame, "Total Revenue", "Rp 0", 0)
        self.card_orders = self.create_stat_card(self.stat_frame, "Total Transactions", "0", 1)
        self.card_top = self.create_stat_card(self.stat_frame, "Top Category", "-", 2)

        #chart
        charts_container = ctk.CTkFrame(self, fg_color="transparent")
        charts_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        charts_container.columnconfigure(0, weight=1) 
        charts_container.columnconfigure(1, weight=1) 
        charts_container.rowconfigure(0, weight=1)

        self.chart_frame_hist = ctk.CTkFrame(charts_container)
        self.chart_frame_hist.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.chart_frame_cat = ctk.CTkFrame(charts_container)
        self.chart_frame_cat.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        #table
        table_container = ctk.CTkFrame(self)
        table_container.grid(row=3, column=0, sticky="nsew", padx=20, pady=(10, 20))
        
        ctk.CTkLabel(table_container, text="Detailed Breakdown", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=10)

        self.tree = ttk.Treeview(table_container, columns=("Revenue", "Qty"), show="tree headings", style="Analytics.Treeview")
        self.tree.heading("#0", text="Category / Product", anchor="w")
        self.tree.heading("Revenue", text="Revenue", anchor="e")
        self.tree.heading("Qty", text="Quantity Sold", anchor="center")
        self.tree.column("#0", width=300)
        self.tree.column("Revenue", width=150, anchor="e")
        self.tree.column("Qty", width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def create_stat_card(self, parent, title, value, col_idx):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=col_idx, sticky="ew", padx=5)
        ctk.CTkLabel(frame, text=title, font=("Segoe UI", 12)).pack(anchor="w", padx=15, pady=(15, 0))
        value_label = ctk.CTkLabel(frame, text=value, font=("Segoe UI", 20, "bold"))
        value_label.pack(anchor="w", padx=15, pady=(0, 15))
        return value_label

    def on_time_change(self, value):
        self.view_mode = value
        self.refresh_dashboard()

    def refresh_dashboard(self):
        # filter
        start_str = self.entry_start.get()
        end_str = self.entry_end.get()
        
        self.current_data = cf.filter_data_by_date(self.full_data_list, start_str, end_str)

        if not self.current_data:
            self.card_revenue.configure(text="Rp 0")
            self.card_orders.configure(text="0 Items")
            self.card_top.configure(text="-")
            self._clear_charts()
            self._clear_tree()
            return

        #calculate stat
        prod_map = {row['name']: row['category'] for _, row in self.data_manager.df_products.iterrows()}
        
        total_rev, total_qty, top_cat = cf.get_stats(self.current_data, prod_map)
        
        self.card_revenue.configure(text=f"Rp {total_rev:,.0f}")
        self.card_orders.configure(text=f"{total_qty} Items")
        self.card_top.configure(text=top_cat)

        #update chart
        self._plot_revenue_history()
        self._update_treeview()

    def _clear_charts(self):
        for widget in self.chart_frame_hist.winfo_children(): widget.destroy()
        
    def _clear_tree(self):
        for item in self.tree.get_children(): self.tree.delete(item)

    def _plot_revenue_history(self):
        self._clear_charts()

        dates, revenues = cf.group_by_time(self.current_data, self.view_mode)
        print(dates,revenues)

        #figure
        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')

        #adjust bar width
        width = 0.8 if self.view_mode == "Day" else 20

        #plot
        ax.bar(dates, revenues, color="#ff0000", alpha=0.8, width=width, label="Actual")

        #style
        ax.set_title(f"daily revenue", color="white", fontsize=10)
        ax.tick_params(axis='x', colors="white", rotation=45, labelsize=8)
        ax.tick_params(axis='y', colors="white", labelsize=8)

        #border
        for spine in ("bottom",):
            ax.spines[spine].set_color("white")
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)

        #spine
        ax.legend(
            loc="upper left",
            fontsize=8,
            facecolor='#2b2b2b',
            edgecolor='white',
            labelcolor='white'
        )

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame_hist)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)


    def _update_treeview(self):
        self._clear_tree()
        
        # get data hierachy
        # struc: {cat: {total_rev, total_qty, products: {prod: {rev, qty}}}}
        tree_data = cf.group_hierarchy(self.current_data)
        
        for cat_name, cat_data in tree_data.items():
            parent_id = self.tree.insert("", "end", text=cat_name, 
                                    values=(f"Rp {cat_data['total_rev']:,.0f}", cat_data['total_qty']), 
                                    open=False)
            
            for prod_name, prod_data in cat_data['products'].items():
                self.tree.insert(parent_id, "end", text=prod_name, 
                            values=(f"Rp {prod_data['rev']:,.0f}", prod_data['qty']))