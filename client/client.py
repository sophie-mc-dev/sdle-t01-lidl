import socket
import sys
from os.path import dirname, abspath

parent_dir = dirname(dirname(abspath(__file__)))
sys.path.append(parent_dir)

from shared.operations import *
from shared.utils import *


# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set the host and port
host = "localhost"
port = 5555

# Connect to the server
client_socket.connect((host, port))


username = client_socket.recv(1024).decode()

file_path = db_dir + "/client_data/clients_lists/" + username + ".txt"
clients_lists_dir = db_dir + "/client_data/clients_lists/"


listed = False

while not listed:
    message = client_socket.recv(1024).decode()

    if "No active shooping lists." in message:
        print("There are no active shooping lists. Let's create one for you.\n")

        list_id = extract_list_id(message)
        client_list[username] = ShoppingList(list_id)

        print(f"Your list id is '{list_id}'.")

    elif "There already are active shooping lists" in message:
        
        print("\n1 - Create a new shopping list \n2 - Connect to an existent shopping list")
        option = input("Option: ")
        client_socket.send(option.encode())

        message = client_socket.recv(1024).decode()

        if "Create new shopping list" in message: # option 1
            print("Let's create a new shopping list.\n")
            print(message)

            list_id = extract_list_id(message)
            client_list[username] = ShoppingList(list_id)

            print(f"You are associated to list id '{list_id}'.")

        elif "Choose one list ID" in message: # option 2
            print(message)

            chosen_list_id = input("List ID: ")
            client_socket.send(chosen_list_id.encode())

            message = client_socket.recv(1024).decode() # "Your list id is '" + list_id + "'."
            list_id = extract_list_id(message)
            client_list[username] = ShoppingList(list_id)


            client_socket.send("Has content?".encode())
            message = client_socket.recv(1024).decode()

            # if that list already has some content..
            if "empty_list" not in message:
                # Split the received data using '\n' as the separator and store it in a list
                list = message.split('\n')

                # Add '\n' to the end of each element in the list
                items = [item + '\n' for item in list]
                # 'items' contains the items from local client union with server items

                for item in items:
                    item_name, quantity, acquired = item.strip().split(':')
                    client_list[username].add_item(item_name, quantity, acquired)
            
            print(f"You are associated to list id '{list_id}'.")

    listed = True
    


# Continue with list management or other operations
while True:
    
    message = client_socket.recv(1024).decode()

    if "Show menu" in message:

        # ---------- server sync: -----------
        
        # read client's list
        items_str = ""
        for item in client_list[username].items:
            items_str += item.name + ':' + str(item.quantity) + ':' + str(item.acquired) + '\n'

        if items_str != "":

            # Send client list items to server
            client_socket.send(items_str.encode())

            # Receive new items list and update client list
            encoded_list_plus_message = client_socket.recv(1024).decode().strip()

            # Split the received data using '\n' as the separator and store it in a list
            list_plus_message = encoded_list_plus_message.split('\n')

            # separate items from syncronization output
            sync_output = list_plus_message.pop()

            # Add '\n' to the end of each element in the list
            items = [item + '\n' for item in list_plus_message]
            # 'items' contains the items from local client union with server items

            client_list[username] = ShoppingList(list_id) # clear client shopping list
            for item in items:
                item_name, quantity, acquired = item.strip().split(':')
                client_list[username].add_item(item_name, quantity, acquired)

            print(sync_output)

        else:
            client_socket.send("noContent".encode())
            #print("There's no content to send.\n")

        #----------------------------------


        # Show user list content
        print("\n------------ MENU ------------")
        
        if client_list[username].is_empty():
            print("> Your list is empty.")
        else: 
            print("After server sync:")
            print_user_list(username)

        print("\nChoose one option:")
        print(" 1 - Modify Shopping List")
        print(" 0 - Exit")
        key = input("Option: ")
            

        if key == "1":
            print("\nChoose one option:")
            print(" 1 - Add item")
            print(" 2 - Delete item")
            print(" 0 - Exit")
            key = input("Option: ")

            if key == "1": 
                item_name = input("> Name of the item: ")
                item_quant = input("> Quantity: ")

                try:
                    item_quant = int(item_quant)
                    # adicionar o novo elemento:
                    client_list[username].add_item(item_name, item_quant, False)
                    print("Item added with success.\n")
                    print_user_list(username)

                except ValueError:
                    print("Quantity must be an integer.")
        

            elif key == "2": 
                print("\nChoose an item to delete:")
                for item in client_list[username].items:
                    print(item.__str__())

                if client_list[username].is_empty():
                    print("\nYou have no items to delete.\n")
                else:
                    item_ID = input("> Item ID: ")
                    client_list[username].delete_item(item_ID)
                    print("Item deleted with success.\n")
                    print_user_list(username)

            elif key == "0":
                print("End of connection.\n")
                break


        elif key == "0":
            print("End of connection.\n")
            break


# Close the client socket
client_socket.close()
