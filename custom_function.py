"""
@file custom_function.py
@brief module for custom function
"""
from datetime import datetime, timedelta
import math

def parse_date(date_str):
    """@brief parse YYYY-MM-DD string to datetime obj"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None

def filter_data_by_date(data, start_str, end_str):
    """
    @brief filter a list of dictionaries based on a date range
    @param:
        data (list[dict]): dataset
        start_str (str): start date 
        end_str (str): end date 
    """
    # set start and end date
    start_date = parse_date(start_str) if start_str else datetime.min
    end_date = parse_date(end_str) + timedelta(days=1) if end_str else datetime.max

    print([row for row in data if (start_date <= row['timestamp'] and row['timestamp'] <= end_date)])
    return [row for row in data if (start_date <= row['timestamp'] and row['timestamp'] <= end_date)]

def get_stats(data, product_map):
    """Calculates total revenue, quantity, and top category."""
    if not data:
        return 0, 0, "-"

    total_revenue = 0
    total_qty = 0
    cat_counts = {}

    for row in data:
        total_revenue += row['total']
        total_qty += row['qty']
        
        # Determine category
        prod_name = row['product_name']
        cat = product_map.get(prod_name, "Uncategorized")
        row['category'] = cat 
        
        cat_counts[cat] = cat_counts.get(cat, 0) + row['total']

    #top cat by revenue
    top_cat = new_max(cat_counts, key=cat_counts.get)
    
    return total_revenue, total_qty, top_cat

def group_by_time(data, mode="Day"):
    """
    Aggregates revenue by Day or Month.
    Returns: Tuple (sorted_dates, revenues)
    """
    grouped = {}
    
    for row in data:
        ts = row['timestamp']
        if mode == "Day":
            key = ts.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # First day of the month
            key = ts.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
        grouped[key] = grouped.get(key, 0) + row['total']

    # Sort by date
    sorted_keys = sorted(grouped.keys())
    values = [grouped[k] for k in sorted_keys]
    
    return sorted_keys, values


def group_hierarchy(data):
    """
    Groups data by Category -> Product for the Treeview.
    Structure: { 'Category': { 'Product': {'rev': 0, 'qty': 0} } }
    """
    tree_data = {}
    
    for row in data:
        cat = row.get('category', 'Uncategorized')
        prod = row['product_name']
        rev = row['total']
        qty = row['qty']
        
        if cat not in tree_data:
            tree_data[cat] = {'total_rev': 0, 'total_qty': 0, 'products': {}}
            
        # Update Category Totals
        tree_data[cat]['total_rev'] += rev
        tree_data[cat]['total_qty'] += qty
        
        # Update Product Totals
        if prod not in tree_data[cat]['products']:
            tree_data[cat]['products'][prod] = {'rev': 0, 'qty': 0}
            
        tree_data[cat]['products'][prod]['rev'] += rev
        tree_data[cat]['products'][prod]['qty'] += qty
        
    return tree_data

def new_sort(iterable, *, key=None):
    result = list(iterable)

    if key is None:
        def key(x): return x
    
    n = len(result)
    for i in range(n):
        for j in range(0, n - i - 1):
            if (key(result[j]) > key(result[j+1])):
                result[j], result[j+1] = result[j+1], result[j]
    return result

def new_max(iterable, key=None):
    iterator = iter(iterable)

    best = next(iterator)

    if key is None:
        key = lambda x: x

    best_key = key(best)

    for item in iterator:
        k = key(item)
        if k > best_key:
            best = item
            best_key = k

    return best