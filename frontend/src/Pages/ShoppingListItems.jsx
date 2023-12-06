
import { useState } from "react";
import "./items.css";

const ShoppingListItems = () => {
  const initialItems = [
    { name: "Apples", quantity: 2 },
    { name: "Milk", quantity: 1 },
    { name: "Bread", quantity: 1 },
    // Add more items as needed
  ];

  const [items, setItems] = useState(initialItems);
  const [acquiredItems, setAcquiredItems] = useState({});

  const handleCheckboxChange = (itemName) => {
    setAcquiredItems((prevItems) => ({
      ...prevItems,
      [itemName]: !prevItems[itemName],
    }));
  };

  const incrementQuantity = (index) => {
    const updatedItems = [...items];
    updatedItems[index].quantity += 1;
    setItems(updatedItems);
  };

  const decrementQuantity = (index) => {
    const updatedItems = [...items];
    if (updatedItems[index].quantity > 0) {
      updatedItems[index].quantity -= 1;
      setItems(updatedItems);
    }
  };

  const addItem = () => {
    const newItem = { name: "New Item", quantity: 1 };
    setItems((prevItems) => [...prevItems, newItem]);
  };

  const deleteItem = (index) => {
    const updatedItems = [...items];
    updatedItems.splice(index, 1);
    setItems(updatedItems);
  };

  return (
    <div className="shopping-list-items">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Quantity</th>
            <th>Acquired</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, index) => (
            <tr key={index}>
              

              <td>{item.name}</td>
              <td>
                <div className="quantity-controls">
                  <button onClick={() => decrementQuantity(index)}>-</button>
                  <span>{item.quantity}</span>
                  <button onClick={() => incrementQuantity(index)}>+</button>
                </div>
              </td>
              <td>
                <label>
                  <input
                    type="checkbox"
                    checked={acquiredItems[item.name] || false}
                    onChange={() => handleCheckboxChange(item.name)}
                  />
                </label>
              </td>
              <td>
                {items.length > 0 && (
                  <button
                    onClick={() => deleteItem(items.length - 1)}
                    className="delete-item-button"
                  >
                    Delete Last Item
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="item-buttons">
        <button onClick={addItem} className="add-item-button">
          Add Item
        </button>
      </div>
    </div>
  );
};

export default ShoppingListItems;
