from shared.CRDT import *

# Example usage:
shopping_lists = {}

# Instance of shopping list
shopping_list = ShoppingList()
shopping_list.name = "Groceries"
shopping_lists[shopping_list.id] = shopping_list

# Define item and add it to the list
item_id1 = str(uuid.uuid4())
item1 = {
    "name": "Milk",
    "quantity": int("2"),
    "acquired": False,
}
shopping_list.add_item(item_id1, item1)


# Get shopping list
def select_shopping_list():
    
    print("Select an option:")
    print("1. Select existing shopping list")
    print("2. Create new shopping list")
    print("3. Exit")
    
    option = input("Enter your choice (1-2): ")
    if option == "1":
        if shopping_lists:
            print("Existing Shopping Lists:")
            for id in shopping_lists.keys():
                print(f"Shopping List ID: {id}")
            
            selected_list_id = input("Enter Shopping List ID to select: ")
            if selected_list_id in shopping_lists:
                return selected_list_id
            else:
                print("Invalid Shopping List ID.")
                return None
        else:
            print("No existing shopping lists.")
            return None
    elif option == "2":
        new_list_id = token_urlsafe(16)
        username = "johndoe"
        name = input("Name your shopping list: ")
        shopping_lists[new_list_id] = ShoppingList(username)
        return new_list_id
    
    elif option == "3":
        return None 

    else:
        print("Invalid choice. Please enter a valid option.")


# Get shopping list ID
user_input_id = select_shopping_list()

if user_input_id:
    shopping_list = shopping_lists[user_input_id]
    print(shopping_list.get_shopping_list(user_input_id))
    
    while True:
        print("\nMenu:")
        print("1. Add item")
        print("2. Remove item")
        print("3. Increment quantity")
        print("4. Decrement quantity")
        print("5. Item acquired")
        print("6. Item not acquired")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ")

        print(shopping_list.get_shopping_list(user_input_id))

        if choice == "1":
            item={}
            item_id = str(uuid.uuid4())  
            item["name"] = input("Enter item name: ")
            item["quantity"] = input("Enter item quantity: ")

            shopping_list.add_item(item_id, item)
            print("Item added successfully.")
            print(shopping_list.get_shopping_list(user_input_id))

        elif choice == "2":
            item_to_remove = input("Enter ID of the item to remove: ")
            shopping_list.remove_item(item_to_remove)
            print("Item removed successfully.")
            print(shopping_list.get_shopping_list(user_input_id))

        if choice == "3":
            item_to_update = input("Enter ID of the item to update quantity: ")
            shopping_list.increment_quantity(item_to_update)
            print("Quantity incremented successfully.")
            print(shopping_list.get_shopping_list(user_input_id))

        elif choice == "4":
            item_to_update = input("Enter ID of the item to update quantity: ")
            shopping_list.decrement_quantity(item_to_update)
            print("Quantity decremented successfully.")
            print(shopping_list.get_shopping_list(user_input_id))

        elif choice == "5":
            item_to_update = input("Enter ID of the item to update status: ")
            shopping_list.update_acquired_status(item_to_update, True)
            print("Acquired status updated successfully.")
            print(shopping_list.get_shopping_list(user_input_id))

        elif choice == "6":
            item_to_update = input("Enter ID of the item to update status: ")
            shopping_list.update_acquired_status(item_to_update, False)
            print("Acquired status updated successfully.")
            print(shopping_list.get_shopping_list(user_input_id))

        elif choice == "7":
            break

        else:
            print("Invalid choice. Please enter a valid option.")
else:
    print("Invalid Shopping List ID.")