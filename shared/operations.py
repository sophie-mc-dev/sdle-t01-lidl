import uuid
from .models import *
from .utils import *


# ------------------- Functions to Manage Shopping Lists and it's items -------------------

# creates a new empty shopping list and associates it with the client
# function only called by the server
def create_new_shopping_list(username):
    list_id = str(uuid.uuid4())

    # register shopping list
    user_list[username] = list_id        

    # save clients lists
    with open(db_dir + "/server_data/user_listsIDs.txt", 'w') as file:
        for username, lists_IDs in user_list.items():
            file.write(f"{username}:{lists_IDs}\n")

    create_file_from_url(list_id, db_dir + "/server_data/shopping_lists", [])
    client_list[list_id] = ShoppingList(list_id)
    
    return list_id

    
# adds an item to a shopping list given its list_id, name, and quantity
# function only called by the client
def add_item_to_list_file(username, name, quantity):

    # adicionar o novo elemento:
    # 1 - Check if the item already exists in the list
    item_exists = False
    for item in client_list[username].items:
        if item.name.lower() == name.lower():
            item.quantity = str(int(item.quantity) + int(quantity))
            item_exists = True
            break
    # 2 - If the item doesn't exist, add it to the list
    if not item_exists:
        client_list[username].add_item(name, quantity, False)

    print("\n=> CLIENT CONTENT:")
    for item in client_list[username].items:
        print(item.__str__())
    print("-------------------")
  

# delete_item_from_list() deletes an item from a shopping list based on its item_id
# function only called by the client
def delete_item_from_list_file(username, item_ID):

    client_list[username].delete_item(item_ID)

    # update file
    print("\n=> CLIENT CONTENT:")
    for item in client_list[username].items:
        print(item.__str__())
    print("-------------------")
    

    return "Item deleted with success.\n"
    