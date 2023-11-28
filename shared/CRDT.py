import uuid
from .pncounter import PNCounter
from .utils import *
from secrets import token_urlsafe


class ShoppingList:
    def __init__(self):
        self.name = ""
        self.id = token_urlsafe(16)

        self.v = {self.id: 0} # vector clock to track the causal ordering of operations

        self.Items = {} # key, value: itemID, item attributes (id, name, quantity, acquired, timestamp)
        self.Users = {}

        self.quantity_counters = {}
        self.acquired_counters = {}

    def associate_user(self, username):
        """
        Associate a user with the shopping list.
        """
        self.Users.add(username)

    def my_id(self):
        """Returns the ID of the shopping list."""
        return self.id
    
    def contains(self, item_id):
        """Checks if the item is present in the shopping list."""
        return item_id in self.Items
    
    def get_shopping_list(self, id=None):
        """
        Returns the shopping list's name, ID, and items.
        """
        if id is None or id != self.id:
            print("Invalid Shopping List ID or no ID provided.")
            return None

        shopping_list_info = {
            "name": self.name,
            "id": self.id,
            "items": self.Items
        }
        return shopping_list_info

    def add_item(self, item_id, item):
        """
        Adds an item to the shopping list.

        Parameters:
        - item_id: Item ID
        - item: Dictionary containing item attributes
        """
        list_id = self.my_id()
        if list_id not in self.v: 
            self.v[list_id] = 0

        # Generate the vector clock timestamp for the item
        self.v[list_id] += 1
        item['timestamp'] = self.v[list_id]

        # Add item to the shopping map
        item_id = str(uuid.uuid4()) 
        self.Items[item_id] = {
            "name": item["name"],
            "quantity": item["quantity"],
            "acquired": False,
            "timestamp": item["timestamp"]
        }

        self.quantity_counters[item_id] = PNCounter(item_id) 
        self.acquired_counters[item_id] = PNCounter(item_id)  

    def remove_item(self, item_id):
        """
        Removes an item of the shopping list.

        Parameters:
        - item_id: Item ID
        """
        if item_id in self.Items:
            del self.Items[item_id]
            del self.quantity_counters[item_id]
            del self.acquired_counters[item_id]

    def update_quantity(self, item_id, new_quantity):
        """
        Update the quantity of an item in the shopping list.
        """
        if item_id in self.Items:
            current_quantity = self.Items[item_id]["quantity"]

            # Adjust quantity using the PNCounter
            diff = new_quantity - current_quantity
            if diff > 0:
                self.quantity_counters[item_id].inc(diff)  # Increase the quantity
            elif diff < 0:
                self.quantity_counters[item_id].dec(abs(diff))  # Decrease the quantity

            self.Items[item_id]["quantity"] = new_quantity

    def increment_quantity(self, item_id):
        """
        Increments the quantity of the shopping list item
        """
        if item_id in self.Items:
            list_id = self.my_id()
            if list_id not in self.v:
                self.v[list_id] = 0

            # Generate the vector clock timestamp for the increment operation
            self.v[list_id] += 1
            self.Items[item_id]["quantity"] += 1
            self.Items[item_id]["timestamp"] = self.v[list_id]

            self.quantity_counters[item_id].inc(item_id)

    def decrement_quantity(self, item_id):
        """
        Decrements the quantity of the shopping list item
        """
        if item_id in self.Items and self.Items[item_id]["quantity"] > 0:
            list_id = self.my_id()
            if list_id not in self.v:
                self.v[list_id] = 0

            # Generate the vector clock timestamp for the decrement operation
            self.v[list_id] += 1
            self.Items[item_id]["quantity"] -= 1
            self.Items[item_id]["timestamp"] = self.v[list_id]

            self.quantity_counters[item_id].dec(item_id)

    def update_acquired_status(self, item_id, status):
        """
        Sets the item as acquired or not acquired
        """
        if item_id in self.Items:
            list_id = self.my_id()
            if list_id not in self.v:
                self.v[list_id] = 0

            # Update the status of the item
            self.v[list_id] += 1
            self.Items[item_id]["acquired"] = status
            self.Items[item_id]["timestamp"] = self.v[list_id]

            # Update the acquired_counters with PN Counters
            if item_id in self.acquired_counters:
                self.acquired_counters[item_id].inc(list_id) if status else self.acquired_counters[item_id].dec(list_id)

    def merge(self, other_map):
        for item_id, other_item in other_map.shopping_map.items():
            if item_id in self.Items:
                current_item = self.Items[item_id]
                if other_item["timestamp"] > current_item["timestamp"]:
                    self.Items[item_id] = other_item  # Update with the latest timestamp
            else:
                self.Items[item_id] = other_item  # Add if the key doesn't exist in self.shopping_map

            if item_id in other_map.quantity_counters:
                if item_id not in self.quantity_counters:
                    self.quantity_counters[item_id] = PNCounter()
                self.quantity_counters[item_id].merge(other_map.quantity_counters[item_id])

            if item_id in other_map.acquired_counters:
                if item_id not in self.acquired_counters:
                    self.acquired_counters[item_id] = PNCounter()
                self.acquired_counters[item_id].merge(other_map.acquired_counters[item_id])