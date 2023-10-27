class CRDTShoppingList: 

    def __init__(self, unique_id): 
        self.unique_id = unique_id 
        self.items = []  

    # add item to list
    def add_item(self, item_name, quantity, acquired):
        # initialize
        quantity = 1
        acquired = False

        # Check if the item with the same name already exists in the list
        for i, (existing_item, existing_quantity) in enumerate(self.items):
            if existing_item == item_name:
                # Increase the quantity of the existing item
                self.items[i] = (existing_item, existing_quantity + quantity)
                return

        # If the item doesn't exist, add it to the list with the specified quantity
        if quantity < 1:
            raise ValueError("Quantity must be a positive integer.")
        self.items.append({'name': item_name, 'quantity': quantity, 'acquired': acquired})

    # remove item from list
    def remove_item(self, item_name):
        self.items = [item for item in self.items if item != item_name]

    def increase_quantity(self, item_name, quantity=1):
        for i, (existing_item, existing_quantity) in enumerate(self.items):
            if existing_item == item_name:
                self.items[i] = (existing_item, existing_quantity + quantity)
                return
            
    def decrease_quantity(self, item_name, quantity=1):
        for i, (existing_item, existing_quantity) in enumerate(self.items):
            if existing_item == item_name:
                remaining_quantity = existing_quantity - quantity
                if remaining_quantity >= 1:
                    self.items[i] = (existing_item, remaining_quantity)
                else:
                    self.remove_item(item_name)

    # add function that marks item as acquired
    def acquire_item(self, item_name):
        for i, (existing_item, existing_quantity) in enumerate(self.items):
            if existing_item == item_name:
                self.items[i] = (existing_item, existing_quantity, True)

    # merge items
    def merge(self, other):
        self.items = self.data.union(other.items)

    # implement a conflict resolution strategy

    # display shopping list
    def get_list(self):
        return self.items
    
'''
Similar example of expected result:

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