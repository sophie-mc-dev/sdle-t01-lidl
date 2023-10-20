class CRDTShoppingList:

    def __init__(self): 
        self.data = []  

    # add item to list
    def add_item(self, item):
        self.data.add(item)

    # remove item from list (modify in the future)
    def remove_item(self, item):
        self.data.remove(item)

    # merge items
    def merge(self, other):
        self.data = self.data.union(other.data)

    # display shopping list
    def get_list(self):
        return self.data
    
'''
Expected output/example:

sl_replica1 = CRDTShoppingList()
sl_replica2 = CRDTShoppingList()

sl_replica1.add_item("Apples")
sl_replica1.add_item("Bananas")
sl_replica1.get_list()
    returns: ["Apples", "Bananas"]

sl_replica2.add_item("Bananas")
sl_replica2.add_item("Peaches")
sl_replica1.get_list()
    returns: ["Bananas", "Peaches"]

sl_replica1.merge(sl_replica2)
sl_replica1.get_list()
    returns: ["Apples", "Bananas", "Peaches"]

sl_replica2.merge(sl_replica1)
sl_replica2.get_list()
    returns: ["Apples", "Bananas", "Peaches"]
'''