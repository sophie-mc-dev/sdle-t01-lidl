import socket

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set the host and port
host = "localhost"
port = 5555

# Connect to the server
client_socket.connect((host, port))

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



listed = False

while not listed:
    message = client_socket.recv(1024).decode()

    if "1 - Create a new shopping list" in message:
        print(message)
        option = input("Option: ")
        client_socket.send(option.encode())

        message = client_socket.recv(1024).decode()

        if "Please choose one of the list IDs:" in message:
            print(message)
            list_id = input("List ID: ")
            client_socket.send(list_id.encode())

    else: # message = Let's create a new shopping list ... 
        print("There are no active shooping lists. Let's create one for you.")
        print(message)
        list_id = input("List ID: ")
        client_socket.send(list_id.encode())


    listed = True
    


# Continue with list management or other operations
while True:
    # Receive and print the server's message
    message = client_socket.recv(1024).decode()
    print(message)

    if message.endswith(":"):
        key = input()
        client_socket.send(key.encode())
    elif "End of connection." in message:
        break


# Close the client socket
client_socket.close()
