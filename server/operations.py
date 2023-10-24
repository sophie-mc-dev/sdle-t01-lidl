import uuid
from models import *


# Local storage:
#  - is a dictionary used for local storage of shopping lists,
#  (simulated as an in-memory data structure)
local_lists = {}


# Cloud storage (simulated):
# - is a dictionary simulating cloud storage for shopping lists
cloud_storage = {}


# Functions to Manage Shopping Lists:

# creates a new shopping list and returns its unique list_id
def create_shopping_list():
    list_id = str(uuid.uuid4())
    local_lists[list_id] = ShoppingList(list_id)
    cloud_storage[list_id] = local_lists[list_id]
    return list_id

#  adds an item to a shopping list given its list_id, name, and quantity
def add_item_to_list(list_id, name, quantity):
    if list_id not in local_lists:
        raise ValueError("List not found.")

    local_lists[list_id].add_item(name, quantity)
    # Update the cloud storage
    cloud_storage[list_id] = local_lists[list_id]

# delete_item_from_list() deletes an item from a shopping list based on its item_id
def delete_item_from_list(list_id, item_id):
    if list_id not in local_lists:
        raise ValueError("List not found.")

    local_lists[list_id].delete_item(item_id)
    # Update the cloud storage
    cloud_storage[list_id] = local_lists[list_id]

# marks an item as acquired based on its item_id
def acquire_item(list_id, item_id):
    if list_id not in local_lists:
        raise ValueError("List not found.")

    local_lists[list_id].acquire_item(item_id)
    # Update the cloud storage
    cloud_storage[list_id] = local_lists[list_id]