/**
 * WhatsApp page — scan QR to connect, view connection status, disconnect.
 *
 * Polls GET /whatsapp/status every 5s while not connected.
 * Fetches a fresh QR on mount and when the old one expires.
 */

import React, { useEffect, useState, useCallback, useRef } from "react";
import { Link } from "react-router-dom";
import * as api from "../api";
import { useAuth } from "../auth";
import type { QRResponse, WhatsAppStatus } from "../types";

const POLL_INTERVAL = 5_000;
const QR_EXPIRY = 90_000;

const WhatsAppPage: React.FC = () => {
  const { logout } = useAuth();

  const [qr, setQr] = useState<QRResponse | null>(null);
  const [status, setStatus] = useState<WhatsAppStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [disconnecting, setDisconnecting] = useState(false);

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const qrExpiryRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // --- Fetch QR ---
  const fetchQR = useCallback(async () => {
    // Clear any existing expiry timer before making the request so that
    // a previous timer cannot fire while a new request is in flight.
    if (qrExpiryRef.current) {
      clearTimeout(qrExpiryRef.current);
      qrExpiryRef.current = null;
    }
    try {
      const res = await api.whatsapp.getQR();
      setQr(res);

      // Auto-refresh QR when it expires
      qrExpiryRef.current = setTimeout(fetchQR, res.expires_in * 1000 || QR_EXPIRY);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate QR");
    }
  }, []);

  // --- Fetch status ---
  const fetchStatus = useCallback(async () => {
    try {
      const res = await api.whatsapp.getStatus();
      setStatus(res);

      // Stop polling once connected
      if (res.connected && pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to check status");
    }
  }, []);

  // On mount: fetch QR + start polling status
  useEffect(() => {
    let cancelled = false;

    (async () => {
      setLoading(true);
      await Promise.all([fetchQR(), fetchStatus()]);
      if (!cancelled) setLoading(false);
    })();

    // Start polling
    pollRef.current = setInterval(fetchStatus, POLL_INTERVAL);

    return () => {
      cancelled = true;
      if (pollRef.current) clearInterval(pollRef.current);
      if (qrExpiryRef.current) clearTimeout(qrExpiryRef.current);
    };
  }, [fetchQR, fetchStatus]);

  // --- Disconnect ---
  const handleDisconnect = async () => {
    setDisconnecting(true);
    setError(null);
    try {
      await api.whatsapp.disconnect();
      setStatus({ connected: false, phone: null });
      // Re-fetch backend status to ensure UI is in sync
      await fetchStatus();
      // Re-fetch QR after disconnecting
      await fetchQR();
      // Resume polling
      if (!pollRef.current) {
        pollRef.current = setInterval(fetchStatus, POLL_INTERVAL);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Disconnect failed");
    } finally {
      setDisconnecting(false);
    }
  };

  if (loading && !qr && !status) {
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
        <h1 className="text-lg font-bold">WhatsApp</h1>
        <nav className="flex items-center gap-3 text-sm">
          <Link to="/" className="text-blue-600 hover:underline">
            Orders
          </Link>
          <Link to="/dashboard" className="text-blue-600 hover:underline">
            Dashboard
          </Link>
          <Link to="/whatsapp/settings" className="text-blue-600 hover:underline">
            Settings
          </Link>
          <button onClick={logout} className="text-red-600 hover:underline">
            Sign Out
          </button>
        </nav>
      </header>

      <div className="px-4 py-6 max-w-md mx-auto space-y-6">
        {/* Error banner */}
        {error && (
          <div className="text-sm text-red-600 bg-red-50 rounded p-2">
            {error}
          </div>
        )}

        {/* Connection status */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <h2 className="text-sm font-medium text-gray-600 mb-2">
            Connection Status
          </h2>
          {status?.connected ? (
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-sm font-medium text-green-700">
                Connected
                {status.phone ? ` — ${status.phone}` : ""}
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-gray-300" />
              <span className="text-sm text-gray-500">Not connected</span>
            </div>
          )}
        </div>

        {/* QR code — only show when not connected */}
        {!status?.connected && qr && (
          <div className="bg-white rounded-lg shadow-sm border p-4 flex flex-col items-center">
            <h2 className="text-sm font-medium text-gray-600 mb-3">
              Scan QR Code
            </h2>
            <img
              src={`data:image/png;base64,${qr.qr_code_base64}`}
              alt="WhatsApp QR Code"
              className="w-56 h-56 object-contain"
            />
            <p className="text-xs text-gray-400 mt-2">
              Session: {qr.session_id} · Expires in {qr.expires_in}s
            </p>
            <p className="text-xs text-gray-400 mt-1">
              Polling status every {POLL_INTERVAL / 1000}s…
            </p>
          </div>
        )}

        {/* Connected state message */}
        {status?.connected && (
          <div className="bg-white rounded-lg shadow-sm border p-4 text-center">
            <p className="text-sm text-green-700 mb-3">
              Your WhatsApp is connected and receiving orders.
            </p>
            <button
              onClick={handleDisconnect}
              disabled={disconnecting}
              className="text-sm bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 disabled:opacity-50 transition"
            >
              {disconnecting ? "Disconnecting…" : "Disconnect WhatsApp"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default WhatsAppPage;
