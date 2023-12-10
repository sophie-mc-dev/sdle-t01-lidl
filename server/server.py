import socket
import threading
import signal
import sys
from os.path import dirname, abspath
from shared.utils import *
from shared.CRDT import *

parent_dir = dirname(dirname(abspath(__file__)))
sys.path.append(parent_dir)

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set the host and port
host = "localhost"
port = 5555

# Bind the socket to the host and port
server_socket.bind((host, port))

# Listen for incoming connections
server_socket.listen(5)  # 5 connections for now
print("\nServer is listening...")

# Function to handle a client
def handle_client(client_socket):
    print(f"Connection from {client_socket.getpeername()}")
    
    # Create ShoppingList object
    shopping_list_from_client = ShoppingList()


    # Get data from client socket

    encoded_client_items = client_socket.recv(1024).decode().strip()
    client_shoppint_list_items = encoded_client_items.split('\n')
    
    for line in client_shoppint_list_items:

        
        item_id, item_name, item_quantity, item_acquired, item_timestamp = line.split(':')

        if item_id == "list_id":
            list_id = item_timestamp
            shopping_list_from_client.set_id(list_id)
            continue
        
        item = {
            "name": item_name,
            "quantity": item_quantity,
            "acquired": item_acquired,
            "timestamp": item_timestamp
        }

        shopping_list_from_client.fill_with_item(item_id, item)


        print("\n\n> Client Shopping List '" + list_id + "' initial content:")
        for item_id, item in shopping_list_from_client.shopping_map.items():
            print(f" - Name: {item['name']}, Quantity: {item['quantity']}, Acquired: {item['acquired']}, Timestamp: {item['timestamp']}")


    list_exists = False
    for id in active_lists:
        if id == list_id:
            list_exists = True
        

    

    if not list_exists: # a lista ainda não existe - criá-la de raiz     

        active_lists.append(list_id)
        server_local_lists[list_id] = shopping_list_from_client

        # Save clients lists
        with open(db_dir + "/server_data/active_lists_file.txt", 'w') as file:
            for list_id in active_lists:
                file.write(list_id + '\n')

        response = "Your list haven't changed.\n"
        client_socket.send(response.encode())


    else: # a lista já existe, se tiver content tem de ser merged com o que vem do client

        # MERGE SHOPPING LIST REPLICAS
        server_local_lists[list_id] = server_local_lists[list_id].merge(shopping_list_from_client)

        # Print the updated/merged list in the server
        print("\n> MERGED LIST:")
        for item_id, item in server_local_lists[list_id].shopping_map.items():
            print(f" - Name: {item['name']}, Quantity: {item['quantity']}, Acquired: {item['acquired']}, Timestamp: {item['timestamp']}")


        # Create a response string containing the updated list and sync success message
        response = ""
        for item_id, item in server_local_lists[list_id].shopping_map.items():
            response += str(item_id) + ':' + str(item['name']) + ':' + str(item['quantity']) + ':' + str(item['acquired']) + ':' + str(item['timestamp']) + '\n'  
        response += "Syncronization done with success - Your list have changed.\n"

        # Send the updated list back to the client
        client_socket.send(response.encode())


    # Save shopping list in the database
    try:
        with open(db_dir + "/server_data/shopping_lists/" + list_id + '.txt', 'w') as file:
            for item_id, item in server_local_lists[list_id].shopping_map.items():
                file.write(str(item_id) + ':' + str(item['name']) + ':' + str(item['quantity']) + ':' + str(item['acquired']) + ':' + str(item['timestamp']) + '\n')
    except FileNotFoundError:
        pass
    
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