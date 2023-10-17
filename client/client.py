import socket

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set the host and port
host = "localhost"
port = 5555

# Connect to the server
client_socket.connect((host, port))

# Send a key to the server
key = "get_list"
client_socket.send(key.encode())

# Receive the list items from the server
items = client_socket.recv(1024).decode()
print("Items received from the server:")
print(items)

# Close the client socket
client_socket.close()