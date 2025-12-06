"""
@file data_manager.py
@brief handle data and integration between csv storage and segment tree.
"""

import pandas as pd
import os
from segment_tree import SegmentTree

class DataManager:
    """
    @class DataManager
    @brief controll csv data and the in memory segment tree.
    """

    def __init__(self, products_file="products.csv", history_file="sales_history.csv"):
        """
        @brief contructor
        @param products_file path to product inventory csv
        @param history_file path to sales sales history csv.
        """
        self.products_file = products_file
        self.history_file = history_file
        
        # init Segment Tree with capacity for 1000 items
        # self.seg_tree = SegmentTree(1000) 
        
        # load data and push it to segment tree
        self.df_products = self.load_products()
        self.df_history = self.load_history()
        # self.rebuild_segment_tree()

    def load_products(self):
        """
        @brief load product CSV.
        @return pd.DataFrame
        """
        if os.path.exists(self.products_file):
            return pd.read_csv(self.products_file)
        return pd.DataFrame(columns=["name", "price", "category", "qr_data"])

    def load_history(self):
        """
        @brief load history CSV.
        @return pd.DataFrame
        """
        if os.path.exists(self.history_file):
            return pd.read_csv(self.history_file)
        return pd.DataFrame(columns=["product_name", "price", "qty", "total", "timestamp"])

    # def rebuild_segment_tree(self):
    #     """
    #     @brief repopulates segmen tree based on current dataframe rows
    #     """
    #     self.seg_tree = SegmentTree(1000)
    #     for idx, row in self.df_products.iterrows():
    #         self.seg_tree.update_value(idx, row['price'], row['name'])

    def add_product(self, name, price, category, qr_data):
        """
        @brief add a new product to the DataFrame and updates segment tree
        @param name product name.
        @param price pdocut price.
        @param category product category.
        @param qr_data product qr_code string
        """
        new_row = {"name": name, "price": price, "category": category, "qr_data": qr_data}
        self.df_products = pd.concat([self.df_products, pd.DataFrame([new_row])], ignore_index=True)
        
        idx = len(self.df_products) - 1
        # self.seg_tree.update_value(idx, price, name)
        
        self.save_data()

    def delete_product_by_name(self, name):
        """
        @brief delete product by name and rebuilds the tree
        @param name name of product to delete
        """
        self.df_products = self.df_products[self.df_products['name'] != name]

        # self.rebuild_segment_tree() 
        self.save_data()

    def find_product_by_qr(self, qr_data):
        """
        @brief search a product by its QR string
        @param qr_data scanned string
        @return DataFrame Row or None
        """
        product = self.df_products[self.df_products['qr_data'] == qr_data]
        if not product.empty:
            return product.iloc[0]
        return None

    def record_transaction(self, cart_items):
        """
        @brief store a list of cart items to the history csv
        @param cart_items list of dictionaries representing the cart
        @return total revenue of the transaction
        """
        new_sales = pd.DataFrame(cart_items)
        self.df_history = pd.concat([self.df_history, new_sales], ignore_index=True)
        self.save_data()
        return sum(item['total'] for item in cart_items)

    def save_data(self):
        """
        @brief writes dataframe to csv
        """
        self.df_products.to_csv(self.products_file, index=False)
        self.df_history.to_csv(self.history_file, index=False)