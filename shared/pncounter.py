from .gcounter import GCounter

class PNCounter:
    def __init__(self, id):
        self.P = GCounter(id)
        self.N = GCounter(id)
        self.id = id

    def add_new_node(self, key):
        self.P.add_new_node(key)
        self.N.add_new_node(key)

    def inc(self, key):
        self.P.inc(key)

    def dec(self, key):
        self.N.inc(key)

    def query(self):
        return self.P.query() - self.N.query()

    def compare(self, pnc2):
        return self.P.compare(pnc2.P) and self.N.compare(pnc2.N)

    def merge(self, pnc2):
        self.P.merge(pnc2.P)
        self.N.merge(pnc2.N)

    def display(self, name):
        # Display object P
        print("{}.P: ".format(name), end="")
        self.P.display()

        # Display object N
        print("{}.N: ".format(name), end="")
        self.N.display()