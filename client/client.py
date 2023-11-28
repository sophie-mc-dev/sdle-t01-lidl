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

        # create a personal shopping list (copy from the original),
        # this list is not shared with anybody
        create_file_from_url(username, clients_lists_dir, [])

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

            # create a personal shopping list (copy from the original),
            # this list is not shared with anybody
            create_file_from_url(username, clients_lists_dir, [])

            print(f"You are associated to list id '{list_id}'.")

        elif "Choose one list ID" in message: # option 2
            print(message)

            chosen_list_id = input("List ID: ")
            client_socket.send(chosen_list_id.encode())

            message = client_socket.recv(1024).decode() # "Your list id is '" + list_id + "'."
            list_id = extract_list_id(message)

            client_socket.send("Has content?".encode())
            # create a personal shopping list (copy from the original),
            # this list is not shared with anybody
            message = client_socket.recv(1024).decode()
            if "empty_list" in message:
                create_file_from_url(username, clients_lists_dir, [])
            else:
                file_content = message.strip().split(',')
                print("file content:")
                print(file_content)
                create_file_from_url(username, clients_lists_dir, file_content)
            
            print(f"You are associated to list id '{list_id}'.")

    listed = True
    


# Continue with list management or other operations
while True:
    
    message = client_socket.recv(1024).decode()

    if "Show menu" in message:

        # antes de mostrar a lista, dar pull da do servidor:        
        # ---------- server sync: -----------
        
        # read client's list
        items_str = ""
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    items_str += line
        except FileNotFoundError:
            pass

        if items_str != "":

            # Send client list items to server
            client_socket.send(items_str.encode())

            # Receive new items list and update client.txt
            encoded_list_plus_message = client_socket.recv(1024).decode().strip()

            # Split the received data using '\n' as the separator and store it in a list
            list_plus_message = encoded_list_plus_message.split('\n')

            # separate items from syncronization output
            sync_output = list_plus_message.pop()

            # Add '\n' to the end of each element in the list
            items = [item + '\n' for item in list_plus_message]

            # update client.txt
            try:
                with open(file_path, 'w') as file:
                    for line in items:
                        file.write(line)
            except FileNotFoundError:
                pass

            print(sync_output)

        else:
            client_socket.send("noContent".encode())
            print("There's no need to syncronize with server.\n")


        #----------------------------------

        # Show user list content
        print_user_list(username)

        print("\nChoose one option:")
        print(" 1 - Modify Shopping List")
        print(" 0 - Exit")
            
        key = input("Option: ")
        #client_socket.send(key.encode()) # only for key 4
            

        if key == "1":
            print("\nChoose one option:")
            print(" 1 - Add item")
            print(" 2 - Delete item")
            print(" 3 - Acquire item")
            print(" 0 - Exit")

            key = input("Option: ")
            #client_socket.send(key.encode())

            if key == "1": 
                item_name = input("> Name of the item: ")
                item_quant = input("> Quantity: ")

                try:
                    item_quant = int(item_quant)
                    add_item_to_list_file(username, item_name, item_quant)
                except ValueError:
                    print("Quantity must be an integer.")
        
            elif key == "2": 
                is_file_empty = True
                to_print = "\nChoose an item to delete: \n"
                items = []
                try:
                    with open(file_path, 'r') as file:
                        idx = 1
                        for line in file:
                            is_file_empty = False
                            name, quantity, acquired = line.strip().split(':')
                            string = str(idx) + " - [Name: " + name + ", Quantity: " + quantity + ", Acquired: " + acquired + "]"
                            items.append(string)
                            idx += 1
                except FileNotFoundError:
                    pass

                if is_file_empty:
                    print("\nYou have no items to delete.\n")
                else:  
                    to_print += "\n".join(items)
                    print(to_print)

                    item_number = input("> Item number: ")

                    try:
                        item_number = int(item_number)
                        print(delete_item_from_list_file(username, item_number-1))
                    except ValueError:
                        print("Item number must be an integer.")

            elif key == "3":

                is_file_empty = True
                to_print = "\nChoose an item to mark as acquired: \n"
                items = []
                try:
                    with open(file_path, 'r') as file:
                        idx = 1
                        for line in file:
                            is_file_empty = False
                            name, quantity, acquired = line.strip().split(':')
                            string = str(idx) + " - [Name: " + name + ", Quantity: " + quantity + ", Acquired: " + acquired + "]"
                            items.append(string)
                            idx += 1
                except FileNotFoundError:
                    pass

                if is_file_empty:
                    print("\nYou have no items to acquire.\n")
                else:  
                    to_print += "\n".join(items)
                    print(to_print)

                    item_number = input("> Item number: ")

                    try:
                        item_number = int(item_number)
                        print(acquire_item_from_list_file(username, item_number-1))
                    except ValueError:
                        print("Item number must be an integer.")
                

            elif key == "0":
                print("End of connection.\n")
                break



        elif key == "0":
            print("End of connection.\n")
            break


# Close the client socket
client_socket.close()
