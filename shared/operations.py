import uuid
from .models import *
from .utils import *


# Functions to Manage Shopping Lists:

def create_personal_client_list(username, list_id):
    # check if list_id already has some content
    file_path = db_dir + "/server_data/shopping_lists/" + list_id + ".txt"
    if is_file_empty(file_path) == True:
        # create an empty file
        create_file_from_url(username, db_dir + "/client_data/clients_lists", [])
    else:
        # get content from list and write it in new personal client list
        file_content = []
        try:
            with open(db_dir + "/server_data/shopping_lists/" + list_id + ".txt", 'r') as file:
                for line in file:
                    file_content.append(line)
            create_file_from_url(username, db_dir + "/client_data/clients_lists", file_content)
            
        except FileNotFoundError:
            pass


def save_shopping_list_to_file(credentials):
    with open(db_dir + "/server_data/user_listsIDs.txt", 'w') as file: # Open in "write" mode ('w')
        for username, lists_IDs in credentials.items():
            file.write(f"{username}:{lists_IDs}\n")


def register_shopping_list(username, list_id):
    try:
        all_user_lists_str = user_list[username]
        all_user_lists_str += ',' + list_id
        user_list[username] = all_user_lists_str
    except:
        user_list[username] = list_id        

    save_shopping_list_to_file(user_list)

    return "List Registration successful."


def create_new_shopping_list(username):
    list_id = str(uuid.uuid4())
    register_shopping_list(username, list_id)
    create_file_from_url(list_id, db_dir + "/server_data/shopping_lists", [])
    client_list[list_id] = ShoppingList(list_id)
    return list_id

    

# Functions to Manage Shopping Lists Items:

#  adds an item to a shopping list given its list_id, name, and quantity
def add_item_to_list_file(username, name, quantity):

    # ler o conteudo do file
    file_content = []
    try:
        with open(db_dir + "/client_data/clients_lists/" + username + ".txt", 'r') as file:
            for line in file:
                #item_name, quantity, acquired = line.strip().split(':')
                file_content.append(line)      
    except FileNotFoundError:
        raise ValueError("List not found.")
    
    # atualizar a list: preencher a shooping list com o conteudo do file 
    client_list[username] = ShoppingList(username) # limpamos a shopping list
    for file_line in file_content:
        item_name, item_quantity, acquired = file_line.strip().split(':')
        client_list[username].add_item(item_name, item_quantity, acquired)

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

    # update file
    file_content = []
    print("\n=> CLIENT FILE CONTENT:")
    for item in client_list[username].items:
        new_item_line = item.name + ":" + str(item.quantity) + ":" + str(False) + "\n"
        file_content.append(new_item_line)
        print(new_item_line)


    with open(db_dir + "/client_data/clients_lists/" + username + ".txt", 'w') as file:
        for line in file_content:
            file.write(line)


# delete_item_from_list() deletes an item from a shopping list based on its item_id
def delete_item_from_list_file(username, item_idx):
    # ler o conteudo do file
    file_content = []
    try:
        with open(db_dir + "/client_data/clients_lists/" + username + ".txt", 'r') as file:
            for line in file:
                file_content.append(line)      
    except FileNotFoundError:
        raise ValueError("List not found.")
    
    file_content.pop(item_idx) 

    # atualizar a list: preencher a shooping list com o conteudo do file 
    client_list[username] = ShoppingList(username) # limpamos a shopping list
    for file_line in file_content:
        item_name, item_quantity, acquired = file_line.strip().split(':')
        client_list[username].add_item(item_name, item_quantity, acquired)

    # update file
    print("\n=> CLIENT FILE CONTENT:")
    with open(db_dir + "/client_data/clients_lists/" + username + ".txt", 'w') as file:
        for line in file_content:
            file.write(line)
            print(line)

    return "Item deleted with success.\n"
    

# marks an item as acquired based on its item_name
def acquire_item_from_list_file(username, item_number):

    item_number = int(item_number)

    # ler o conteudo do file
    file_content = []
    try:
        with open(db_dir + "/client_data/clients_lists/" + username + ".txt", 'r') as file:
            for line in file:
                #item_name, quantity, acquired = line.strip().split(':')
                file_content.append(line)      
    except FileNotFoundError:
        raise ValueError("List not found.")
    
    # atualizar a list: preencher a shooping list com o conteudo do file 
    client_list[username] = ShoppingList(username) # limpamos a shopping list

    counter = 0
    for file_line in file_content:
        item_name, item_quantity, acquired = file_line.strip().split(':')
        if counter == item_number:
            client_list[username].add_item(item_name, item_quantity, str(True))
        else:
            client_list[username].add_item(item_name, item_quantity, acquired)
        counter += 1

    # update file
    file_content = []
    print("\n=> CLIENT FILE CONTENT:")
    for item in client_list[username].items:
        new_item_line = item.name + ":" + str(item.quantity) + ":" + str(item.acquired) + "\n"
        file_content.append(new_item_line)
        print(new_item_line)