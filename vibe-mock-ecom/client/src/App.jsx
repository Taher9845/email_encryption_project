import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch products from backend
  useEffect(() => {
    fetch("http://localhost:4000/api/products")
      .then((res) => res.json())
      .then((data) => {
        console.log("Fetched products:", data); // 🧠 debug log
        setProducts(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Fetch error:", err);
        setLoading(false);
      });
  }, []);

  const addToCart = (product) => {
    fetch("http://localhost:4000/api/cart", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ productId: product.id, qty: 1 }),
    });
    setCart((prev) => [...prev, product]);
  };

  const removeFromCart = (id) => {
    fetch(`http://localhost:4000/api/cart/${id}`, { method: "DELETE" });
    setCart((prev) => prev.filter((item) => item.id !== id));
  };

  const checkout = async () => {
    const res = await fetch("http://localhost:4000/api/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cartItems: cart }),
    });
    const data = await res.json();
    alert(`✅ Checkout complete! Total: $${data.total}`);
    setCart([]);
  };

  if (loading) return <h2>Loading...</h2>;

  return (
    <div className="app">
      <h1>🛒 Vibe Mock E-Com</h1>

      <h2>Products</h2>
      <div className="grid">
        {products.map((p) => (
          <div key={p.id} className="card">
            <h3>{p.name}</h3>
            <p>${p.price}</p>
            <button onClick={() => addToCart(p)}>Add to Cart</button>
          </div>
        ))}
      </div>

      <h2>Cart ({cart.length})</h2>
      {cart.length === 0 ? (
        <p>No items yet</p>
      ) : (
        <ul>
          {cart.map((c) => (
            <li key={c.id}>
              {c.name} - ${c.price}
              <button onClick={() => removeFromCart(c.id)}>❌</button>
            </li>
          ))}
        </ul>
      )}

      {cart.length > 0 && (
        <button onClick={checkout} className="checkout">
          Checkout
        </button>
      )}
    </div>
  );
}

export default App;
