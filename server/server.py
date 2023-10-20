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


# CREATE LIST

list_id = create_shopping_list()
add_item_to_list(list_id, "Milk", 2)
add_item_to_list(list_id, "Eggs", 1)

while True:
    # Accept a connection from a client
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    while True:
        client_socket.send("\nPress 1 to see list, 2 to add element:".encode())

        # Receive the key from the client

        try:
            key = client_socket.recv(1024).decode().strip()
        except ConnectionResetError:
            print("Client closed the connection.")
            break

        if not key:
            print("Client disconnected unexpectedly.")
            break
        
        print(f"Received key: {key}")

        
        if (key == "1"):

            # Get the list items
            items = [str(item) for item in local_lists[list_id].items]

            # Send the list items back to the client
            client_socket.send(" ".join(items).encode())
        elif (key == "2"):
            client_socket.send("Name of the item:".encode())

            name = client_socket.recv(1024).decode().strip()

            client_socket.send("Quantity:".encode())

            quantity = client_socket.recv(1024).decode().strip()

            try:
                quantity = int(quantity)
                add_item_to_list(list_id, name, quantity)

            except ValueError:
                client_socket.send("Invalid quantity. Please enter a valid integer.".encode())
        elif (key == "0"):
            break # break inner loop
        

        else:
            client_socket.send("Invalid key".encode())

    # Close the client socket
    client_socket.close()