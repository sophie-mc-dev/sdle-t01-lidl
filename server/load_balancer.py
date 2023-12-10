import socket
import subprocess
import threading
import time

# List to store server processes
server_processes = []

server_startup_lock = threading.Lock()

# Function to start a new server
def start_server(port):
    server_cmd = ["python3", "-m" "server.server.py", str(port)]  
    server_process = subprocess.Popen(server_cmd)
    return server_process

# List of server ports
server_ports = [8081, 8082, 8083]
current_server_index = 0

for port in server_ports:
    server_process = start_server(port)
    server_processes.append(server_process)
    time.sleep(2)  # Allow some time for the server to start

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a port
sock.bind(("localhost", 9090))

# Listen for incoming connections
sock.listen(5)

def handle_client(client_sock, client_addr, current_server_index):
    try:
        # Choose the next server in a round-robin fashion
        current_server_port = server_ports[current_server_index]
        print("Forwarding to port", current_server_port)
        current_server_index = (current_server_index + 1) % len(server_ports)

        # Check if the server process for the selected port is running
        with server_startup_lock: # ensures that only one thread at a time can start a new server
            if not any(p.poll() is None for p in server_processes):
                # If not running, start a new server process
                print("Starting a new server process...")
                server_process = start_server(current_server_port)
                server_processes.append(server_process)
                time.sleep(2)  # Allow some time for the server to start

        # Create a socket to connect to the chosen server
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Connecting to server in port", current_server_port)
        server_sock.connect(("localhost", current_server_port))

        # Forward initial response from the server to the client
        user = server_sock.recv(1024)
        client_sock.sendall(user)
        print("username: ", user)

        message = server_sock.recv(1024)
        client_sock.sendall(message)
        print("Second message? ", message)

        # Forward messages from client to server and vice versa
        while True:
            data = client_sock.recv(1024)
            print("Client says: ", data)
            if not data:
                break
            server_sock.sendall(data)

            response = server_sock.recv(1024)
            print("Server responds with: ", response)
            if not response:
                break
            client_sock.sendall(response)

        print("Connection closed. Closing load balancer connection.")
        server_sock.close()
        client_sock.close()

    except Exception as e:
        print("Error forwarding connection:", e)

while True:
    # Accept an incoming connection from the client
    client_sock, client_addr = sock.accept()
    print("Received connection from", client_addr)

    # Handle each client in a separate thread
    client_handler = threading.Thread(target=handle_client, args=(client_sock, client_addr, current_server_index))
    client_handler.start()