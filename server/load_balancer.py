import heapq

class DynamicWeightedRoundRobinLoadBalancer:
    def __init__(self):
        self.servers = []
        self.heap = []

    def add_server(self, server):
        self.servers.append(server)  # Add server to the list
        heapq.heappush(self.heap, (0, server))  # (load, server)

    def remove_server(self, server):
        self.servers.remove(server)
        self.heap = [(load, s) for load, s in self.heap if s != server]
        heapq.heapify(self.heap)

    def get_next_server(self):
        if not self.servers:
            raise ValueError("No servers available")

        _, server = heapq.heappop(self.heap)
        load = self._get_server_load(server)
        heapq.heappush(self.heap, (load + 1, server))  # Increase load for the next cycle
        return server

    def _get_server_load(self, server):
        # Simulate getting the current load for a server (replace with your logic)
        # For this example, let's use a random number as a placeholder
        return len(server) + hash(server) % 10
