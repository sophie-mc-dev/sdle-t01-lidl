import socket
import subprocess
import time

# List to store server processes
server_processes = []

# Function to start a new server
def start_server(port):
    server_cmd = ["python", "server.py", str(port)]  
    server_process = subprocess.Popen(server_cmd)
    return server_process

# List of server ports
server_ports = [8000, 8001, 8002]
current_server_index = 0

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a port
sock.bind(("localhost", 8080))

# Listen for incoming connections
sock.listen(5)

while True:
    # Accept an incoming connection
    client_sock, client_addr = sock.accept()
    print("Received connection from", client_addr)

    # Choose the next server in a round-robin fashion
    current_server_port = server_ports[current_server_index]
    current_server_index = (current_server_index + 1) % len(server_ports)

    # Check if the server process for the selected port is running
    if not any(p.poll() is None for p in server_processes):
        # If not running, start a new server process
        server_process = start_server(current_server_port)
        server_processes.append(server_process)
        time.sleep(1)  # Allow some time for the server to start

    # Create a socket to connect to the chosen server
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.connect(("localhost", current_server_port))

    # Forward the connection
    server_sock.sendall(client_sock.recv(1024))

    # Close the connection to the server
    server_sock.close()

    # Close the connection to the client
    client_sock.close()

