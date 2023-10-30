import socket

import sys
from os.path import dirname, abspath


parent_dir = dirname(dirname(abspath(__file__)))
sys.path.append(parent_dir)

from server.operations import *

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set the host and port
host = "localhost"
port = 5555

# Connect to the server
client_socket.connect((host, port))

client_list = ""
authenticated = False

while not authenticated:
    # Authentication loop
    message = client_socket.recv(1024).decode()
    #print(message)

    if "Authentication successful" in message or "Registration successful." in message:
        print(message)
        authenticated = True
    else:
        choice = input(message)
        client_socket.send(choice.encode())


def extract_list_id(message):
    start_index = message.find("Your list id is '")

    if start_index != -1:
        end_index = message.find("'", start_index + len("Your list id is '"))

        if end_index != -1:
            list_id = message[start_index + len("Your list id is '"):end_index]
            return list_id
        else:
            print("Closing single quote not found.")
    else:
        print("Message format not recognized.")
    return None


listed = False

while not listed:
    message = client_socket.recv(1024).decode()

    if "There are no active shooping lists." in message:
        print(message) 

        list_id = extract_list_id(message)
        if list_id is not None:
            client_list = list_id
    
    else:
        print(message)
        option = input("Option: ")
        client_socket.send(option.encode())

        message = client_socket.recv(1024).decode()

        if "Let's create a new shopping list." in message: # option 1
            list_id = extract_list_id(message)
            if list_id is not None:
                client_list = list_id

        elif "Please choose one of the list IDs:" in message: # option 2
            print(message)
            list_id = input("List ID: ")
            client_socket.send(list_id.encode())

            message = client_socket.recv(1024).decode() # "Your list id is '" + list_id + "'."

            list_id = extract_list_id(message)
            if list_id is not None:
                client_list = list_id

    listed = True
    
print("> You are associated with shopping list '", client_list, "'.")


# Continue with list management or other operations
while True:
    # Receive and print the server's message
    message = client_socket.recv(1024).decode()
    if not message.endswith(":"):
        print(message)

    if message.endswith(":"):
        print(message)
        key = input("Option: ")
        client_socket.send(key.encode())

    elif message in "Add Item":
        item_name = input("> Name of the item: ")
        item_quant = input("> Quantity: ")

        try:
            item_quant = int(item_quant)
            #print_lists(client_list)
            add_item_to_list_file(client_list, item_name, item_quant)
        
        except ValueError:
            print("Quantity must be an integer.")

    elif "End of connection." in message:
        break


# Close the client socket
client_socket.close()
