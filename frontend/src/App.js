import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Blank from "./Pages/Blank";
import ShoppingListItems from "./Pages/ShoppingListItems";
import AppLayout from "./Components/Layout/AppLayout";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route path="/shopping_list/id" element={<ShoppingListItems />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
