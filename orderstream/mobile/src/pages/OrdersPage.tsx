/**
 * Orders page — list all orders with status filter, detail expansion,
 * and inline actions: confirm, fulfill, generate payment link.
 */

import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import type { Order, OrderListResponse } from "../types";
import * as api from "../api";
import { useAuth } from "../auth";

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  confirmed: "bg-blue-100 text-blue-800",
  paid: "bg-green-100 text-green-800",
  fulfilled: "bg-gray-100 text-gray-800",
  cancelled: "bg-red-100 text-red-800",
};

const OrdersPage: React.FC = () => {
  const { logout } = useAuth();

  const [orders, setOrders] = useState<Order[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Action states keyed by order ID
  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>(
    {},
  );
  const [actionError, setActionError] = useState<Record<string, string>>({});
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const PAGE_SIZE = 20;

  const fetchOrders = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res: OrderListResponse = await api.orders.list({
        status: statusFilter || undefined,
        page,
        page_size: PAGE_SIZE,
      });
      setOrders(res.orders);
      setTotal(res.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load orders");
    } finally {
      setLoading(false);
    }
  }, [statusFilter, page]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  // --- Actions ---

  const markActionLoading = (id: string, val: boolean) =>
    setActionLoading((prev) => ({ ...prev, [id]: val }));

  const setActionErr = (id: string, msg: string) =>
    setActionError((prev) => ({ ...prev, [id]: msg }));

  const handleConfirm = async (id: string) => {
    markActionLoading(id, true);
    setActionErr(id, "");
    try {
      await api.orders.confirm(id);
      await fetchOrders();
    } catch (err) {
      setActionErr(
        id,
        err instanceof Error ? err.message : "Confirm failed",
      );
    } finally {
      markActionLoading(id, false);
    }
  };

  const handleFulfill = async (id: string) => {
    markActionLoading(id, true);
    setActionErr(id, "");
    try {
      await api.orders.fulfill(id);
      await fetchOrders();
    } catch (err) {
      setActionErr(
        id,
        err instanceof Error ? err.message : "Fulfill failed",
      );
    } finally {
      markActionLoading(id, false);
    }
  };

  const handlePaymentLink = async (id: string) => {
    markActionLoading(id, true);
    setActionErr(id, "");
    try {
      await api.payments.createLink(id);
      await fetchOrders();
    } catch (err) {
      setActionErr(
        id,
        err instanceof Error ? err.message : "Payment link failed",
      );
    } finally {
      markActionLoading(id, false);
    }
  };

  const toggleExpand = (id: string) =>
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <header className="bg-white border-b px-4 py-3 flex items-center justify-between sticky top-0 z-10">
        <h1 className="text-lg font-bold">OrderStream Orders</h1>
        <nav className="flex items-center gap-3 text-sm">
          <Link to="/whatsapp" className="text-blue-600 hover:underline">
            WhatsApp
          </Link>
          <Link to="/dashboard" className="text-blue-600 hover:underline">
            Dashboard
          </Link>
          <button
            onClick={logout}
            className="text-red-600 hover:underline"
          >
            Sign Out
          </button>
        </nav>
      </header>

      {/* Filters */}
      <div className="px-4 pt-4 flex items-center gap-2 flex-wrap">
        <label className="text-sm font-medium text-gray-600">Status:</label>
        {["", "pending", "confirmed", "paid", "fulfilled", "cancelled"].map(
          (s) => (
            <button
              key={s}
              onClick={() => {
                setStatusFilter(s);
                setPage(1);
              }}
              className={`text-xs px-2 py-1 rounded border transition ${
                statusFilter === s
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white text-gray-600 border-gray-300 hover:bg-gray-100"
              }`}
            >
              {s || "All"}
            </button>
          ),
        )}
      </div>

      {/* Error banner */}
      {error && (
        <div className="mx-4 mt-3 text-sm text-red-600 bg-red-50 rounded p-2">
          {error}
        </div>
      )}

      {/* Order list */}
      <div className="px-4 py-4 space-y-3">
        {loading && orders.length === 0 ? (
          <div className="text-center text-gray-400 py-12">Loading…</div>
        ) : orders.length === 0 ? (
          <div className="text-center text-gray-400 py-12">
            No orders found.
          </div>
        ) : (
          orders.map((order) => (
            <div
              key={order.id}
              className="bg-white rounded-lg shadow-sm border p-4"
            >
              {/* Row header */}
              <div
                className="flex items-center justify-between cursor-pointer"
                onClick={() => toggleExpand(order.id)}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded ${
                      STATUS_COLORS[order.status] || "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {order.status}
                  </span>
                  <span className="font-medium truncate">
                    {order.customer_name}
                  </span>
                  <span className="text-sm text-gray-500 truncate">
                    {order.customer_phone}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm font-semibold whitespace-nowrap">
                    ₦{order.total.toLocaleString()}
                  </span>
                  <span className="text-gray-400 text-xs">
                    {expanded[order.id] ? "▲" : "▼"}
                  </span>
                </div>
              </div>

              {/* Expanded detail */}
              {expanded[order.id] && (
                <div className="mt-3 border-t pt-3 space-y-2">
                  {/* Items */}
                  <div className="text-sm">
                    <span className="font-medium text-gray-600">Items:</span>
                    <ul className="ml-4 list-disc">
                      {order.items.map((item, idx) => (
                        <li key={idx}>
                          {item.quantity}× {item.product} @ ₦
                          {item.price.toLocaleString()}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Notes */}
                  {order.notes && (
                    <p className="text-sm text-gray-500">
                      <span className="font-medium">Notes:</span> {order.notes}
                    </p>
                  )}

                  {/* Payment link */}
                  {order.payment_link && (
                    <div className="text-sm">
                      <span className="font-medium text-gray-600">
                        Payment Link:
                      </span>{" "}
                      <a
                        href={order.payment_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline break-all"
                      >
                        {order.payment_link}
                      </a>
                    </div>
                  )}

                  {/* Created at */}
                  <p className="text-xs text-gray-400">
                    Created: {new Date(order.created_at).toLocaleString()}
                  </p>

                  {/* Action error */}
                  {actionError[order.id] && (
                    <div className="text-xs text-red-600 bg-red-50 rounded p-1">
                      {actionError[order.id]}
                    </div>
                  )}

                  {/* Action buttons */}
                  <div className="flex gap-2 flex-wrap">
                    {order.status === "pending" && (
                      <button
                        onClick={() => handleConfirm(order.id)}
                        disabled={!!actionLoading[order.id]}
                        className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 disabled:opacity-50 transition"
                      >
                        {actionLoading[order.id] ? "…" : "Confirm"}
                      </button>
                    )}
                    {order.status === "confirmed" && (
                      <>
                        <button
                          onClick={() => handlePaymentLink(order.id)}
                          disabled={!!actionLoading[order.id]}
                          className="text-xs bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 disabled:opacity-50 transition"
                        >
                          {actionLoading[order.id] ? "…" : "Payment Link"}
                        </button>
                        <button
                          onClick={() => handleFulfill(order.id)}
                          disabled={!!actionLoading[order.id]}
                          className="text-xs bg-gray-600 text-white px-3 py-1 rounded hover:bg-gray-700 disabled:opacity-50 transition"
                        >
                          {actionLoading[order.id] ? "…" : "Fulfill"}
                        </button>
                      </>
                    )}
                    {order.status === "paid" && (
                      <button
                        onClick={() => handleFulfill(order.id)}
                        disabled={!!actionLoading[order.id]}
                        className="text-xs bg-gray-600 text-white px-3 py-1 rounded hover:bg-gray-700 disabled:opacity-50 transition"
                      >
                        {actionLoading[order.id] ? "…" : "Fulfill"}
                      </button>
                    )}
                    {/* Edit button — always available */}
                    <Link
                      to={`/orders/${order.id}/edit`}
                      className="text-xs bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700 transition"
                    >
                      Edit
                    </Link>
                    {/* Payment page link */}
                    <Link
                      to={`/payments/${order.id}`}
                      className="text-xs bg-pink-600 text-white px-3 py-1 rounded hover:bg-pink-700 transition"
                    >
                      Payment
                    </Link>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="px-4 pb-6 flex items-center justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="text-sm px-3 py-1 border rounded bg-white hover:bg-gray-50 disabled:opacity-30 transition"
          >
            ← Prev
          </button>
          <span className="text-sm text-gray-600">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="text-sm px-3 py-1 border rounded bg-white hover:bg-gray-50 disabled:opacity-30 transition"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
};

export default OrdersPage;
