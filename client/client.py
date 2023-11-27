import socket
import sys
from os.path import dirname, abspath

parent_dir = dirname(dirname(abspath(__file__)))
sys.path.append(parent_dir)

from shared.operations import *
from shared.utils import *


# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set the host and port of the load balancer
load_balancer_host = "localhost"
load_balancer_port = 9090

# Connect to the load balancer
client_socket.connect((load_balancer_host, load_balancer_port))

client_list = ""
file_path = db_dir + "/client_data/clients_lists/" + username + ".txt"

client_socket.send("Hello from the client!".encode())
response = client_socket.recv(1024).decode()
print(response)  # DOESNT RECEIVE ANYTHING

authenticated = False
print("Welcome to the shopping list app!\n") #BUT PRINTS THIS
while not authenticated:
    # Authentication loop
    message = client_socket.recv(1024).decode()  
    print(message)

    if "Authentication successful" in message or "Registration successful." in message:
        print(message)
        username = extract_username(message)
        if username is not None:
            client_username = username
        authenticated = True
    else:
        choice = input(message)
        client_socket.send(choice.encode())



listed = False

while not listed:
    message = client_socket.recv(1024).decode()
    print(message) #já tiro

    if "No active shooping lists." in message:
        print("There are no active shooping lists. Let's create one for you.\n")

        list_id = extract_list_id(message)
        if list_id is not None:
            client_list = list_id
        
        # create a personal shopping list (copy from the oriinal),
        # this list is not shared with anybody
        create_personal_client_list(client_username, client_list)
        print(f"Your list id is '{client_list}'.")

    elif "There already are active shooping lists" in message:
        print("\n1 - Create a new shopping list \n2 - Connect to an existent shopping list")
        option = input("Option: ")
        client_socket.send(option.encode())

        message = client_socket.recv(1024).decode()

        if "Create new shopping list" in message: # option 1
            print("Let's create a new shopping list.\n")
            print(message)
            list_id = extract_list_id(message)
            if list_id is not None:
                client_list = list_id
            create_personal_client_list(client_username, client_list)
            print(f"You are associated to list id '{client_list}'.")


        elif "Choose one list ID" in message: # option 2
            print(message)

            list_id = input("List ID: ")
            client_socket.send(list_id.encode())

            message = client_socket.recv(1024).decode() # "Your list id is '" + list_id + "'."

            list_id = extract_list_id(message)
            if list_id is not None:
                client_list = list_id

            create_personal_client_list(client_username, client_list)
            print(f"You are associated to list id '{client_list}'.")


    listed = True
    
#print("> You are associated with shopping list '", client_list, "'.")


# Continue with list management or other operations
while True:
    
    message = client_socket.recv(1024).decode()

    if "Show menu" in message:
        print("\nChoose one option:")
        print(" 1 - Check your list")
        print(" 2 - Add item")
        print(" 3 - Delete item")
        print(" 4 - Server syncronization")
        print(" 0 - Exit")
            
        key = input("Option: ")
        client_socket.send(key.encode()) # only for key 4

        if key == "1": 
            is_file_empty = True
            items = []
            items.append("\nYour list content:")
            try:
                with open(db_dir + "/client_data/clients_lists/" + username + ".txt", 'r') as file:
                    for line in file:
                        print(line)
                        if is_file_empty:
                            is_file_empty = False
                        name, quantity, acquired = line.strip().split(':')
                        string = "- [Name: " + name + ", Quantity: " + quantity + ", Acquired: " + acquired + "]"
                        items.append(string)
            except FileNotFoundError:
                pass

            if is_file_empty:
                print("\nYour shopping list is empty. Try to add some items to your list.\n")
            else:  
                print("\n".join(items))
        
        elif key == "2": 
            item_name = input("> Name of the item: ")
            item_quant = input("> Quantity: ")

            try:
                item_quant = int(item_quant)
                add_item_to_list_file(client_username, item_name, item_quant)
            except ValueError:
                print("Quantity must be an integer.")
    
        elif key == "3": 
            is_file_empty = True
            to_print = "\nChoose an item to delete: \n"
            items = []
            try:
                with open(db_dir + "/client_data/clients_lists/" + username + ".txt", 'r') as file:
                    idx = 1
                    for line in file:
                        if is_file_empty:
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
                    print(delete_item_from_list_file(client_username, item_number-1))
                except ValueError:
                    print("Item number must be an integer.")

        elif key == "4": 
            client_items = []
            items_str = ""
            try:
                with open(db_dir + "/client_data/clients_lists/" + username + ".txt", 'r') as file:
                    for line in file:
                        items_str += line
            except FileNotFoundError:
                pass

            # Send client list items to server
            client_socket.send(items_str.encode())

            # Receive new items list and update client .txt
            encoded_list_plus_message = client_socket.recv(1024).decode().strip()

            # Split the received data using '\n' as the separator and store it in a list
            list_plus_message = encoded_list_plus_message.split('\n')

            # separate items from syncronization output
            sync_output = list_plus_message.pop()

            # Add '\n' to the end of each element in the list
            items = [item + '\n' for item in list_plus_message]

            # update client .txt
            try:
                with open(db_dir + "/client_data/clients_lists/" + username + '.txt', 'w') as file:
                    for line in items:
                        file.write(line)
            except FileNotFoundError:
                pass

            print(sync_output)

        elif key == "0":
            print("End of connection.\n")
            break


# Close the client socket
client_socket.close()
