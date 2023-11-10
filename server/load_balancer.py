import heapq
import threading

class DynamicWeightedRoundRobinLoadBalancer:
    def __init__(self):
        self.servers = []  # Maintain a list of servers for reference
        self.server_index = 0
        self.lock = threading.Lock()  # Add a lock for thread safety

    def add_server(self, server):
        with self.lock:
            self.servers.append(server)  # Add server to the list

    def remove_server(self, server):
        with self.lock:
            self.servers.remove(server)  # Remove server from the list

    def get_next_server(self):
        with self.lock:
            if not self.servers:
                raise ValueError("No servers available")

            server = self.servers[self.server_index]
            self.server_index = (self.server_index + 1) % len(self.servers)
            return server

    def _get_server_load(self, server):
        # Simulate getting the current load for a server (replace with your logic)
        # For this example, let's use a random number as a placeholder
        return len(server) + hash(server) % 10
