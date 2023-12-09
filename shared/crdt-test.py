import unittest
from shared.CRDT import *

class TestShoppingListMerge(unittest.TestCase):
    def setUp(self):
        # Create two instances of ShoppingList with the same ID
        self.shopping_list = ShoppingList()
        self.shopping_list.add_item("item1", {"name": "Orange", "quantity": 3}) # Timestamp = 1

        # Create replica of shopping list
        self.replica = ShoppingList()
        # Ensure both shopping lists have the same ID
        self.replica.id = self.shopping_list.id
        for item_id, item_data in self.shopping_list.shopping_map.items():
            self.replica.add_item(item_id, item_data) # Timestamp = 1

       

    def test_merge_conflict_resolution(self):
        item_id = "item1" 

        # Modify shopping_list
        self.shopping_list.update_acquired_status(item_id, True)  # Simulate acquired status change, Timestamp = 2
        
        # Modify replica with conflicting changes
        self.replica.increment_quantity(item_id) # increment quantity to 4, Timestamp = 2        
        self.replica.increment_quantity(item_id) # increment quantity to 5, Timestamp = 3

        # Merge replica into shopping_list
        print("Before Merge: ", self.shopping_list.shopping_map)
        self.shopping_list.merge(self.replica)
        print("After Merge: ", self.shopping_list.shopping_map)

        # Assert the expected state of shopping_list after merge
        self.assertEqual(self.shopping_list.shopping_map[item_id]["quantity"], 5)
        self.assertEqual(self.shopping_list.shopping_map[item_id]["acquired"], False) 

if __name__ == '__main__':
    unittest.main()
