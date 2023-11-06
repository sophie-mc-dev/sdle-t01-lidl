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
            to_send = "There are no active shooping lists. Let's create one for you. \n"
            
            list_id = create_new_shopping_list(username) # create new shopping list 
            to_send = to_send + "Your list id is '" + list_id + "'."
            client_socket.send(to_send.encode())
            
            #print_user_list()

        else:
            client_socket.send("\n1 - Create a new shopping list \n2 - Connect to an existent shopping list".encode())
            option = client_socket.recv(1024).decode().strip()

            if option == "1":
                to_send = "Let's create a new shopping list. \n"
                list_id = create_new_shopping_list(username) # create new shopping list 

                to_send = to_send + "Your list id is '" + list_id + "'."
                client_socket.send(to_send.encode())

                #print_user_list()

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

                to_send = "Your list id is '" + user_list[username] + "'."
                client_socket.send(to_send.encode())

                #print_user_list()


        listed = True
        
    
    print("User '", username, "' is associated with shopping list '", user_list[username], "'.")


    while True:
        client_socket.send("\nPress 1 to see list, 2 to add element, 3 to delete element, 4 to server syncronization or 0 to exit:".encode())
        key = client_socket.recv(1024).decode().strip()

        if not key:
            print("Client disconnected unexpectedly.")
            break

        if key == "1":
            # ----- This prints on the server terminal
            file_path = db_dir + "/server_data/shopping_lists/" + user_list[username] + ".txt"
            if is_file_empty(file_path) == True:
                print("Your shopping list is empty in server. Syncronize it.")
            else:
                items = []
                try:
                    with open(db_dir + "/server_data/shopping_lists/" + list_id + ".txt", 'r') as file:
                        for line in file:
                            name, quantity, acquired = line.strip().split(':')
                            string = "[Name: " + name + ", Quantity: " + quantity + ", Acquired: " + acquired + "]"
                            items.append(string)
                except FileNotFoundError:
                    pass
                print("\nYour shopping list in server has the items:")
                print("\n".join(items))
            # ------
            

            file_path = db_dir + "/client_data/clients_lists/" + username + ".txt"
            if is_file_empty(file_path) == True:
                client_socket.send("Your shopping list is empty. Try to add some items to your list.".encode())
            else:
                items = []
                try:
                    with open(db_dir + "/client_data/clients_lists/" + username + ".txt", 'r') as file:
                        for line in file:
                            name, quantity, acquired = line.strip().split(':')
                            string = "[Name: " + name + ", Quantity: " + quantity + ", Acquired: " + acquired + "]"
                            items.append(string)
                except FileNotFoundError:
                    pass
                client_socket.send("\n".join(items).encode())

        elif key == "2":
            client_socket.send("Add Item".encode())
        
        elif key == "3":
            client_socket.send("Delete Item".encode())

        elif key == "4": # later implement CRDTs here

            # for now, only substitute the server client's shopping list with the union of his personal list and the server list

            client_items = []
            try:
                with open(db_dir + "/client_data/clients_lists/" + username + ".txt", 'r') as file:
                    for line in file:
                        client_items.append(line)
            except FileNotFoundError:
                pass

            server_items = []
            try:
                with open(db_dir + "/server_data/shopping_lists/" + list_id + ".txt", 'r') as file:
                    for line in file:
                        server_items.append(line)
            except FileNotFoundError:
                pass

            
            # if server list is empty 
            if is_file_empty(db_dir + "/server_data/shopping_lists/" + list_id + ".txt") == True:

                # only write to sever list
                items = []
                try:
                    with open(db_dir + "/client_data/clients_lists/" + username + ".txt", 'r') as file:
                        for line in file:
                            items.append(line)
                except FileNotFoundError:
                    pass
                # if client list has some content, write it to server list
                if len(items) != 0:
                    try:
                        with open(db_dir + "/server_data/shopping_lists/" + list_id + '.txt', 'w') as file:
                            for line in items:
                                file.write(line)
                    except FileNotFoundError:
                        pass

                    client_socket.send("Syncronization done with success. Your list does not change.\n".encode()) 
                else: 
                    client_socket.send("Syncronization done with success. No content need update.\n".encode()) 


            elif client_items != server_items:
            
                items = list(set(client_items + server_items))

                # write to both lists
                try:
                    with open(db_dir + "/client_data/clients_lists/" + username + '.txt', 'w') as file:
                        for line in items:
                            file.write(line)
                except FileNotFoundError:
                    pass

                try:
                    with open(db_dir + "/server_data/shopping_lists/" + list_id + '.txt', 'w') as file:
                        for line in items:
                            file.write(line)
                except FileNotFoundError:
                    pass

                client_socket.send("Syncronization done with success.\n".encode()) 

            else: # client_items == server_items:
                client_socket.send("The server is already syncronized with your list.\n".encode()) 




            # ----- This prints on the server terminal
            print("Syncronization done with success.")

            file_path = db_dir + "/server_data/shopping_lists/" + user_list[username] + ".txt"
            if is_file_empty(file_path) == True:
                print("Your shopping list is empty in server.")
            else:
                items = []
                try:
                    with open(db_dir + "/server_data/shopping_lists/" + list_id + ".txt", 'r') as file:
                        for line in file:
                            name, quantity, acquired = line.strip().split(':')
                            string = "[Name: " + name + ", Quantity: " + quantity + ", Acquired: " + acquired + "]"
                            items.append(string)
                except FileNotFoundError:
                    pass
                print("Your shopping list in server has the items:\n")
                print("\n".join(items))
            # ------            


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

