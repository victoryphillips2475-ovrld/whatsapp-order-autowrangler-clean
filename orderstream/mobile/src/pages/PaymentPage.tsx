/**
 * Payment/Checkout page — generate payment link, display payment options,
 * and track payment status for an order.
 *
 * Supports:
 * - Payment link generation via POST /payments/link
 * - Display of payment methods (Paystack, Flutterwave, Bank Transfer)
 * - Payment status polling
 * - Copy-to-clipboard for payment link
 * - Share functionality
 */

import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import * as api from "../api";
import { useAuth } from "../auth";
import type { Order } from "../types";

const PAYMENT_METHODS = [
  {
    id: "paystack",
    name: "Paystack",
    icon: "credit_card",
    color: "bg-green-600",
    description: "Card, Bank Transfer, USSD",
  },
  {
    id: "flutterwave",
    name: "Flutterwave",
    icon: "account_balance",
    color: "bg-orange-500",
    description: "Card, Mobile Money, Bank Transfer",
  },
  {
    id: "bank_transfer",
    name: "Bank Transfer",
    icon: "account_balance_wallet",
    color: "bg-blue-600",
    description: "Direct bank transfer",
  },
];

const PaymentPage: React.FC = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const { logout } = useAuth();

  const [order, setOrder] = useState<Order | null>(null);
  const [paymentLink, setPaymentLink] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

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
        if (res.payment_link) {
          setPaymentLink(res.payment_link);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load order");
      } finally {
        setLoading(false);
      }
    };

    fetchOrder();
  }, [orderId]);

  const handleGenerateLink = async () => {
    if (!orderId) return;

    setGenerating(true);
    setError(null);
    try {
      const res = await api.payments.createLink(orderId);
      setPaymentLink(res.payment_link || null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate payment link");
    } finally {
      setGenerating(false);
    }
  };

  const handleCopyLink = async () => {
    if (!paymentLink) return;

    try {
      await navigator.clipboard.writeText(paymentLink);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("Failed to copy link");
    }
  };

  const handleShare = async () => {
    if (!paymentLink) return;

    if (navigator.share) {
      try {
        await navigator.share({
          title: "Payment Link",
          text: `Pay for order ${orderId}`,
          url: paymentLink,
        });
      } catch {
        // User cancelled share
      }
    } else {
      handleCopyLink();
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
    <div className="min-h-screen bg-gray-50">
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
          <h1 className="text-lg font-bold">Payment</h1>
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
        {/* Error banner */}
        {error && (
          <div className="text-sm text-red-600 bg-red-50 rounded p-2">
            {error}
          </div>
        )}

        {/* Order Summary */}
        {order && (
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <h2 className="text-sm font-medium text-gray-600 mb-3">
              Order Summary
            </h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Order ID</span>
                <span className="text-sm font-medium">#{order.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Customer</span>
                <span className="text-sm font-medium">{order.customer_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Phone</span>
                <span className="text-sm font-medium">{order.customer_phone}</span>
              </div>
              <div className="border-t pt-2 mt-2">
                <div className="flex justify-between items-center">
                  <span className="text-base font-medium text-gray-700">Total</span>
                  <span className="text-xl font-bold text-green-600">
                    ₦{order.total.toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Payment Link Section */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <h2 className="text-sm font-medium text-gray-600 mb-3">
            Payment Link
          </h2>

          {paymentLink ? (
            <div className="space-y-3">
              <div className="bg-green-50 border border-green-200 rounded p-3">
                <div className="flex items-center gap-2 text-green-700">
                  <span className="material-symbols-outlined text-[18px]">check_circle</span>
                  <span className="text-sm font-medium">Payment link generated</span>
                </div>
              </div>

              <div className="bg-gray-50 rounded p-3 break-all text-sm text-gray-600 border">
                {paymentLink}
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleCopyLink}
                  className="flex-1 h-10 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition flex items-center justify-center gap-2"
                >
                  <span className="material-symbols-outlined text-[18px]">content_copy</span>
                  {copied ? "Copied!" : "Copy"}
                </button>
                <button
                  onClick={handleShare}
                  className="flex-1 h-10 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition flex items-center justify-center gap-2"
                >
                  <span className="material-symbols-outlined text-[18px]">share</span>
                  Share
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-sm text-gray-500 mb-3">
                Generate a secure payment link to send to the customer
              </p>
              <button
                onClick={handleGenerateLink}
                disabled={generating}
                className="h-11 px-6 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 transition"
              >
                {generating ? "Generating…" : "Generate Payment Link"}
              </button>
            </div>
          )}
        </div>

        {/* Payment Methods */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <h2 className="text-sm font-medium text-gray-600 mb-3">
            Accepted Payment Methods
          </h2>
          <div className="space-y-2">
            {PAYMENT_METHODS.map((method) => (
              <div
                key={method.id}
                className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 transition"
              >
                <div className={`w-10 h-10 ${method.color} rounded-full flex items-center justify-center`}>
                  <span className="material-symbols-outlined text-white text-[20px]">
                    {method.icon}
                  </span>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-700">{method.name}</p>
                  <p className="text-xs text-gray-500">{method.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Security Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded p-3">
          <div className="flex items-start gap-2">
            <span className="material-symbols-outlined text-blue-600 text-[18px] mt-0.5">
              security
            </span>
            <div>
              <p className="text-sm font-medium text-blue-800">Secure Payment</p>
              <p className="text-xs text-blue-600 mt-1">
                All transactions are encrypted and secured with PCI DSS compliance.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Material Icons CDN */}
      <link
        href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght@400;500&display=swap"
        rel="stylesheet"
      />
    </div>
  );
};

export default PaymentPage;