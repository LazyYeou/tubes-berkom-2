'''
@brief: implement segment tree data structure to store products
'''

class product_node:
    def __init__(self, name, val):
        self.name = name
        self.minVal = val
        self.maxVal = val
        self.sumVal = val

    def set_val(self, name, val):
        self.name = name
        self.minVal = val
        self.maxVal = val
        self.sumVal = val
    
class SegmentTree:
    def __init__(self, size):
        self.size = size
        self.tree = [product_node("", 0) for i in range(4 * size)]

    def merge(self, node):
        left_child = self.tree[2 * node]
        right_child = self.tree[2 * node + 1]
        
        self.tree[node].sumVal = left_child.sumVal + right_child.sumVal
        self.tree[node].minVal = min(left_child.minVal, right_child.minVal)
        self.tree[node].maxVal = max(left_child.maxVal, right_child.maxVal)

    def update(self, node, left, right, idx, price, name):
        """
        Updates a speicific product id with new price and name.
        """
        if left == right:
            # Leaf node reached
            self.tree[node].set_val(name, price)
            return

        mid = (left + right) // 2
        if idx <= mid:
            self.update(2 * node, left, mid, idx, price, name)
        else:
            self.update(2 * node + 1, mid + 1, right, idx, price, name)
        
        self.merge(node)

    def update_value(self, idx, price, name="Product"):
        self.update(1, 0, self.size - 1, idx, price, name)

    def get_total_sum(self, node, left, right, l_range, r_range):
        if(r_range < left or right < l_range):
            return 0
        if(l_range <= left and r_range >= right):
            return self.tree[node].sumVal
        
        mid = (left + right)//2
        return self.get_total_sum(node * 2, left, mid, l_range, r_range) + self.get_total_sum(node * 2 + 1, mid+1, right, l_range, r_range)
        
    def add(self, node, left, right, val):
        if left == right:
            if self.tree[node].minVal <= val.minVal:
                self.tree[2 * node] = self.tree[node]
                self.tree[2 * node + 1] = val
            else :
                self.tree[2 * node] = val
                self.tree[2 * node + 1] = self.tree[node]
        else:
            if self.tree[node].minVal > val.minval or self.tree[node].maxVal < val.minval:
                return
            mid = (left + right)/2
            self.add(node * 2, left, mid, val)
            self.add(node * 2 + 1, mid + 1, right, val)
        self.tree[node].minVal = min(self.tree[2 * node].minVal, self.tree[2 * node + 1].minVal)
        self.tree[node].maxVal = max(self.tree[2 * node].maxVal, self.tree[2 * node + 1].maxVal)
        self.tree[node].sumVal = self.tree[2 * node].sumVal + self.tree[2 * node + 1].sumVal

    def min_range_query(self, node, left, right, l_range, r_range):
        if(r_range < left or right < l_range):
            return 0
        if(l_range <= left and r_range >= right):
            return self.tree[node].minVal
        mid = (left + right)//2
        return min(self.min_range_query(node * 2, left, mid, l_range, r_range), self.min_range_query(node * 2 + 1, mid + 1, right, l_range, r_range))
        
    def max_range_query(self, node, left, right, l_range, r_range):
        if(r_range < left or right < l_range):
            return 0
        if(l_range <= left and r_range >= right):
            return self.tree[node].minVal
        mid = (left + right)//2
        return max(self.max_range_query(node * 2, left, mid, l_range, r_range), self.max_range_query(node * 2 + 1, mid + 1, right, l_range, r_range))
    
    def get_stats(self):
        total = self.get_total_sum(1, 0, self.size - 1, 0, self.size - 1)
        min_val = self.min_range_query(1, 0, self.size - 1, 0, self.size - 1)
        max_val = self.max_range_query(1, 0, self.size - 1, 0, self.size - 1)
        
        if min_val == float('inf'): min_val = 0
        if max_val == float('-inf'): max_val = 0
        
        return total, min_val, max_val
