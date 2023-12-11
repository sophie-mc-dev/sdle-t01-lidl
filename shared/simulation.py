# import threading
# import time
# import random
from shared.CRDT import *  

# # Function to initialize the shopping list with some initial items
# def initialize_shopping_list(shopping_list):
#     # Add some initial items to the shopping list
#     for i in range(5):
#         shopping_list.add_item(f"Item-{i}", {"name": f"Item-{i}", "quantity": random.randint(1, 10)})

# # Function simulating user operations
# def simulate_user_actions(shopping_list, user_id):
#     # Simulate various operations on the shopping list by each user
#     for _ in range(3):  # Simulate multiple operations per user
#         if shopping_list.shopping_map:
#             operation = random.choice(["update_quantity", "change_acquired_status"])
            
#             if operation == "update_quantity":
#                 item_id = random.choice(list(shopping_list.shopping_map.keys()))
#                 new_quantity = random.randint(1, 10)  # Random quantity
#                 shopping_list.update_quantity(item_id, new_quantity)
#             elif operation == "change_acquired_status":
#                 item_id = random.choice(list(shopping_list.shopping_map.keys()))
#                 acquired_status = random.choice([True, False])  # Random acquired status
#                 shopping_list.update_acquired_status(item_id, acquired_status)
            
#             # Introduce a delay to simulate user actions taking time
#             time.sleep(random.uniform(0.5, 1.5))
#         else:
#             print("Shopping list is empty. Skipping operations.")

#     # Print the shopping list state after user operations
#     print(f"User {user_id} updated shopping list:")
#     print("SHOPPING LIST: ", shopping_list.get_shopping_list(shopping_list.my_id()))

# def run_concurrent_updates():
#     # Create an instance of ShoppingList
#     shopping_list = ShoppingList()

#     # Initialize the shopping list with initial items
#     initialize_shopping_list(shopping_list)

#     # Define the number of concurrent users (threads)
#     num_users = 3

#     # Create threads representing users performing operations concurrently
#     threads = []
#     for i in range(num_users):
#         thread = threading.Thread(target=simulate_user_actions, args=(shopping_list, i))
#         threads.append(thread)

#     # Start threads
#     for thread in threads:
#         thread.start()

#     # Wait for all threads to finish
#     for thread in threads:
#         thread.join()

#     # After all threads finish, print the final state of the shopping list
#     print("\nFinal state of the shopping list after concurrent updates:")
#     print(shopping_list.get_shopping_list(shopping_list.my_id()))

# # Run concurrent updates simulation
# run_concurrent_updates()

import threading
import time

# Function simulating user operations
def simulate_user_actions(shopping_list, user_id):
    # Simulate User 1 and User 2 updating the quantity of the same item concurrently
    item_id = 'item_id_to_update'  # Replace 'item_id_to_update' with the actual ID of the item to be updated

    # Simulate User 1 changing the quantity
    if user_id == 1:
        for _ in range(5):
            # Perform operations (e.g., increment quantity)
            shopping_list.increment_quantity(item_id) 
            shopping_list.increment_quantity(item_id)
            shopping_list.increment_quantity(item_id) # (13)
            time.sleep(0.1)  # Introduce a delay to simulate processing time

    # Simulate User 2 changing the quantity
    elif user_id == 2:
        for _ in range(5):
            # Perform operations (e.g., decrement quantity)
            shopping_list.decrement_quantity(item_id) # -1
            shopping_list.increment_quantity(item_id) # +1
            shopping_list.increment_quantity(item_id) # +1 (11)
            time.sleep(0.1)  # Introduce a delay to simulate processing time

def run_concurrent_updates():
    shopping_list = ShoppingList()

    # Perform an initial addition of an item to the shopping list
    initial_item = {"name": "Sample Item", "quantity": 10}
    shopping_list.add_item('item_id_to_update', initial_item)

    num_users = 2  # Simulate two users concurrently updating the same item

    # Create threads representing users performing operations concurrently
    threads = []
    for i in range(1, num_users + 1):
        thread = threading.Thread(target=simulate_user_actions, args=(shopping_list, i))
        threads.append(thread)

    # Start threads
    for thread in threads:
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # After all threads finish, print the final state of the shopping list
    print("\nFinal state of the shopping list after concurrent updates:")
    print(shopping_list.get_shopping_list(shopping_list.my_id()))

# Run concurrent updates simulation
run_concurrent_updates()
