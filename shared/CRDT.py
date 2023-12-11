import uuid
from .pncounter import PNCounter
from secrets import token_urlsafe
import random

class ShoppingList:
    def __init__(self):
        self.id = 0 # =token_urlsafe(16)
        self.replica_id = 0

        self.v = {} # vector clock to track the causal ordering of operations

        self.shopping_map = {} # key, value: itemID, item attributes (id, name, quantity, acquired, timestamp)
        self.Users = set()

        self.quantity_counters = {}
        self.acquired_counters = {}
    
    def set_vector_clock(self, dict):
        self.v = dict

    def get_vector_clock(self):
        return self.v

    def set_replica_id(self, replica_id):
        self.replica_id = replica_id
    
    def my_replica_id(self):
        """Returns the ID of the shopping list."""
        return self.replica_id
    
    def set_id(self, id):
        self.id = id

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
        # item_id = str(uuid.uuid4()) 
        quantity_counter = PNCounter(self.replica_id,item_id)
        acquired_counter = PNCounter(self.replica_id,item_id)
        quantity_counter.add_new_node(item_id)
        acquired_counter.add_new_node(item_id)
        quantity_counter.inc(item_id, int(item["quantity"]))
        if item["acquired"]:
            acquired_counter.inc(item_id)
        
        self.shopping_map[item_id] = {
            "name": item["name"],
            "quantity": item["quantity"],
            "acquired": item["acquired"],
            "timestamp": item["timestamp"]
        }

        self.quantity_counters[item_id] = quantity_counter
        self.acquired_counters[item_id] = acquired_counter
        self.v[self.replica_id] = int(item["timestamp"])

        # self.quantity_counters[item_id] = PNCounter(item_id) 
        # self.acquired_counters[item_id] = PNCounter(item_id)

    def add_item(self, item_id, item):
        """
        Adds an item to the shopping list.

        Parameters:
        - item_id: Item ID
        - item: Dictionary containing item attributes
        """
        """
        list_id = self.id
        if list_id not in self.v: 
            self.v[list_id] = 0

        # Generate the vector clock timestamp for the item
        self.v[list_id] += 1
        item['timestamp'] = self.v[list_id]
        """
        timestamp = self.increment_counter()
        quantity_counter = PNCounter(self.replica_id,item_id)
        acquired_counter = PNCounter(self.replica_id,item_id)
        quantity_counter.add_new_node(item_id)
        acquired_counter.add_new_node(item_id)
        quantity_counter.inc(item_id, item["quantity"])

        self.quantity_counters[item_id] = quantity_counter
        self.acquired_counters[item_id] = acquired_counter

        item_name = item['name']
        existing_items = [existing_item for existing_item in self.shopping_map.values() if existing_item["name"] == item_name]

        if existing_items:
            print(f"Warning! An item with the name '{item_name}' already exists in this shopping list.")

        print(quantity_counter.query())

        # Add item to the shopping map
        self.shopping_map[item_id] = {
            "name": item["name"],
            "quantity": quantity_counter.query(),
            "acquired": acquired_counter.query(),
            "timestamp": timestamp   # ver este timestamp
        }

        # self.quantity_counters[item_id] = PNCounter(item_id) 
        # self.acquired_counters[item_id] = PNCounter(item_id)  

        return timestamp

    def remove_item(self, item_name):
        """
        Removes an item of the shopping list.

        Parameters:
        - item_name: Name of item to remove
        """
        item_id = self.get_item_id_by_name(item_name)
        if item_id not in self.shopping_map:
            raise ValueError("Item ID does not exist in the shopping list.")
        
        if item_id in self.shopping_map:
            timestamp = self.increment_counter()
            del self.shopping_map[item_id]
            del self.quantity_counters[item_id]
            del self.acquired_counters[item_id]

        return timestamp

    def increment_counter(self):
        if self.replica_id not in self.v:
            self.v[self.replica_id] = 1
        else:
            self.v[self.replica_id] += 1
        return self.v[self.replica_id]

    def get_item_id_by_name(self, item_name):
        """
        Returns the item ID of the item with the provided name.
        """
        for item_id, item in self.shopping_map.items():
            if item["name"] == item_name:
                return item_id
        return None
        
    def get_quantity_counter(self, item_id):
        """
        Returns the quantity counter of the item with the provided ID.
        """
        return self.quantity_counters[item_id]

    def increment_quantity(self, item_id):
        """
        Increments the quantity of the shopping list item
        """

        """
        if item_id in self.shopping_map:
            list_id = self.my_id()
            if list_id not in self.v:
                self.v[list_id] = 0

        """
        print(self.shopping_map.keys())
        if item_id in self.shopping_map:

            # Generate the vector clock timestamp for the increment operation
            timestamp = self.increment_counter()
            quantity_counter = self.quantity_counters[item_id]
            quantity_counter.inc(item_id, 1)
            # self.v[self.replica_id] += 1

            # updated_quantity = int(self.shopping_map[item_id]["quantity"]) + 1

            self.shopping_map[item_id]["quantity"] = quantity_counter.query()
            self.shopping_map[item_id]["timestamp"] = timestamp

            print("Increment quantity")
            # print(self.shopping_map[item_id]["quantity"].query())
            print(self.shopping_map[item_id]["timestamp"])

            # self.quantity_counters[item_id].inc(item_id)

            return timestamp


    def decrement_quantity(self, item_id):
        """
        Decrements the quantity of the shopping list item
        """
        """
        if item_id in self.shopping_map and self.shopping_map[item_id]["quantity"] > 0:
            list_id = self.my_id()
            if list_id not in self.v:
                self.v[list_id] = 0
        """
        print(self.quantity_counters.keys())
        print(self.quantity_counters.values())
        if item_id in self.shopping_map:
            print("heyyyy")
            if int(self.shopping_map[item_id]["quantity"]) <= 1:
                raise ValueError("Item quantity cannot be negative or zero.")
            else:
                # Generate the vector clock timestamp for the decrement operation
                timestamp = self.increment_counter()
                quantity_counter = self.quantity_counters[item_id]
                quantity_counter.dec(item_id)
                print("Decrement quantityyyyyyyyyyyyyyyyy")
                # self.v[self.replica_id] += 1

                # updated_quantity = int(self.shopping_map[item_id]["quantity"]) - 1
                self.shopping_map[item_id]["quantity"] = quantity_counter.query()
                self.shopping_map[item_id]["timestamp"] = timestamp

                # self.quantity_counters[item_id].dec(item_id)

                return timestamp
            """
            # Generate the vector clock timestamp for the decrement operation
            self.v[list_id] += 1

            updated_quantity = int(self.shopping_map[item_id]["quantity"]) - 1
            self.shopping_map[item_id]["quantity"] = updated_quantity 
            self.shopping_map[item_id]["timestamp"] = self.v[list_id]

            self.quantity_counters[item_id].dec(item_id)
            """

    def update_acquired_status(self, item_id, status):
        """
        Sets the item as acquired or not acquired
        """
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
        """

        if item_id in self.shopping_map:
            timestamp = self.increment_counter()
            acquired_counter = self.acquired_counters[item_id]
            if status:
                acquired_counter.inc(item_id)
                self.shopping_map[item_id]["acquired"] = acquired_counter.query()
            else:
                acquired_counter.dec(item_id)
                self.shopping_map[item_id]["acquired"] = acquired_counter.query()
            self.shopping_map[item_id]["timestamp"] = timestamp

            # self.acquired_counters[item_id].inc(item_id) if status else self.acquired_counters[item_id].dec(item_id)

            return timestamp

    def merge(self, replica):

        # Extract item names from the current instance and the replica
        self_items_names = {item['name']: item for item in self.shopping_map.values()}
        replica_items_names = {item['name']: item for item in replica.shopping_map.values()}

        local_v = self.v
        replica_v = replica.v
        print("replica_id:\n")
        print(replica.replica_id)
        local_timestamp = local_v[self.replica_id]
        replica_timestamp = replica_v[replica.replica_id]

        print("Local v: ", local_v)
        print("Replica v: ", replica_v)
        print(local_v.values())
        
        # Handle conflicts based on timestamps, quantities and acquired status
        for item_name in replica_items_names:
            is_self_defined = False
            for item_id, item in self.shopping_map.items():
                if (item_name == item['name']):
                    self_id = item_id
                    self_item = item
                    is_self_defined = True

            for item_id, item in replica.shopping_map.items():
                if (item_name == item['name']):
                    replica_id = item_id
                    replica_item = item

            if is_self_defined:
                # IF REPLICA'S MODIFICATION IS MORE RECENT
                if replica_timestamp > local_timestamp:

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
                if replica_timestamp == local_timestamp:

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
                    
                    # No conflicts in quantity or acquired status, update with random replica
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

        # Merge items from replica in case of item deletion
<<<<<<< Updated upstream
        '''
=======
>>>>>>> Stashed changes
        for item_name in self_items_names:
            if item_name not in replica_items_names:
                item_id = self.get_item_id_by_name(item_name)
                if item_id is not None:
<<<<<<< Updated upstream
                    del self.shopping_map[item_id] '''
=======
                    if replica_timestamp > local_timestamp:
                        del self.shopping_map[item_id]
>>>>>>> Stashed changes

        # Merge quantity counters and acquired counters            
        for item_id in replica.quantity_counters:
            if item_id not in self.quantity_counters:
                self.quantity_counters[item_id] = PNCounter(replica.replica_id, item_id)
            self.quantity_counters[item_id].merge(replica.quantity_counters[item_id])

        for item_id in replica.acquired_counters:
            if item_id not in self.acquired_counters:
                self.acquired_counters[item_id] = PNCounter(replica.replica_id,item_id)
            self.acquired_counters[item_id].merge(replica.acquired_counters[item_id])

        return self