import sys
from os.path import dirname, abspath
import urllib.parse
import os


parent_dir = dirname(dirname(abspath(__file__)))
sys.path.append(parent_dir)

db_dir = parent_dir + "/database"


# ----------------------------- Data -----------------------------

# Local storage:
#  - is a dictionary used for local storage of shopping lists, (simulated as an in-memory data structure)
local_list = {}

# User lists
active_lists = []


# ----------------------------- Fetch data -----------------------------

try: # User lists
    with open(db_dir + "/server_data/active_lists_file.txt", 'r') as file:
        for list_id in file:
            if list_id != '\n':
                active_lists.append(list_id)
except FileNotFoundError:
    pass



# ----------------------------- Auxiliar functions -----------------------------

# prints current client local list
# function only called by the client
def print_user_list(user_id):
    print(f"\n> Your List content:")
    print("Items: ")
    if local_list[user_id].is_empty():
        print("Oops... Looks like you have no items yet.")
    else:
        for item_id, item in local_list[user_id].shopping_map.items():
            print(f" Item ID: {item_id}, Name: {item['name']}, Quantity: {item['quantity']}, Acquired: {item['acquired']}, Timestamp: {item['timestamp']}")
    print("------------------------------\n")
