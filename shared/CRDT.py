import uuid
import time


class AWORMap:
    def __init__(self):
        self.shopping_list_id = "1"
        self.shopping_map = {}

    def add_item(self, key, item):
        item["timestamp"] = time.time()
        self.shopping_map[key] = item

    def remove_item(self, key):
        if key in self.shopping_map:
            del self.shopping_map[key]

    def get_shopping_list(self, shopping_list_id=None):
        if shopping_list_id is None or shopping_list_id != self.shopping_list_id:
            print("Invalid Shopping List ID or no ID provided.")
            return None

        for key, item in self.shopping_map.items():
            print(f"Item ID: {key}, Item: {item}")
        return self.shopping_map

    def update_quantity(self, key, quantity):
        if key in self.shopping_map:
            self.shopping_map[key]["quantity"] = quantity
            self.shopping_map[key]["timestamp"] = time.time()

    def update_acquired_status(self, key, status):
        if key in self.shopping_map:
            self.shopping_map[key]["acquired"] = status
            self.shopping_map[key]["timestamp"] = time.time()

    # Add merge function
    # ...
    def merge(self, other_map):
        for key, other_item in other_map.shopping_map.items():
            if key in self.shopping_map:
                current_item = self.shopping_map[key]
                if other_item["timestamp"] > current_item["timestamp"]:
                    self.shopping_map[key] = other_item  # Update with the latest timestamp
            else:
                self.shopping_map[key] = other_item  # Add if the key doesn't exist in self.shopping_map

# # Example usage:

# # Instance of shopping list
# shopping_list = AWORMap()

# # Define item
# item_id1 = str(uuid.uuid4())
# item_id2 = str(uuid.uuid4())

# item1 = {
#     "name": "Milk",
#     "quantity": int("2"),
#     "acquired": False,
#     "timestamp": time.time(),
# }
# item2 = {
#     "name": "Apple",
#     "quantity": int("5"),
#     "acquired": False,
#     "timestamp": time.time(),
# }

# # Add items created to the list
# shopping_list.add_item(item_id1, item1)
# shopping_list.add_item(item_id2, item2)

# # Get shopping list
# user_input_id = input("Enter Shopping List ID: ")
# if user_input_id == shopping_list.shopping_list_id:
#     shopping_list.get_shopping_list(user_input_id)
#     while True:
#         print("\nMenu:")
#         print("1. Add item")
#         print("2. Remove item")
#         print("3. Update quantity")
#         print("4. Update acquired status")
#         print("5. Exit")

#         choice = input("Enter your choice (1-5): ")

#         if choice == "1":
#             # Add item
#             item_id = str(uuid.uuid4())  # Generate a new ID for the item
#             item_name = input("Enter item name: ")
#             item_quantity = int(input("Enter item quantity: "))

#             new_item = {
#                 "name": item_name,
#                 "quantity": item_quantity,
#                 "acquired": False,
#                 "timestamp": time.time(),  # Set timestamp for new item
#             }

#             shopping_list.add_item(item_id, new_item)
#             print("Item added successfully.")
#             shopping_list.get_shopping_list(user_input_id)  # Display updated list

#         elif choice == "2":
#             # Remove item
#             item_to_remove = input("Enter ID of the item to remove: ")
#             shopping_list.remove_item(item_to_remove)
#             print("Item removed successfully.")
#             shopping_list.get_shopping_list(user_input_id)  # Display updated list

#         elif choice == "3":
#             # Update quantity
#             item_to_update = input("Enter ID of the item to update quantity: ")
#             quantity_to_update = int(input("Enter desired quantity: "))
#             shopping_list.update_quantity(item_to_update, quantity_to_update)
#             print("Quantity updated successfully.")
#             shopping_list.get_shopping_list(user_input_id)  # Display updated list

#         elif choice == "4":
#             # Update acquired status
#             item_to_update = input("Enter ID of the item to update status: ")
#             acquired_status = input("Enter 'True' if item is acquired, 'False' otherwise: ").lower()

#             if acquired_status == 'true':
#                 acquired_status = True
#             elif acquired_status == 'false':
#                 acquired_status = False
#             else:
#                 print("Invalid input for acquired status. Please enter 'True' or 'False'.")
#                 continue

#             shopping_list.update_acquired_status(item_to_update, acquired_status)
#             print("Acquired status updated successfully.")
#             shopping_list.get_shopping_list(user_input_id)  # Display updated list

#         elif choice == "5":
#             # Exit
#             break

#         else:
#             print("Invalid choice. Please enter a valid option.")
# else:
#     print("Invalid Shopping List ID.")


# counter para quantity, acquired

from threading import Thread

# Your AWORMap class definition

# Create instances of AWORMap to simulate different replicas
replica1 = AWORMap()
replica2 = AWORMap()

# Function to simulate updates on replica 1
def simulate_replica1_updates():
    for i in range(5):
        item_id = str(i)
        item = {"name": f"Item_{i}", "quantity": i, "acquired": False, "timestamp": time.time()}
        replica1.add_item(item_id, item)
        time.sleep(0.5)  # Introduce delay between updates

# Function to simulate conflicting updates on replica 2
def simulate_replica2_updates():
    for i in range(5):
        item_id = str(i)
        # Simulate conflicting updates with different values but same key and timestamp
        item = {"name": f"Conflicting_Item_{i}", "quantity": i + 10, "acquired": True, "timestamp": time.time()}
        replica2.add_item(item_id, item)
        time.sleep(0.5)  # Introduce delay between updates

# Start threads to simulate updates on replicas concurrently
thread_replica1 = Thread(target=simulate_replica1_updates)
thread_replica2 = Thread(target=simulate_replica2_updates)

thread_replica1.start()
thread_replica2.start()

# Wait for threads to finish
thread_replica1.join()
thread_replica2.join()

# Merge the updates from replica 2 into replica 1
replica1.merge(replica2)

# Get the final shopping list state from replica 1 after merging
print("Final Shopping List State from Replica 1 after merging:")
replica1.get_shopping_list(shopping_list_id="1")  # Provide the shopping list ID if needed
