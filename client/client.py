import socket

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set the host and port
host = "localhost"
port = 5555

# Connect to the server
client_socket.connect((host, port))


while True:
    # Receive and print the server's message
    message = client_socket.recv(1024).decode()
    print(message)

    if message.endswith(":"): 
        key = (input())
        client_socket.send(key.encode())




# Close the client socket
client_socket.close()