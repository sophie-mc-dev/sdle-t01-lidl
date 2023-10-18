import socket
from importlib.machinery import SourceFileLoader


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

while True:
    # Accept a connection from a client
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    # Receive the key from the client
    key = client_socket.recv(1024).decode()
    print(f"Received key: {key}")

    if (key):
        
        list_id = create_shopping_list()
        add_item_to_list(list_id, "Milk", 2)
        add_item_to_list(list_id, "Eggs", 1)

        # Get the list items
        items = [str(item) for item in local_lists[list_id].items]

        # Send the list items back to the client
        client_socket.send(" ".join(items).encode())
    else:
        client_socket.send("Invalid key".encode())

    # Close the client socket
    client_socket.close()