import unittest
from shared.CRDT import *

class TestShoppingListMerge(unittest.TestCase):
    def setUp(self):
        # Create two instances of ShoppingList with the same ID
        self.shopping_list = ShoppingList()
        self.replica = ShoppingList()

        # Ensure both shopping lists have the same ID
        self.replica.id = self.shopping_list.id

    def test_merge_conflict_resolution(self):
        item_id = "item1" 

        # Modify shopping_list
        self.shopping_list.add_item(item_id, {"name": "Apple", "quantity": 8})
        self.shopping_list.update_acquired_status(item_id, True)  # Simulate acquired status change
        
        # Modify replica with conflicting changes
        self.replica.increment_quantity(item_id) # increment quantity to 9

        # Merge replica into shopping_list
        print("Before Merge - Quantity:", self.shopping_list.shopping_map[item_id]["quantity"])
        self.shopping_list.merge(self.replica)
        print("After Merge - Quantity:", self.shopping_list.shopping_map[item_id]["quantity"])

        # Assert the expected state of shopping_list after merge
        self.assertEqual(self.shopping_list.shopping_map[item_id]["quantity"], 9)
        self.assertEqual(self.shopping_list.shopping_map[item_id]["acquired"], True)

if __name__ == '__main__':
    unittest.main()
