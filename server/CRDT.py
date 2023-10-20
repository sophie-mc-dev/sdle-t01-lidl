class CRDTShoppingList: # represents a shopping list that contains multiple items

    def __init__(self, unique_id): 
        self.unique_id = unique_id # unique identifier for the shopping list (URL format)
        self.items = []  # a list to store ShoppingListItem objects

    # add item to list
    def add_item(self, item_name, quantity=1):
        # Check if the item with the same name already exists in the list
        for i, (existing_item, existing_quantity) in enumerate(self.items):
            if existing_item == item_name:
                # Increase the quantity of the existing item
                self.items[i] = (existing_item, existing_quantity + quantity)
                return

        # If the item doesn't exist, add it to the list with the specified quantity
        if quantity < 1:
            raise ValueError("Quantity must be a positive integer.")
        self.items.append((item_name, quantity))

    # remove item from list
    def remove_item(self, item_name, quantity):
        if quantity < 1:
            raise ValueError("Quantity must be a positive integer.")
        
        updated_items = []
        for item, existing_quantity in self.items:
            if item == item_name:
                remaining_quantity = existing_quantity - quantity
                if remaining_quantity > 0:
                    updated_items.append((item, remaining_quantity))
            else:
                updated_items.append((item, existing_quantity))
        
        self.items = updated_items

    # merge items
    def merge(self, other):
        self.items = self.data.union(other.items)

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