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

    if "Username" in message:
        username = input("Username: ")
        client_socket.send(username.encode())

    elif "Password" in message:
        password = input("Password: ")
        client_socket.send(password.encode())

    elif "Authentication successful" in message:
        authenticated = True

    else:
        print("Authentication failed. Please try again.")


# Continue with list management or other operations
while True:
    # Receive and print the server's message
    message = client_socket.recv(1024).decode()
    print(message)

    if message.endswith(":"):
        key = input()
        client_socket.send(key.encode())


# Close the client socket
client_socket.close()
