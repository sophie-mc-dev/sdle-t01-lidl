import socket
import sys
from os.path import dirname, abspath
import time
from shared.utils import *
from shared.CRDT import *

parent_dir = dirname(dirname(abspath(__file__)))
sys.path.append(parent_dir)

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set the host and port
host = "localhost"
port = 5555


# choose a list ID to connect
print("Please enter listID: ")
list_id = input("ListID: ")


# Create ShoppingList object
shopping_list = ShoppingList()
shopping_list.set_id(list_id)
local_list[list_id] = shopping_list


def connect_to_server():
    try:
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Try to connect to the server
        client_socket.connect((host, port))
        #print("Connected to the server successfully!")
        return client_socket
    except Exception as e:
        # Handle connection errors
        print(f"Error connecting to the server: {e}")
        return None
    

while True:

    # Show user list content
    print("\n------------ MENU ------------")
    print("> [After server sync]")
    print_user_list(list_id)

    print("\nChoose one option:")
    print(" 1 - Modify Shopping List")
    print(" 0 - Exit")
    key = input("Option: ")
        

    if key == "1":
        print_user_list(list_id)

        print("Choose one option:")
        print(" 1 - Add item")
        print(" 2 - Delete item")
        print(" 3 - Increment quantity")
        print(" 4 - Decrement quantity")
        print(" 5 - Item acquired")
        print(" 6 - Item not acquired")
        print(" 0 - Exit")
        key = input("Option: ")

        if key == "1": 
            item={}
            item_id = str(uuid.uuid4())  
            item["name"] = input("> Enter item name: ")
            item["quantity"] = input("> Enter item quantity: ")

            try:
                item["quantity"] = int(item["quantity"])
                local_list[list_id].add_item(item_id, item)
                print("\nItem added successfully.")

                print("\n[Before merging with server list...]")
                print_user_list(list_id)

            except ValueError:
                print("Quantity must be an integer.")
    
        elif key == "2": 
            is_empty = True

            for item in local_list[list_id].shopping_map.items():
                is_empty = False
                print(item.__str__())

            if is_empty:
                print("\nYou have no items to delete.\n")
            else:
                item_to_remove = input("> Enter ID of the item to remove: ")
                local_list[list_id].remove_item(item_to_remove)
                print("\nItem removed successfully.")

                print("\n[Before merging with server list...]")
                print_user_list(list_id)
            
        elif key == "3":
            is_empty = True

            for item in local_list[list_id].shopping_map.items():
                is_empty = False
                print(item.__str__())

            if is_empty:
                print("\nYou have no items to increment.\n")
            else:
                item_to_increment = input("> Enter ID of the item to increment: ")
                local_list[list_id].increment_quantity(item_to_increment)
                print("\nItem quantity incremented successfully.")

                print("\n[Before merging with server list...]")
                print_user_list(list_id)

        elif key == "4":
            is_empty = True

            for item in local_list[list_id].shopping_map.items():
                is_empty = False
                print(item.__str__())

            if is_empty:
                print("\nYou have no items to decrement.\n")
            else:
                item_to_decrement = input("> Enter ID of the item to decrement: ")
                local_list[list_id].decrement_quantity(item_to_decrement)
                print("\nItem quantity decremented successfully.")

                print("\n[Before merging with server list...]")
                print_user_list(list_id)

        elif key == "5":
            is_empty = True

            for item in local_list[list_id].shopping_map.items():
                is_empty = False
                print(item.__str__())

            if is_empty:
                print("\nYou have no items to decrement.\n")
            else:
                item_to_update = input("> Enter ID of the item to update status: ")
                local_list[list_id].update_acquired_status(item_to_update, True)
                print("\nAcquired status updated successfully.")

                print("\n[Before merging with server list...]")
                print_user_list(list_id)

        elif key == "6":

            is_empty = True

            for item in local_list[list_id].shopping_map.items():
                is_empty = False
                print(item.__str__())

            if is_empty:
                print("\nYou have no items to decrement.\n")
            else:
                item_to_update = input("> Enter ID of the item to update status: ")
                local_list[list_id].update_acquired_status(item_to_update, False)
                print("\nAcquired status updated successfully.")

                print("\n[Before merging with server list...]")
                print_user_list(list_id) 

        elif key == "0":
            print("End of connection.\n")

    elif key == "0":
        print("End of connection.\n")
        


    # When you want to update things, connect to the server
    print("Trying connect to server now...")
    time.sleep(1)

    client_socket = connect_to_server()

    if client_socket is not None:

        # marosca para mandar o userID e a listID
        items_str = "list_id:to:send:is:" + list_id + '\n'
        
        for item_id, item in local_list[list_id].shopping_map.items():
            items_str += str(item_id) + ':' + str(item['name']) + ':' + str(item['quantity']) + ':' + str(item['acquired']) + ':' + str(item['timestamp']) + '\n'
        
        # send user id and user list content to server
        try:
            client_socket.send(items_str.encode())
        except Exception as e:
            # Handle sending data errors
            print(f"Error sending data to the server: {e}")

        
        # Receive new items list and update client list
        encoded_list_plus_message = client_socket.recv(1024).decode().strip()
        # Split the received data using '\n' as the separator and store it in a list
        list_plus_message = encoded_list_plus_message.split('\n')

        # separate items from syncronization output
        response = list_plus_message.pop()
        print(response)

        # merge happens, need to update client local shopping_list
        if 'Your list have changed' in response:

            # Add '\n' to the end of each element in the list
            items = list_plus_message
            # 'items' contains the items from local client union with server items

            # update client local shopping_list
            updated_shopping_list = ShoppingList()
            shopping_list.set_id(list_id)

            for line in items:
                try:
                    item_id, item_name, item_quantity, item_acquired, item_timestamp = line.split(':')

                    item = {
                        "name": item_name,
                        "quantity": item_quantity,
                        "acquired": item_acquired,
                        "timestamp": item_timestamp
                    }

                    updated_shopping_list.fill_with_item(item_id, item)

                except:
                    continue
    
            local_list[list_id] = updated_shopping_list
        
        else: # client shopping list is already updated
            pass


        # Close the connection to the server
        client_socket.close()
        print("Disconnected from the server.")

    # Continue working locally
