import threading

class DynamicWeightedRoundRobinLoadBalancer:
    def __init__(self):
        self.servers = []  # Maintain a list of servers for reference
        self.serverUsers = []
        self.server_index = 0
        self.lock = threading.Lock()  # Add a lock for thread safety

    def add_server(self, server):
        with self.lock:
            self.servers.append(server)  # Add server to the list

    def remove_server(self, server):
        with self.lock:
            self.servers.remove(server)  # Remove server from the list

    def add_user(self):
        with self.lock:
            self.serverUsers[(self.server_index) % len(self.servers)] += 1
    def remove_user(self, index):
        with self.lock:
            self.serverUsers[(self.server_index) % len(self.servers)] -= 1

    def get_next_server(self):
        with self.lock:
            if not self.servers:
                raise ValueError("No servers available")

            server = self.servers[self.server_index]
            self.server_index = (self.server_index + 1) % len(self.servers)
            return server
