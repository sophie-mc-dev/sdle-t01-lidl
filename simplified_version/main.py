from operations import *

# Example usage
list_id = create_shopping_list()
add_item_to_list(list_id, "Milk", 2)
add_item_to_list(list_id, "Eggs", 1)

# Print the list with meaningful representation
for item in local_lists[list_id].items:
    print(item)