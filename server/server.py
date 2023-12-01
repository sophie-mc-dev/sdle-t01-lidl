import socket
import threading
import signal
import sys
import uuid
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

    # Create a random user id to identify the client
    user_id = "userid1"
    client_socket.send(user_id.encode())

    listed = False

    while not listed:

        if len(user_list) == 0:
            to_send = "No active shooping lists.\n"

            # Create ShoppingList object
            shopping_list = ShoppingList()
            list_id = shopping_list.my_id()
            shopping_list.associate_user(user_id) # User is stored in the shopping list's self.Users 
            user_list[user_id] = list_id

            # Save clients lists
            with open(db_dir + "/server_data/user_listsIDs.txt", 'w') as file:
                for user_id, lists_IDs in user_list.items():
                    file.write(f"{user_id}:{lists_IDs}\n")

            client_list[list_id] = shopping_list

            to_send = to_send + "Your list id is '" + list_id + "'."
            client_socket.send(to_send.encode())
            
        else:
            client_socket.send("There already are active shooping lists".encode())
            # client will choose a menu option
            option = client_socket.recv(1024).decode().strip()

            if option == "1":
                to_send = "Create new shopping list"

                 # Create ShoppingList object
                shopping_list = ShoppingList()
                list_id = shopping_list.my_id()
                user_list[user_id] = list_id

                to_send = to_send + "Your list id is '" + list_id + "'."
                client_socket.send(to_send.encode()) 

            elif option == "2":                
                to_send = "\nChoose one list ID:\n"

                # get all the lists available
                available_lists = []
                for user_name, lists_IDs in user_list.items():
                    try:
                        lists_IDs = lists_IDs.strip().split(',')
                        for listID in lists_IDs:
                            available_lists.append(listID)
                    except:
                        available_lists.append(lists_IDs)

                available_lists = list(set(available_lists))

                idx = 1
                for list_id in available_lists:
                    to_send += str(idx) + " - " + str(list_id) + "\n"
                    idx = idx + 1

                client_socket.send(to_send.encode())
                option = client_socket.recv(1024).decode().strip()

                user_list[user_id] = available_lists[int(option) - 1]
                with open(db_dir + "/server_data/user_listsIDs.txt", 'w') as file:
                    for user_id, list_id in user_list.items():
                        file.write(f"{user_id}:{list_id}\n")

                list_id = user_list[user_id]

                to_send = "Your list id is '" + list_id + "'."
                client_socket.send(to_send.encode())

                message = client_socket.recv(1024).decode() # needed just to messages logic work
                if client_list[list_id].is_empty():
                    client_socket.send("empty_list".encode())
                else:
                    server_items = []
                    for item in client_list[list_id].shopping_map.items():
                        item_str = item.name + ':' + str(item.quantity) + ':' + str(item.acquired)
                        server_items.append(item_str)
                    # 'server_items' contains the server items

                    client_socket.send('\n'.join(server_items).encode())                    
                        

        listed = True
        
    print("User '", user_id, "' is associated with shopping list '", list_id, "'.")



    while True:
        client_socket.send("Show menu.\n".encode())


        # for now, only substitute the server client's shopping list with the union of his personal list and the server list
        # Later implement CRDTs here


        encoded_client_items = client_socket.recv(1024).decode().strip()
        
        if "noContent" in encoded_client_items:
            client_socket.send("No sync".encode())
        
        else: # syncronize lists

            # Split the received data using '\n' as the separator and store it in a list
            client_items_not_treated = encoded_client_items.split('\n')
            # Add '\n' to the end of each element in the list
            client_items = [item + '\n' for item in client_items_not_treated]
            # 'client_items' contains the local client items
                
            server_items = []
            for item in client_list[list_id].shopping_map.items():
                item_str = item.name + ':' + str(item.quantity) + ':' + str(item.acquired) + '\n'
                server_items.append(item_str)
            # 'server_items' contains the server items
            
            # 'all_items' contains the local client items union with server items
            all_items = list(set(client_items + server_items))

            client_list[list_id] = ShoppingList() # clears server shopping list
            for item in all_items:
                item_name, quantity, acquired = item.strip().split(':')
                client_list[list_id].add_item(item_name, quantity, acquired)

            print("\n=>> what is now in server list '" + list_id + "':")
            for item in client_list[list_id].shopping_map.items():
                print(item.__str__())
            print("-------------------------\n")

            
            all_items.append("Syncronization done with success.\n")

            str_to_send = ""
            for elem in all_items:
                str_to_send += elem

            # send new items and message output to client
            client_socket.send(str_to_send.encode())

    
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