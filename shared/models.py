import uuid

class ShoppingListItem: # represents an item in a shopping list
    def __init__(self, name, quantity, acquired=False):
        self.id = str(uuid.uuid4())
        self.name = name
        self.quantity = quantity
        self.acquired = acquired # whether the item is acquired or not

    def __str__(self):
        # string representation of the item for printing purposes
        return f"Item ID: {self.id}, Name: {self.name}, Quantity: {self.quantity}, Acquired: {self.acquired}"


class ShoppingList: # represents a shopping list that contains multiple items
    def __init__(self, list_id):
        self.list_id = list_id  # unique identifier for the shopping list
        self.items = []         # a list to store ShoppingListItem objects

    def add_item(self, name, quantity, acquired):
        item = ShoppingListItem(name, quantity, acquired)
        self.items.append(item)

    def delete_item(self, item_id):
        self.items = [item for item in self.items if item.id != item_id]