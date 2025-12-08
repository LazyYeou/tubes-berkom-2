'''
@brief: implement segment tree data structure to store products
'''

class product_node:
    def __init__(self, name, val, category, qr):
        self.name = name
        self.price = val
        self.category = category
        self.qr_data = qr

    def setVal(self, name, val, category, qr):
        self.name = name
        self.price = val
        self.category = category
        self.qr_data = qr
    
class SegmentTree:
    def __init__(self, size, prod):
        self.size = size
        self.tree = [product_node("", 0, "", "") for i in range(4 * size)]
        self.build(1, 0, self.size-1, prod)

    def merge(self, node):
        left_child = self.tree[2 * node]
        right_child = self.tree[2 * node + 1]
        
        self.tree[node].price = left_child.price + right_child.price

    def update(self, node, left, right, idx, prod):
        """
        Updates a speicific product id with new price and name.
        """
        if left == right:
            # Leaf node reached
            self.tree[node] = prod
            return

        mid = (left + right) // 2
        if idx <= mid:
            self.update(2 * node, left, mid, idx, prod)
        else:
            self.update(2 * node + 1, mid + 1, right, idx, prod)
        
        self.merge(node)

    def update_value(self, idx, prod):
        self.update(1, 0, self.size - 1, idx, prod)

    def get_total_sum(self, node, left, right, l_range, r_range):
        if(r_range < left or right < l_range):
            return 0
        if(l_range <= left and r_range >= right):
            return self.tree[node].price
        
        mid = (left + right)//2
        return self.get_total_sum(node * 2, left, mid, l_range, r_range) + self.get_total_sum(node * 2 + 1, mid+1, right, l_range, r_range)
        
    def build(self, node, left, right, prod):
        if(left == right):
            self.tree[node] = prod[left]
            return
        mid = (left + right)//2
        self.build(self, 2 * node, left, mid, prod)
        self.build(self, 2 * node + 1, mid + 1, right, prod)
        self.merge(node)
  

    
    def get_stats(self):
        total = self.get_total_sum(1, 0, self.size - 1, 0, self.size - 1)
        
        return total
