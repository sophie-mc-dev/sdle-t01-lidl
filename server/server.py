import socket
import threading
from operations import *
from auxiliar import *


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

# Function to handle a client
def handle_client(client_socket):
    print(f"Connection from {client_socket.getpeername()}")

    authenticated = False  # Track authentication status

    while not authenticated:
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


    # Once authenticated, proceed with list management

    listed = False

    while not listed:
        if len(local_lists) == 0:
            client_socket.send("Let's create a new shopping list.".encode())
            print("There are no active shooping lists. Let's create one.")
            list_id = create_shopping_list()    # create new shopping list 
            user_list[username] = list_id       # associate user with a shopping list
        else:
            client_socket.send("\n1 - Create a new shopping list \n2 - Connect to an existent shopping list".encode())
            #print("1 - Create a new shopping list \n 2 - Connect to an existent shopping list")
            option = client_socket.recv(1024).decode().strip()

            if option == "1":
                client_socket.send("Let's create a new shopping list.".encode())
                list_id = create_shopping_list()    # create new shopping list 
                user_list[username] = list_id       # associate user with a shopping list

            elif option == "2":                
                to_send = "Please choose one of the list IDs:\n"
                idx = 1
                for list_id in local_lists:
                    to_send += str(idx) + " - " + list_id + "\n"
                    idx = idx + 1
                #print(to_send)
                client_socket.send(to_send.encode())
                option = client_socket.recv(1024).decode().strip()

                aux = 1
                for list_id in local_lists:
                    if str(aux) == option:
                        user_list[username] = list_id
                        break
                    else:
                        aux = aux + 1

        listed = True
        
    
    print("User '", username, "' is associated with shopping list '", user_list[username], "'.")


    while True:
        client_socket.send("\nPress 1 to see list, 2 to add element, or 0 to exit:".encode())
        key = client_socket.recv(1024).decode().strip()

        if not key:
            print("Client disconnected unexpectedly.")
            break

        if key == "1":
            items = [str(item) for item in local_lists[list_id].items]
            client_socket.send("\n".join(items).encode())

        elif key == "2":
            client_socket.send("Name of the item:".encode())
            name = client_socket.recv(1024).decode().strip()

            client_socket.send("Quantity:".encode())
            quantity = client_socket.recv(1024).decode().strip()

            try:
                quantity = int(quantity)
                add_item_to_list(list_id, name, quantity)
            except ValueError:
                client_socket.send("Invalid quantity. Please enter a valid integer.".encode())

        elif key == "0":
            break

    client_socket.close()

# Main server loop
while True:
    client_socket, client_address = server_socket.accept()

    # Create a new thread to handle the client
    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
    client_handler.start()

