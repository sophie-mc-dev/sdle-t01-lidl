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
                to_send = "Authentication successful. You can now access your list.\nYour username is '" + username + "'"
                client_socket.send(to_send.encode())
            else:
                client_socket.send("Authentication failed. Please try again.".encode())
        
        elif choice == "2":
            client_socket.send("Choose a Username:".encode())
            new_username = client_socket.recv(1024).decode().strip()

            client_socket.send("Choose a Password:".encode())
            new_password = client_socket.recv(1024).decode().strip()

            registration_result = register_user(new_username, new_password)
            to_send = registration_result + "\nYour username is '" + new_username + "'"
            client_socket.send(to_send.encode())
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
            to_send = "No active shooping lists.\n"
            
            list_id = create_new_shopping_list(username) # create new shopping list 
            to_send = to_send + "Your list id is '" + list_id + "'."
            client_socket.send(to_send.encode())
            
            #print_user_list()

        else:
            client_socket.send("There already are active shooping lists".encode())
            # client will choose a menu option
            option = client_socket.recv(1024).decode().strip()

            if option == "1":
                to_send = "Create new shopping list"
                list_id = create_new_shopping_list(username)  

                to_send = to_send + "Your list id is '" + list_id + "'."
                client_socket.send(to_send.encode())

                #print_user_list()

            elif option == "2":                
                to_send = "\nChoose one list ID:\n"

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

                to_send = "Your list id is '" + user_list[username] + "'."
                client_socket.send(to_send.encode())

                #print_user_list()


        listed = True
        
    
    print("User '", username, "' is associated with shopping list '", user_list[username], "'.")


    while True:
        client_socket.send("Show menu.\n".encode())
        key = client_socket.recv(1024).decode().strip()

        if not key:
            print("Client disconnected unexpectedly.")
            break

        elif key == "4": # later implement CRDTs here
            # for now, only substitute the server client's shopping list with the union of his personal list and the server list

            encoded_client_items = client_socket.recv(1024).decode().strip()

            # Split the received data using '\n' as the separator and store it in a list
            client_items_not_treated = encoded_client_items.split('\n')
            # Add '\n' to the end of each element in the list
            client_items = [item + '\n' for item in client_items_not_treated]
                

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

                    # client shopping list was not modified
                    client_items.append("Syncronization done with success. Your list does not change.\n")

                else: 
                    # client shopping list has no items
                    client_items.append("Syncronization attempt, but there's no content to update.\n".encode()) 

            elif client_items != server_items:
                items = list(set(client_items + server_items))

                # write to both lists
                if len(client_items) < len(server_items): 
                    client_items.append("Syncronization done with success. Your list have changed.\n")
                else:
                    client_items.append("Syncronization done with success. Server list have changed.\n")

                try:
                    with open(db_dir + "/server_data/shopping_lists/" + list_id + '.txt', 'w') as file:
                        for line in items:
                            file.write(line)
                except FileNotFoundError:
                    pass

            else: # client_items == server_items:
                client_items.append("The server is already syncronized with your list.\n")

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

    try:


        # Pass the client socket to the chosen server for handling
        handle_client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        handle_client_thread.start()

    except ValueError as e:
        print("No servers available. Handle this case appropriately.")
