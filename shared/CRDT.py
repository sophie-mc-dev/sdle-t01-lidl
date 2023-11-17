import uuid

class AWORMap:
    def __init__(self):
        self.shopping_list_id = "1"
        self.shopping_map = {}

    def add_item(self, key, item):
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




# Example usage:

# Instance of shopping list
shopping_list = AWORMap()

# Define item
item_id1 = str(uuid.uuid4())
item_id2 = str(uuid.uuid4())

item1 = {
    "name": "Milk",
    "quantity": int("2"),
    "acquired": False,
    "timestamp": 1  # Add timestamp for versioning/CRDT purposes
}
item2 = {
    "name": "Apple",
    "quantity": int("5"),
    "acquired": False,
    "timestamp": 2  
}

# Add items created to the list
shopping_list.add_item(item_id1, item1)
shopping_list.add_item(item_id2, item2)

# Get shopping list
user_input_id = input("Enter Shopping List ID: ")
if user_input_id == shopping_list.shopping_list_id:
    while True:
        print("\nMenu:")
        print("1. Add item")
        print("2. Remove item")
        print("3. Exit")
        
        choice = input("Enter your choice (1/2/3): ")

        if choice == "1":
            # Add item
            item_id = str(uuid.uuid4())  # Generate a new ID for the item
            item_name = input("Enter item name: ")
            item_quantity = int(input("Enter item quantity: "))

            new_item = {
                "name": item_name,
                "quantity": item_quantity,
                "acquired": False,
                "timestamp": 3  # Set timestamp for new item
            }
            shopping_list.add_item(item_id, new_item)
            print("Item added successfully.")
            shopping_list.get_shopping_list(user_input_id)  # Display updated list
            
        elif choice == "2":
            # Remove item
            item_to_remove = input("Enter ID of the item to remove: ")
            shopping_list.remove_item(item_to_remove)
            print("Item removed successfully.")
            shopping_list.get_shopping_list(user_input_id)  # Display updated list
            
        elif choice == "3":
            # Exit
            break
        
        else:
            print("Invalid choice. Please enter a valid option.")
else:
    print("Invalid Shopping List ID.")



# counter para quantity, acquired
# update quantity function
# update acquired status function