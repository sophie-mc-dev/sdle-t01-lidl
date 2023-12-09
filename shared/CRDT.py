import uuid
from .pncounter import PNCounter
from .utils import *
from secrets import token_urlsafe
import random

class ShoppingList:
    def __init__(self):
        self.id = token_urlsafe(16)

        self.v = {self.id: 0} # vector clock to track the causal ordering of operations

        self.shopping_map = {} # key, value: itemID, item attributes (id, name, quantity, acquired, timestamp)
        self.Users = set()

        self.quantity_counters = {}
        self.acquired_counters = {}

    def my_id(self):
        """Returns the ID of the shopping list."""
        return self.id

    def is_empty(self):
        """Returns True if shopping list is empty, or False otherwise"""
        return self.shopping_map == {}

    def delete_list(self, id):
        """Deletes the shopping list identified by the provided list_id."""
        if id == self.id:
            # Clear all the attributes related to the shopping list
            self.name = ""
            self.shopping_map = {}
            self.Users = set()
            self.quantity_counters = {}
            self.acquired_counters = {}
            self.v = {}
            print(f"Shopping list with ID '{id}' has been deleted.")
        else:
            print("Invalid list ID. Deletion failed.")

    def associate_user(self, user_id):
        """
        Associate a user with the shopping list.
        Adds user id to shopping list's Users set
        """
        self.Users.add(user_id)


    def my_id(self):
        """Returns the ID of the shopping list."""
        return self.id
    
    def contains(self, item_id):
        """Checks if the item is present in the shopping list."""
        return item_id in self.shopping_map
    
    def get_shopping_list(self, id=None):
        """Returns the shopping list's name, ID, and items."""
        if id is None or id != self.id:
            raise ValueError("Invalid Shopping List ID or no ID provided.")

        shopping_list_info = {
            "list_id": self.id,
            "items": self.shopping_map
        }
        return shopping_list_info

    # add_item but with concrete values from acquired and timestamp
    def fill_with_item(self, item_id, item):
        # Add item to the shopping map
        item_id = str(uuid.uuid4()) 
        self.shopping_map[item_id] = {
            "name": item["name"],
            "quantity": item["quantity"],
            "acquired": item["acquired"],
            "timestamp": item["timestamp"]
        }

        self.quantity_counters[item_id] = PNCounter(item_id) 
        self.acquired_counters[item_id] = PNCounter(item_id)

    def add_item(self, item_id, item):
        """
        Adds an item to the shopping list.

        Parameters:
        - item_id: Item ID
        - item: Dictionary containing item attributes
        """
        list_id = self.id
        if list_id not in self.v: 
            self.v[list_id] = 0

        # Generate the vector clock timestamp for the item
        self.v[list_id] += 1
        item['timestamp'] = self.v[list_id]

        # Add item to the shopping map
        self.shopping_map[item_id] = {
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
        if item_id not in self.shopping_map:
            raise ValueError("Item ID does not exist in the shopping list.")
        
        if item_id in self.shopping_map:
            del self.shopping_map[item_id]
            del self.quantity_counters[item_id]
            del self.acquired_counters[item_id]

    def increment_quantity(self, item_id):
        """
        Increments the quantity of the shopping list item
        """
        if item_id in self.shopping_map:
            list_id = self.my_id()
            if list_id not in self.v:
                self.v[list_id] = 0

            # Generate the vector clock timestamp for the increment operation
            self.v[list_id] += 1

            updated_quantity = int(self.shopping_map[item_id]["quantity"]) + 1
            self.shopping_map[item_id]["quantity"] = updated_quantity
            self.shopping_map[item_id]["timestamp"] = self.v[list_id]

            self.quantity_counters[item_id].inc(item_id)

    def decrement_quantity(self, item_id):
        """
        Decrements the quantity of the shopping list item
        """
        if item_id in self.shopping_map and self.shopping_map[item_id]["quantity"] > 0:
            list_id = self.my_id()
            if list_id not in self.v:
                self.v[list_id] = 0

            # Generate the vector clock timestamp for the decrement operation
            self.v[list_id] += 1

            updated_quantity = int(self.shopping_map[item_id]["quantity"]) - 1
            self.shopping_map[item_id]["quantity"] = updated_quantity 
            self.shopping_map[item_id]["timestamp"] = self.v[list_id]

            self.quantity_counters[item_id].dec(item_id)

    def update_acquired_status(self, item_id, status):
        """
        Sets the item as acquired or not acquired
        """
        if item_id in self.shopping_map:
            list_id = self.my_id()
            if list_id not in self.v:
                self.v[list_id] = 0

            # Update the status of the item
            self.v[list_id] += 1
            self.shopping_map[item_id]["acquired"] = status
            self.shopping_map[item_id]["timestamp"] = self.v[list_id]

            # Update the acquired_counters with PN Counters
            if item_id in self.acquired_counters:
                self.acquired_counters[item_id].inc(list_id) if status else self.acquired_counters[item_id].dec(list_id)

    def merge(self, replica):

        # Extract item names from the current instance and the replica
        self_items_names = {item['name']: item for item in self.shopping_map.values()}
        replica_items_names = {item['name']: item for item in replica.shopping_map.values()}

        # Handle conflicts based on timestamps, quantities and acquired status
        for item_name in replica_items_names:
            for item_id, item in self.shopping_map.items():
                if (item_name == item['name']):
                    self_id = item_id
                    self_item = item

            for item_id, item in replica.shopping_map.items():
                if (item_name == item['name']):
                    replica_id = item_id
                    replica_item = item

            # IF REPLICA'S MODIFICATION IS MORE RECENT
            if int(replica_item["timestamp"]) > int(self_item["timestamp"]):

                # Check for conflicts in acquired status
                if replica_item["acquired"] != self_item["acquired"]:
                    self.shopping_map[self_id]["acquired"] = replica.shopping_map[replica_id]["acquired"]
                    self.shopping_map[self_id]["timestamp"] = replica.shopping_map[replica_id]["timestamp"]
                
                # Check for conflicts in quantities
                if replica_item["quantity"] != self_item["quantity"]:
                    # Handle quantity conflict
                    self.shopping_map[self_id]["quantity"] = int(replica.shopping_map[replica_id]["quantity"])
                    self.shopping_map[self_id]["timestamp"] = replica.shopping_map[replica_id]["timestamp"]
                
                # No conflicts in quantity or acquired status, update with the latest timestamp
                else:
                    self.shopping_map[self_id] = replica_item

            # IF TIMESTAMPS ARE THE SAME
            if int(replica_item["timestamp"]) == int(self_item["timestamp"]):

                chosen_replica = random.choice([self_item, replica_item])

                # Check for conflicts in acquired status
                if replica_item["acquired"] != self_item["acquired"]:
                    self.shopping_map[self_id]["acquired"] = chosen_replica["acquired"]
                    self.shopping_map[self_id]["timestamp"] = chosen_replica["timestamp"]
                
                # Check for conflicts in quantities
                if replica_item["quantity"] != self_item["quantity"]:
                    # Handle quantity conflict
                    self.shopping_map[self_id]["quantity"] = int(chosen_replica["quantity"])
                    self.shopping_map[self_id]["timestamp"] = chosen_replica["timestamp"]
                
                # No conflicts in quantity or acquired status, update with the latest timestamp
                else:
                    self.shopping_map[self_id] = chosen_replica
            
        # Merge items from replica into self.shopping_map
        for item_name in replica_items_names:
            if item_name not in self_items_names:

                for item_id, item in replica.shopping_map.items():
                    if (item_name == item['name']):
                        replica_item = item
                        replica_id = item_id

                self.shopping_map[replica_id] = replica.shopping_map[replica_id]

        # Merge quantity counters and acquired counters            
        for item_id in replica.quantity_counters:
            if item_id not in self.quantity_counters:
                self.quantity_counters[item_id] = PNCounter(item_id)
            self.quantity_counters[item_id].merge(replica.quantity_counters[item_id])

        for item_id in replica.acquired_counters:
            if item_id not in self.acquired_counters:
                self.acquired_counters[item_id] = PNCounter(item_id)
            self.acquired_counters[item_id].merge(replica.acquired_counters[item_id])

        return self