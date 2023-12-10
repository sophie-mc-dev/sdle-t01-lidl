import sys
from os.path import dirname, abspath
import urllib.parse
import os
from shared.CRDT import ShoppingList

parent_dir = dirname(dirname(abspath(__file__)))
sys.path.append(parent_dir)

db_dir = parent_dir + "/database"


# ----------------------------- Data -----------------------------

# Local storage:
#  - is a dictionary used for local storage of shopping lists, (simulated as an in-memory data structure)
local_list = {}

# Active shopping lists
active_lists = []


# ----------------------------- Fetch data -----------------------------

# Active shopping lists
try: 
    with open(db_dir + "/active_lists_file.txt", 'r') as file:
        for list_id in file:
            list_id = list_id.strip()  # Removes '\n'
            active_lists.append(list_id)
except FileNotFoundError:
    pass


# Get server local shopping lists
try: 
    for list_id in active_lists:

        shopping_list = ShoppingList()
        shopping_list.set_id(list_id)

        with open(db_dir + "/shopping_lists/" + list_id + ".txt", 'r') as file:
            for line in file:
                line = line.strip()
                item_id, item_name, item_quantity, item_acquired, item_timestamp = line.split(':')

                item = {
                    "name": item_name,
                    "quantity": item_quantity,
                    "acquired": item_acquired,
                    "timestamp": item_timestamp
                }

            shopping_list.fill_with_item(item_id, item)

        local_list[list_id] = shopping_list
        
except FileNotFoundError:
    pass


# ----------------------------- Auxiliar functions -----------------------------

# prints current client local list items
def print_user_list(list_id):
    if local_list[list_id].is_empty():
        print("\nOops...")
        print("Looks like you have no items yet.")
    else:
        print(f"\n> Your Shopping List Items:")
        for item_id, item in local_list[list_id].shopping_map.items():
            print(f" - Name: {item['name']}, Quantity: {item['quantity']}, Acquired: {item['acquired']}, Timestamp: {item['timestamp']}")

def show_menu(list_id):
    print("\n-------------- MENU --------------")
    print_user_list(list_id)
    print("\n----------------------------------") 

    print("\nChoose one option:")
    print(" 1 - Modify Shopping List")
    print(" 0 - Syncronize Shopping List")
    key = input("Option: ")   

    return key



# called to show items before a list modification
def aux_print_items(list_id):
    print("\nItems:")
    for item_id, item in local_list[list_id].shopping_map.items():
        print(f" - Name: {item['name']}, Quantity: {item['quantity']}, Acquired: {item['acquired']}, Timestamp: {item['timestamp']}")

 