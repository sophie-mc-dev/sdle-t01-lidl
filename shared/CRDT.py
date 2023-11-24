import uuid
import time
from .pncounter import PNCounter


class AWORMap:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.v = {self.id: 0}
        self.I = set()  # item, timestamp, shopping list
        self.quantity_counters = {}

    # returns shopping list ID
    def my_id(self):
        return self.id

    # contains
    def contains(self, item):
        return any((i, c, sl) for i, c, sl in self.I if i == item)

    # elements
    def elements(self):
        return {i for i, _, _ in self.I}

    # add item
    def add_item(self, item):
        list_id = self.my_id()
        timestamp = self.v[list_id] + 1
        self.effect(item, timestamp, list_id)

        if timestamp > self.v[list_id]:
            previous_state = {(i, timestamp_prime, list_id_prime) for i, timestamp_prime, list_id_prime in self.I if timestamp_prime < timestamp} 
            self.v[list_id] = timestamp
            self.I = (self.I | {(item, timestamp, list_id)}) - previous_state

    def effect(self, item, timestamp, shopping_list):
        self.I.add((item, timestamp, shopping_list))

    def remove_item(self, item):
        R = {(i, c, sl) for i, c, sl in self.I if i == item}
        self.effect(R)

        self.I -= R

    def compare(self, other):
        R = {(c, sl) for i, c, sl in self.I if 0 < c <= self.v[sl]}
        R_prime = {(c, sl) for i, c, sl in other.I if 0 < c <= other.v[sl]}
        return all(self.v[i] <= other.v[i] and R.issubset(R_prime) for i in range(len(self.v)))
    
    def merge(self, other):
        merge = self.I.intersection(other.I)

        merge_prime = {(i, c, sl) for i, c, sl in self.I - other.I if c > other.v[sl]}
        merge_double_prime = {(i, c, sl) for i, c, sl in other.I - self.I if c > self.v[sl]}

        union = merge.union(merge_prime, merge_double_prime)

        previous_state = {(i, c, sl) for i, c, sl in union if any((i, c_prime, sl) in union for c_prime in range(c))}

        self.I = union - previous_state
        self.v = [max(self.v[i], other.v[i]) for i in range(len(self.v))]

    


# Example usage:

# Example usage with interactive menu
shopping_map = AWORMap()

while True:
    print("\nMenu:")
    print("1. Add item")
    print("2. Remove item")
    print("3. Display items")
    print("4. Exit")

    choice = input("Enter your choice (1-4): ")

    if choice == "1":
        item_name = input("Enter item name to add: ")
        shopping_map.add_item(item_name)
        print("Item added successfully.")

    elif choice == "2":
        item_name = input("Enter item name to remove: ")
        shopping_map.remove_item(item_name)
        print("Item removed successfully.")

    elif choice == "3":
        print("List of items:")
        items = shopping_map.elements()
        if items:
            print(", ".join(items))
        else:
            print("No items in the list.")

    elif choice == "4":
        print("Exiting...")
        break

    else:
        print("Invalid choice. Please enter a valid option.")