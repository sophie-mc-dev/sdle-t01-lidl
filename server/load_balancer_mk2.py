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
server_ports = [8081, 8082, 8083]
current_server_index = 0

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a port
sock.bind(("localhost", 9090))

# Listen for incoming connections
sock.listen(5)

while True:
    # Accept an incoming connection
    client_sock, client_addr = sock.accept()
    print("Received connection from", client_addr)

    # Choose the next server in a round-robin fashion
    current_server_port = server_ports[current_server_index]
    print("Forwarding to port", current_server_port)
    current_server_index = (current_server_index + 1) % len(server_ports)

    # Check if the server process for the selected port is running
    if not any(p.poll() is None for p in server_processes):
        # If not running, start a new server process
        print("Starting a new server process...")
        server_process = start_server(current_server_port)
        server_processes.append(server_process)
        time.sleep(1)  # Allow some time for the server to start 

    # Create a socket to connect to the chosen server
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Connecting to server in port", current_server_port)
    server_sock.connect(("localhost", current_server_port))

    try:
        # Forward the connection
        server_sock.sendall(client_sock.recv(1024))
        print("Forwarded the connection to port", current_server_port)

        confirmation = server_sock.recv(1024).decode()

        if confirmation != "Ready":
            print("Server not ready. Closing connections.")
            # server_sock.close()
            # client_sock.close()
        else:
            print("Server is ready. Closing load balancer connection.")
            server_sock.close() # DONT REMOVE THIS
            client_sock.close()
    except Exception as e:
        print("Error forwarding connection:", e)

