import socket
import sys
from os.path import dirname, abspath
from shared.utils import *
from shared.CRDT import *

parent_dir = dirname(dirname(abspath(__file__)))
sys.path.append(parent_dir)

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set the host and port
host = "localhost"
port = 5555

# Connect to the server
client_socket.connect((host, port))

user_id = client_socket.recv(1024).decode()
file_path = db_dir + "/client_data/clients_lists/" + user_id + ".txt"
clients_lists_dir = db_dir + "/client_data/clients_lists/"
listed = False

while not listed:
    message = client_socket.recv(1024).decode()

    if "No active shooping lists." in message:
        print("There are no active shooping lists. Let's create one for you.\n")
        
        # Create ShoppingList object
        shopping_list = ShoppingList()
        local_list[user_id] = shopping_list

    elif "There already are active shooping lists" in message:
        print("1 - Create a new shopping list")
        print("2 - Connect to an existent shopping list")

        option = input("Option: ")
        client_socket.send(option.encode())

        message = client_socket.recv(1024).decode()

        if "Create new shopping list" in message: # option 1
            print("Let's create a new shopping list.\n")

            # Create ShoppingList object
            shopping_list = ShoppingList()
            local_list[user_id] = shopping_list

        elif "Choose one list ID" in message: # option 2
            print(message) # Available lists to choose

            chosen_list_id = input("List ID: ")
            client_socket.send(chosen_list_id.encode())

            # Create ShoppingList object
            shopping_list = ShoppingList()
            local_list[user_id] = shopping_list

            message = client_socket.recv(1024).decode() # "Your list id is '" + list_id + "'."


            client_socket.send("Has content?".encode())
            # create a personal shopping list (copy from the original),
            # this list is not shared with anybody
            message = client_socket.recv(1024).decode()

            if "empty_list" not in message:
                # Split the received data using '\n' as the separator and store it in a list
                list = message.split('\n')

                # Add '\n' to the end of each element in the list
                items = [item for item in list if item != ""]
                # 'items' contains the items from local client union with server items

                for line in items:
                    item_id, item_name, item_quantity, item_acquired, item_timestamp = line.split(':')

                    item = {
                        "name": item_name,
                        "quantity": item_quantity,
                        "acquired": item_acquired,
                        "timestamp": item_timestamp
                    }

                    local_list[user_id].add_item(item_id, item)

            
    listed = True
    

# Continue with list management or other operations
while True:
    message = client_socket.recv(1024).decode()

    if "Show menu" in message:

        # antes de mostrar a lista, dar pull da do servidor:        
        # ---------- server sync: -----------
        
        # Read client's shopping list
        items_str = ""

        for item_id, item in local_list[user_id].shopping_map.items():
            items_str += str(item_id) + ':' + str(item['name']) + ':' + str(item['quantity']) + ':' + str(item['acquired']) + ':' + str(item['timestamp']) + '\n'

        if items_str != "":

            # Send client list items to server
            client_socket.send(items_str.encode())

            # Receive new items list and update client list
            encoded_list_plus_message = client_socket.recv(1024).decode().strip()
            print("after server synccc_________________")
            print(encoded_list_plus_message)

            # Split the received data using '\n' as the separator and store it in a list
            list_plus_message = encoded_list_plus_message.split('\n')

            # separate items from syncronization output
            sync_output = list_plus_message.pop()
            print(sync_output)


            # Add '\n' to the end of each element in the list
            items = [item + '\n' for item in list_plus_message]
            # 'items' contains the items from local client union with server items

            local_list[user_id] = ShoppingList() # clear client shopping list
            for line in items:
                item_id, item_name, item_quantity, item_acquired, item_timestamp = line.split(':')

                item = {
                    "name": item_name,
                    "quantity": item_quantity,
                    "acquired": item_acquired,
                    "timestamp": item_timestamp
                }

                local_list[user_id].add_item(item_id, item)


        else:
            client_socket.send("noContent".encode())
            print("There's no need to syncronize with server.\n")

        #----------------------------------

        # Show user list content
        print("\n------------ MENU ------------")
        print("(after server sync)")
        print_user_list(user_id)

        print("\nChoose one option:")
        print(" 1 - Modify Shopping List")
        print(" 0 - Exit")
        key = input("Option: ")
            

        if key == "1":
            print_user_list(user_id)

            print("Choose one option:")
            print(" 1 - Add item")
            print(" 2 - Delete item")
            print(" 3 - Increment quantity")
            print(" 4 - Decrement quantity")
            print(" 5 - Item acquired")
            print(" 6 - Item not acquired")
            print(" 0 - Exit")
            key = input("Option: ")

            if key == "1": 
                item={}
                item_id = str(uuid.uuid4())  
                item["name"] = input("> Enter item name: ")
                item["quantity"] = input("> Enter item quantity: ")

                try:
                    item["quantity"] = int(item["quantity"])
                    local_list[user_id].add_item(item_id, item)
                    print_user_list(user_id)
                except ValueError:
                    print("Quantity must be an integer.")
        
            elif key == "2": 
                is_empty = True

                for item in local_list[user_id].shopping_map.items():
                    is_empty = False
                    print(item.__str__())

                if is_empty:
                    print("\nYou have no items to delete.\n")
                else:
                    item_to_remove = input("> Enter ID of the item to remove: ")
                    local_list[user_id].remove_item(item_to_remove)
                    print("Item removed successfully.")
                    print_user_list(user_id)
                
            elif key == "3":
                item_to_update = input("> Enter ID of the item to remove: ")
                local_list[user_id].increment_quantity(item_to_update)
                print("Quantity incremented successfully.")
                print_user_list(user_id)

            elif key == "4":
                item_to_update = input("> Enter ID of the item to remove: ")
                local_list[user_id].decrement_quantity(item_to_update)
                print("Quantity incremented successfully.")
                print_user_list(user_id) 

            elif key == "5":
                item_to_update = input("Enter ID of the item to update status: ")
                local_list[user_id].update_acquired_status(item_to_update, True)
                print("Acquired status updated successfully.")
                print_user_list(user_id) 

            elif key == "6":
                item_to_update = input("Enter ID of the item to update status: ")
                local_list[user_id].update_acquired_status(item_to_update, False)
                print("Acquired status updated successfully.")
                print_user_list(user_id) 

            elif key == "0":
                print("End of connection.\n")
                break

        elif key == "0":
            print("End of connection.\n")
            break

# Close the client socket
client_socket.close()
