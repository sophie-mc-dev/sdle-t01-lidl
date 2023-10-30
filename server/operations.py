import uuid
from models import *
#from auxiliar import *



# Local storage:
#  - is a dictionary used for local storage of shopping lists,
#  (simulated as an in-memory data structure)
local_lists = {}


# Cloud storage (simulated):
# - is a dictionary simulating cloud storage for shopping lists
cloud_storage = {}


client_list = {}

# Fetch data

#credentials
user_credentials = {}
with open('db/user_credentials.txt', 'r') as file:
    for line in file:
        username, password = line.strip().split(':')
        user_credentials[username] = password

# user lists
user_list = {}
try:
    with open('db/user_list.txt', 'r') as file:
        for line in file:
            username, listID = line.strip().split(':')
            user_list[username] = listID
except FileNotFoundError:
    pass



import os
import urllib.parse

def create_empty_file_from_url(url, folder_path="./db/shopping_lists"):
    # Parse the URL to get the filename
    parsed_url = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed_url.path) + '.txt'

    # Join the folder_path and filename to create the full file path
    file_path = os.path.join(folder_path, filename)

    # Create an empty file
    with open(file_path, 'w') as file:
        pass

    return file_path


def save_shopping_list_to_file(credentials):
    with open('db/user_list.txt', 'w') as file: # Open in "write" mode ('w')
        for username, list_id in credentials.items():
            file.write(f"{username}:{list_id}\n")

def register_shopping_list(username, list_id):
    user_list[username] = list_id
    save_shopping_list_to_file(user_list)
    return "List Registration successful."

def create_new_shopping_list(username):
    list_id = str(uuid.uuid4())
    register_shopping_list(username, list_id)
    create_empty_file_from_url(list_id)
    client_list[list_id] = ShoppingList(list_id)
    #cloud_storage[list_id] = local_lists[list_id]
    return list_id




# Functions to Manage Shopping Lists:

#  adds an item to a shopping list given its list_id, name, and quantity
def add_item_to_list_file(list_id, name, quantity):

    file_content = []
    #try:
    #    with open("db/shopping_lists/" + list_id + ".txt", 'r') as file:
    #        for line in file:
    #            #item_name, quantity, acquired = line.strip().split(':')
    #            file_content.append(line)      
    #except FileNotFoundError:
    #    raise ValueError("List not found.")

    # Check if the item already exists in the list
    item_exists = False
    for item in client_list[list_id].items:
        if item.name.lower() == name.lower():
            item.quantity += quantity
            item_exists = True
            break

    # If the item doesn't exist, add it to the list
    if not item_exists:
        client_list[list_id].add_item(name, quantity)

    # update file
    for item in client_list[list_id].items:
        new_item_line = item.name + ":" + str(item.quantity) + ":" + str(False) + "\n"
        file_content.append(new_item_line)

    with open("db/shopping_lists/" + list_id + ".txt", 'w') as file:
        for line in file_content:
            file.write(line)


    # Update the cloud storage
    #cloud_storage[list_id] = local_lists[list_id]


# ------------------------

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

    # Check if the item already exists in the list
    item_exists = False
    for item in local_lists[list_id].items:
        if item.name.lower() == name.lower():
            item.quantity += quantity
            item_exists = True
            break

    # If the item doesn't exist, add it to the list
    if not item_exists:
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