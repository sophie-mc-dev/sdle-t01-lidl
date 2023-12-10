import socket
import subprocess
import threading
import time
import hashlib

import psutil

from shared.utils import *

# List to store server processes
server_processes = []

server_startup_lock = threading.Lock()

# Function to start a new server
def start_server(port):
    server_cmd = ["python", "-m" "server.server.py", str(port)]  
    server_process = subprocess.Popen(server_cmd)
    return server_process

# List of server ports
server_ports = [8081, 8082, 8083]

for port in server_ports:
    server_process = start_server(port)
    server_processes.append(server_process)
    print("Started a new server in port", port)
    time.sleep(2)  # Allow some time for the server to start

# Create a socket object
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a port
sock.bind(("localhost", 9090))

# Listen for incoming connections
sock.listen(5)

# Function to calculate the hash of a shopping list ID
def hash_shopping_list_id(shopping_list_id):
    return int(hashlib.sha256(shopping_list_id.encode()).hexdigest(), 16) % (2**32)

def get_server_port(shopping_list_id):
    hashed_id = hash_shopping_list_id(shopping_list_id)
    return server_ports[hashed_id % len(server_ports)]

def handle_client(client_sock, client_addr):
    try:
        
        encoded_client_items = client_sock.recv(1024).decode().strip()
        print("Client Shopping List initial content: " + encoded_client_items)
        client_shoppint_list_items = encoded_client_items.split('\n')
    
        for line in client_shoppint_list_items:

            
            item_id, _, _, _, item_timestamp = line.split(':')

            
            list_id = item_timestamp
            print("list_id: ", list_id)



            # Calculate the average CPU usage across existing servers
            average_cpu_usage = sum(psutil.cpu_percent(percpu=True)[0] for _ in server_ports) / len(server_ports)
            print("Average CPU Usage:", average_cpu_usage)

            # Dynamically add a new server if the average CPU usage is above a threshold
            
            if (average_cpu_usage > 70):  # Adjust this threshold based on your requirements
                print("Adding a new server due to high CPU usage...")
                with server_startup_lock:
                    new_port = max(server_ports) + 1
                    server_ports.append(new_port)
                    server_process = start_server(new_port)
                    server_processes.append(server_process)
                    print("Started a new server in port", new_port)
                    time.sleep(1)  # Allow some time for the server to start 

            # Choose the server based on consistent hashing
            current_server_port = get_server_port(list_id)
            print("Forwarding to port", current_server_port)

            # Create a socket to connect to the chosen server
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Connecting to server in port", current_server_port)
            server_sock.connect(("localhost", current_server_port))

            

            server_sock.sendall(encoded_client_items.encode())

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
    client_handler = threading.Thread(target=handle_client, args=(client_sock, client_addr))
    client_handler.start()