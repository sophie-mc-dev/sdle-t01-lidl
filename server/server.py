import socket
import threading
import signal
import sys
from os.path import dirname, abspath

parent_dir = dirname(dirname(abspath(__file__)))
sys.path.append(parent_dir)

from shared.operations import *
from shared.utils import *



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

    authenticated = False  # Track authentication status

    while not authenticated:

        # message = authentication||registration:username:password
        encoded_message = client_socket.recv(1024).decode().strip()

        # Split the received data using '\n' as the separator and store it in a list
        message = encoded_message.split(':')

        choice, username, password = message

        if choice == "authentication":
            if username in user_credentials and user_credentials[username] == password:
                authenticated = True
                to_send = "Authentication successful."
                client_socket.send(to_send.encode())
            else:
                client_socket.send("Authentication failed. Please try again.".encode())
        
        elif choice == "registration":
            registration_result = register_user(username, password)
            print(registration_result)
            client_socket.send(registration_result.encode())
            if ("Registration successful" in registration_result):
                authenticated = True
                user_list[username] = None 


    # Once authenticated, proceed with list management

    listed = False

    while not listed:

        if len(user_list) == 0:
            to_send = "No active shooping lists.\n"
            
            list_id = create_new_shopping_list(username) # create new shopping list 
            to_send = to_send + "Your list id is '" + list_id + "'."
            client_socket.send(to_send.encode())
            
        else:
            client_socket.send("There already are active shooping lists".encode())
            # client will choose a menu option
            option = client_socket.recv(1024).decode().strip()

            if option == "1":
                to_send = "Create new shopping list"
                list_id = create_new_shopping_list(username)  

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

                user_list[username] = available_lists[int(option) - 1]
                with open(db_dir + "/server_data/user_listsIDs.txt", 'w') as file:
                    for username, list_id in user_list.items():
                        file.write(f"{username}:{list_id}\n")

                to_send = "Your list id is '" + user_list[username] + "'."
                client_socket.send(to_send.encode())

                message = client_socket.recv(1024).decode() # needed just to messages logic work
                if is_file_empty(db_dir + "/server_data/shopping_lists/" + list_id + ".txt"):
                    client_socket.send("empty_list".encode())
                else:
                    # get content from list and send it to client
                    file_content = []
                    try:
                        with open(db_dir + "/server_data/shopping_lists/" + list_id + ".txt", 'r') as file:
                            for line in file:
                                file_content.append(line)
                        client_socket.send(",".join(file_content).encode())                    
                        
                    except FileNotFoundError:
                        pass

        listed = True
        
    print("User '", username, "' is associated with shopping list '", user_list[username], "'.")



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
            print(client_items)
                
            server_items = []
            try:
                with open(db_dir + "/server_data/shopping_lists/" + list_id + ".txt", 'r') as file:
                    for line in file:
                        server_items.append(line)
            except FileNotFoundError:
                pass

            # if server list is empty 
            if is_file_empty(db_dir + "/server_data/shopping_lists/" + list_id + ".txt") == True:

                # if client list has some content, write it to server list
                if len(client_items) != 0:
                    try:
                        with open(db_dir + "/server_data/shopping_lists/" + list_id + '.txt', 'w') as file:
                            for line in client_items:
                                file.write(line)
                    except FileNotFoundError:
                        pass

            elif client_items != server_items:
                items = list(set(client_items + server_items))
                client_items = items

                try:
                    with open(db_dir + "/server_data/shopping_lists/" + list_id + '.txt', 'w') as file:
                        for line in items:
                            file.write(line)
                except FileNotFoundError:
                    pass

            
            client_items.append("Syncronization done with success.\n")

            str_to_send = ""
            for elem in client_items:
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

