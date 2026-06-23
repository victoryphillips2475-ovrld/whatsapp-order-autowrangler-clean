/**
 * Dashboard page — merchant summary statistics.
 *
 * Fetches GET /dashboard/stats and renders a grid of metric cards.
 * The backend returns a flexible dict, so we render whatever key-value
 * pairs come back.
 */

import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as api from "../api";
import { useAuth } from "../auth";
import type { DashboardStats } from "../types";

/** Display-friendly labels for known stat keys. */
const LABEL_MAP: Record<string, string> = {
  total_orders: "Total Orders",
  pending_orders: "Pending",
  confirmed_orders: "Confirmed",
  paid_orders: "Paid",
  fulfilled_orders: "Fulfilled",
  total_revenue: "Revenue (₦)",
  whatsapp_connected: "WhatsApp",
};

/** Color classes for stat card accents. */
const COLOR_MAP: Record<string, string> = {
  total_orders: "border-blue-400",
  pending_orders: "border-yellow-400",
  confirmed_orders: "border-blue-400",
  paid_orders: "border-green-400",
  fulfilled_orders: "border-gray-400",
  total_revenue: "border-green-500",
  whatsapp_connected: "border-emerald-400",
};

const DashboardPage: React.FC = () => {
  const { logout } = useAuth();

  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await api.dashboard.stats();
        setStats(res);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load stats");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const formatValue = (key: string, value: unknown): string => {
    if (typeof value === "boolean") return value ? "Yes" : "No";
    if (typeof value === "number") {
      if (key.includes("revenue")) return `₦${value.toLocaleString()}`;
      return String(value);
    }
    return String(value);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top bar */}
      <header className="bg-white border-b px-4 py-3 flex items-center justify-between sticky top-0 z-10">
        <h1 className="text-lg font-bold">Dashboard</h1>
        <nav className="flex items-center gap-3 text-sm">
          <Link to="/" className="text-blue-600 hover:underline">
            Orders
          </Link>
          <Link to="/analytics" className="text-blue-600 hover:underline">
            Analytics
          </Link>
          <Link to="/profile" className="text-blue-600 hover:underline">
            Profile
          </Link>
          <button onClick={logout} className="text-red-600 hover:underline">
            Sign Out
          </button>
        </nav>
      </header>

      <div className="px-4 py-6 max-w-2xl mx-auto">
        {/* Error */}
        {error && (
          <div className="text-sm text-red-600 bg-red-50 rounded p-2 mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center text-gray-400 py-12">Loading…</div>
        ) : stats ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {Object.entries(stats).map(([key, value]) => (
              <div
                key={key}
                className={`bg-white rounded-lg shadow-sm border-l-4 p-4 ${
                  COLOR_MAP[key] || "border-gray-300"
                }`}
              >
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                  {LABEL_MAP[key] || key.replace(/_/g, " ")}
                </p>
                <p className="text-2xl font-bold mt-1">
                  {formatValue(key, value)}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-gray-400 py-12">
            No stats available.
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
