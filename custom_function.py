class CustomFunction:
    def new_sum(x):
        total = 0
        for i in x:
            total += i
        return total
    
    def new_min(x):
        min = x[0]
        for i in x:
            if i < min:
                min = i
        return min
    
    