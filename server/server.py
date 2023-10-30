import socket
import threading
import signal
import sys
from operations import *

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set the host and port
host = "localhost"
port = 5555

# Bind the socket to the host and port
server_socket.bind((host, port))

# Listen for incoming connections
server_socket.listen(5)  # 5 connections for now
print("Server is listening...")


# list content

def save_credentials_to_file(credentials):
    with open('db/user_credentials.txt', 'w') as file:
        for username, password in credentials.items():
            file.write(f"{username}:{password}\n")

def register_user(username, password):
    if username in user_credentials:
        return "Username already exists. Please choose a different one."
    user_credentials[username] = password
    save_credentials_to_file(user_credentials)
    return "Registration successful. You can now log in."


def print_user_list():
    try:
        user_list = {}
        with open('db/user_list.txt', 'r') as file:

            for line in file:
                username, listID = line.strip().split(':')
                user_list[username] = listID
    except FileNotFoundError:
        pass

    print("\n> User:ListID contents:")
    for username, list_id in user_list.items():
            print(f"{username}:{list_id}\n")


import os

def is_file_empty(filename):
    try:
        file_path = "./db/shopping_lists/" + filename + ".txt"
        # Get the size of the file
        file_size = os.path.getsize(file_path)
        return file_size == 0
    except FileNotFoundError:
        # Handle the case where the file does not exist
        return False


# Function to handle a client
def handle_client(client_socket):
    print(f"Connection from {client_socket.getpeername()}")

    authenticated = False  # Track authentication status

    while not authenticated:
        client_socket.send("\n1 - Log in\n2 - Register\nYour choice:".encode())
        choice = client_socket.recv(1024).decode().strip()

        if choice == "1":
            # Authentication loop
            client_socket.send("Username:".encode())
            username = client_socket.recv(1024).decode().strip()

            client_socket.send("Password:".encode())
            password = client_socket.recv(1024).decode().strip()

            if username in user_credentials and user_credentials[username] == password:
                authenticated = True
                client_socket.send("Authentication successful. You can now access your list.".encode())
            else:
                client_socket.send("Authentication failed. Please try again.".encode())
        
        elif choice == "2":
            client_socket.send("Choose a Username:".encode())
            new_username = client_socket.recv(1024).decode().strip()

            client_socket.send("Choose a Password:".encode())
            new_password = client_socket.recv(1024).decode().strip()

            registration_result = register_user(new_username, new_password)
            client_socket.send(registration_result.encode())
            if ("Registration successful" in registration_result):
                authenticated = True
                username = new_username
                user_list[username] = None 
        else:
            client_socket.send("Invalid choice. Please choose 1 or 2.".encode())



    # Once authenticated, proceed with list management

    listed = False

    while not listed:


        if len(user_list) == 0:
            to_send = "Let's create a new shopping list. \n"
            print("There are no active shooping lists. Let's create one.")
            
            list_id = create_new_shopping_list(username) # create_shopping_list(username)    # create new shopping list 
            #register_list(username, list_id)       # associate user with a shopping list
            
            to_send = to_send + "Your list id is '" + list_id + "'."
            client_socket.send(to_send.encode())
            
            print_user_list()

        else:
            client_socket.send("\n1 - Create a new shopping list \n2 - Connect to an existent shopping list".encode())
            option = client_socket.recv(1024).decode().strip()

            if option == "1":
                client_socket.send("Let's create a new shopping list.".encode())
                list_id = create_new_shopping_list(username) # create_shopping_list(username)    # create new shopping list 
                #user_list[username] = list_id       # associate user with a shopping list

                print_user_list()

            elif option == "2":                
                to_send = "Please choose one of the list IDs:\n"

                # get all the lists available
                available_lists = []
                for user_name, list_id in user_list.items():
                    if list_id != None:
                        available_lists.append(list_id)
                available_lists = list(set(available_lists))

                idx = 1
                for list_id in available_lists:
                    to_send += str(idx) + " - " + str(list_id) + "\n"
                    idx = idx + 1

                client_socket.send(to_send.encode())
                option = client_socket.recv(1024).decode().strip()

                user_list[username] = available_lists[int(option) - 1]
                save_shopping_list_to_file(user_list)

                print_user_list()

                

        listed = True
        
    
    print("User '", username, "' is associated with shopping list '", user_list[username], "'.")


    while True:
        client_socket.send("\nPress 1 to see list, 2 to add element, or 0 to exit:".encode())
        key = client_socket.recv(1024).decode().strip()

        if not key:
            print("Client disconnected unexpectedly.")
            break

        if key == "1":
            if is_file_empty(user_list[username]) == True:
                client_socket.send("Your shopping list is empty. Try to add some items to your list.".encode())
            else:
                items = []
                try:
                    with open("db/shopping_lists/" + list_id + ".txt", 'r') as file:
                        for line in file:
                            name, quantity, acquired = line.strip().split(':')
                            string = "[Name: " + name + ", Quantity: " + quantity + ", Acquired: " + acquired + "]"
                            items.append(string)
                except FileNotFoundError:
                    pass
                client_socket.send("\n".join(items).encode())

        elif key == "2":
            client_socket.send("Name of the item:".encode())
            name = client_socket.recv(1024).decode().strip()

            client_socket.send("Quantity:".encode())
            quantity = client_socket.recv(1024).decode().strip()

            try:
                quantity = int(quantity)
                add_item_to_list_file(list_id, name, quantity)
            except ValueError:
                client_socket.send("Invalid quantity. Please enter a valid integer.".encode())

        elif key == "0":
            client_socket.send("End of connection.".encode())
            break

    client_socket.close()

def signal_handler(sig, frame):
    print("\nShutting down the server...")
    server_socket.close()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)


# Main server loop
while True:
    client_socket, client_address = server_socket.accept()

    # Create a new thread to handle the client
    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()

