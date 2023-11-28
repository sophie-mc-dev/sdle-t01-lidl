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
    