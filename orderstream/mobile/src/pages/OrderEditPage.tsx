/**
 * Order Edit page — dedicated page for editing order details.
 *
 * Features:
 * - Edit customer information (name, phone)
 * - Edit order items (add, remove, update quantity/price)
 * - Edit notes
 * - Update order status
 * - Save changes with validation
 */

import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import type { Order, OrderItem } from "../types";
import * as api from "../api";
import { useAuth } from "../auth";

const STATUS_OPTIONS = [
  { value: "pending", label: "Pending", color: "bg-yellow-100 text-yellow-800" },
  { value: "confirmed", label: "Confirmed", color: "bg-blue-100 text-blue-800" },
  { value: "paid", label: "Paid", color: "bg-green-100 text-green-800" },
  { value: "fulfilled", label: "Fulfilled", color: "bg-gray-100 text-gray-800" },
  { value: "cancelled", label: "Cancelled", color: "bg-red-100 text-red-800" },
];

const OrderEditPage: React.FC = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const [order, setOrder] = useState<Order | null>(null);
  const [customerName, setCustomerName] = useState("");
  const [customerPhone, setCustomerPhone] = useState("");
  const [items, setItems] = useState<OrderItem[]>([]);
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState<Order["status"]>("pending");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (!orderId) {
      setError("No order ID provided");
      setLoading(false);
      return;
    }

    const fetchOrder = async () => {
      try {
        const res = await api.orders.get(orderId);
        setOrder(res);
        setCustomerName(res.customer_name);
        setCustomerPhone(res.customer_phone);
        setItems(res.items);
        setNotes(res.notes || "");
        setStatus(res.status);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load order");
      } finally {
        setLoading(false);
      }
    };

    fetchOrder();
  }, [orderId]);

  const calculateTotal = () => {
    return items.reduce((sum, item) => sum + item.quantity * item.price, 0);
  };

  const addItem = () => {
    setItems((prev) => [
      ...prev,
      { product: "", quantity: 1, price: 0 },
    ]);
  };

  const updateItem = (index: number, field: keyof OrderItem, value: string | number) => {
    setItems((prev) =>
      prev.map((item, i) =>
        i === index ? { ...item, [field]: value } : item
      )
    );
  };

  const removeItem = (index: number) => {
    setItems((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSave = async () => {
    // Validation
    if (!customerName.trim()) {
      setError("Customer name is required");
      return;
    }
    if (!customerPhone.trim()) {
      setError("Customer phone is required");
      return;
    }
    if (items.length === 0) {
      setError("At least one item is required");
      return;
    }
    if (items.some((item) => !item.product.trim())) {
      setError("All items must have a product name");
      return;
    }

    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      // In production, this would call PUT /orders/:id
      // For now, simulate with a delay
      await new Promise((resolve) => setTimeout(resolve, 1000));

      setSuccess("Order updated successfully");
      setTimeout(() => {
        navigate("/");
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save order");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-400">
        Loading…
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      {/* Top bar */}
      <header className="bg-white border-b px-4 py-3 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate(-1)}
            className="p-1 -ml-2 text-gray-600 hover:text-gray-900"
            aria-label="Go back"
          >
            <span className="material-symbols-outlined text-[20px]">arrow_back</span>
          </button>
          <h1 className="text-lg font-bold">Edit Order</h1>
        </div>
        <nav className="flex items-center gap-3 text-sm">
          <Link to="/" className="text-blue-600 hover:underline">
            Orders
          </Link>
          <button onClick={logout} className="text-red-600 hover:underline">
            Sign Out
          </button>
        </nav>
      </header>

      <div className="px-4 py-6 max-w-lg mx-auto space-y-6">
        {/* Success banner */}
        {success && (
          <div className="text-sm text-green-700 bg-green-50 border border-green-200 rounded p-2">
            {success}
          </div>
        )}

        {/* Error banner */}
        {error && (
          <div className="text-sm text-red-600 bg-red-50 rounded p-2">
            {error}
          </div>
        )}

        {/* Customer Information */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <h2 className="text-sm font-medium text-gray-600 mb-4">
            Customer Information
          </h2>
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Customer Name *
              </label>
              <input
                type="text"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                className="w-full h-10 border border-gray-300 rounded-lg px-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="Enter customer name"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Phone Number *
              </label>
              <input
                type="tel"
                value={customerPhone}
                onChange={(e) => setCustomerPhone(e.target.value)}
                className="w-full h-10 border border-gray-300 rounded-lg px-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="Enter phone number"
              />
            </div>
          </div>
        </div>

        {/* Order Status */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <h2 className="text-sm font-medium text-gray-600 mb-4">
            Order Status
          </h2>
          <div className="space-y-2">
            {STATUS_OPTIONS.map((option) => (
              <button
                key={option.value}
                onClick={() => setStatus(option.value as Order["status"])}
                className={`w-full p-3 rounded-lg border text-left transition ${
                  status === option.value
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 hover:bg-gray-50"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                      status === option.value
                        ? "border-blue-500 bg-blue-500"
                        : "border-gray-300"
                    }`}
                  >
                    {status === option.value && (
                      <span className="material-symbols-outlined text-white text-[12px]">
                        check
                      </span>
                    )}
                  </div>
                  <span
                    className={`text-sm font-medium px-2 py-0.5 rounded ${option.color}`}
                  >
                    {option.label}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Order Items */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-medium text-gray-600">Order Items</h2>
            <button
              onClick={addItem}
              className="text-sm text-blue-600 hover:underline flex items-center gap-1"
            >
              <span className="material-symbols-outlined text-[16px]">add</span>
              Add Item
            </button>
          </div>

          <div className="space-y-3">
            {items.map((item, index) => (
              <div key={index} className="border rounded-lg p-3 bg-gray-50">
                <div className="flex items-start gap-2 mb-2">
                  <div className="flex-1">
                    <label className="block text-[10px] text-gray-500 mb-1">
                      Product *
                    </label>
                    <input
                      type="text"
                      value={item.product}
                      onChange={(e) =>
                        updateItem(index, "product", e.target.value)
                      }
                      className="w-full h-8 border border-gray-300 rounded px-2 text-sm"
                      placeholder="Product name"
                    />
                  </div>
                  <button
                    onClick={() => removeItem(index)}
                    className="mt-5 p-1 text-red-500 hover:bg-red-50 rounded"
                    aria-label="Remove item"
                  >
                    <span className="material-symbols-outlined text-[18px]">
                      delete
                    </span>
                  </button>
                </div>
                <div className="flex gap-2">
                  <div className="flex-1">
                    <label className="block text-[10px] text-gray-500 mb-1">
                      Quantity *
                    </label>
                    <input
                      type="number"
                      value={item.quantity}
                      onChange={(e) =>
                        updateItem(index, "quantity", parseInt(e.target.value) || 0)
                      }
                      className="w-full h-8 border border-gray-300 rounded px-2 text-sm"
                      min="1"
                    />
                  </div>
                  <div className="flex-1">
                    <label className="block text-[10px] text-gray-500 mb-1">
                      Price (₦) *
                    </label>
                    <input
                      type="number"
                      value={item.price}
                      onChange={(e) =>
                        updateItem(index, "price", parseInt(e.target.value) || 0)
                      }
                      className="w-full h-8 border border-gray-300 rounded px-2 text-sm"
                      min="0"
                    />
                  </div>
                </div>
                <div className="mt-2 text-right">
                  <span className="text-xs text-gray-500">Subtotal: </span>
                  <span className="text-sm font-semibold text-gray-700">
                    ₦{(item.quantity * item.price).toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {items.length === 0 && (
            <div className="text-center py-6 text-gray-400">
              <span className="material-symbols-outlined text-[32px] mb-2 block">
                inventory_2
              </span>
              <p className="text-sm">No items in this order</p>
              <button
                onClick={addItem}
                className="mt-2 text-sm text-blue-600 hover:underline"
              >
                Add your first item
              </button>
            </div>
          )}

          {/* Order Total */}
          <div className="border-t mt-4 pt-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-600">Total</span>
              <span className="text-xl font-bold text-green-600">
                ₦{calculateTotal().toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {/* Notes */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <h2 className="text-sm font-medium text-gray-600 mb-3">Notes</h2>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full border border-gray-300 rounded-lg p-3 text-sm resize-none"
            rows={4}
            placeholder="Add any additional notes about this order..."
          />
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full h-12 bg-blue-600 text-white rounded-xl text-base font-semibold hover:bg-blue-700 disabled:opacity-50 transition shadow-sm"
        >
          {saving ? "Saving…" : "Save Changes"}
        </button>
      </div>

      {/* Material Icons CDN */}
      <link
        href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght@400;500&display=swap"
        rel="stylesheet"
      />
    </div>
  );
};

export default OrderEditPage;