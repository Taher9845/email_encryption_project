import express from "express";
import cors from "cors";

const app = express();
app.use(cors());
app.use(express.json());

const products = [
  { id: 1, name: "iPhone 15 Pro", price: 1299 },
  { id: 2, name: "AirPods Pro", price: 249 },
  { id: 3, name: "MacBook Air", price: 999 },
  { id: 4, name: "Apple Watch", price: 399 },
  { id: 5, name: "iPad Pro", price: 1099 }
];

let cart = [];

app.get("/api/products", (req, res) => {
  res.json(products);
});

app.get("/api/cart", (req, res) => {
  const total = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
  res.json({ items: cart, total });
});

app.post("/api/cart", (req, res) => {
  const { productId, qty } = req.body;
  const product = products.find((p) => p.id === productId);
  if (!product) return res.status(404).json({ message: "Product not found" });

  const existing = cart.find((i) => i.id === productId);
  if (existing) existing.qty += qty;
  else cart.push({ ...product, qty });

  res.json(cart);
});

app.delete("/api/cart/:id", (req, res) => {
  const id = parseInt(req.params.id);
  cart = cart.filter((i) => i.id !== id);
  res.json(cart);
});

app.post("/api/checkout", (req, res) => {
  const total = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
  const receipt = { total, timestamp: new Date().toISOString() };
  cart = [];
  res.json(receipt);
});

app.listen(4000, () =>
  console.log("✅ Server running on http://localhost:4000")
);
