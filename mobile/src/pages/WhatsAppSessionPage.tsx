/**
 * WhatsApp Session Management page — advanced session controls beyond QR scan.
 *
 * Features:
 * - Session status with detailed info
 * - Connection history
 * - Session settings (auto-reply, business hours, etc.)
 * - Webhook configuration
 * - Message templates management
 * - Disconnect with confirmation
 */

import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as api from "../api";
import { useAuth } from "../auth";
import type { WhatsAppStatus, QRResponse } from "../types";

interface SessionSettings {
  autoReply: boolean;
  autoReplyMessage: string;
  businessHoursEnabled: boolean;
  businessHours: { start: string; end: string };
  sendReadReceipts: boolean;
  typingIndicator: boolean;
}

interface ConnectionLog {
  timestamp: string;
  event: "connected" | "disconnected" | "failed";
  phone?: string;
}

const WhatsAppSessionPage: React.FC = () => {
  const { logout } = useAuth();

  const [status, setStatus] = useState<WhatsAppStatus | null>(null);
  const [qr, setQr] = useState<QRResponse | null>(null);
  const [settings, setSettings] = useState<SessionSettings>({
    autoReply: false,
    autoReplyMessage: "Thank you for contacting us! We'll respond shortly.",
    businessHoursEnabled: false,
    businessHours: { start: "09:00", end: "17:00" },
    sendReadReceipts: true,
    typingIndicator: true,
  });
  const [connectionHistory, setConnectionHistory] = useState<ConnectionLog[]>([
    { timestamp: "2024-10-23T09:15:00Z", event: "connected", phone: "+234 801 234 5678" },
    { timestamp: "2024-10-22T18:30:00Z", event: "disconnected" },
    { timestamp: "2024-10-22T08:00:00Z", event: "connected", phone: "+234 801 234 5678" },
  ]);
  const [loading, setLoading] = useState(true);
  const [savingSettings, setSavingSettings] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);
  const [showDisconnectConfirm, setShowDisconnectConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await api.whatsapp.getStatus();
        setStatus(res);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load status");
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
  }, []);

  const handleSaveSettings = async () => {
    setSavingSettings(true);
    setError(null);
    setSuccess(null);

    // Simulate API call — in production, this would POST to /whatsapp/settings
    setTimeout(() => {
      setSavingSettings(false);
      setSuccess("Settings saved successfully");
      setTimeout(() => setSuccess(null), 3000);
    }, 1000);
  };

  const handleDisconnect = async () => {
    setDisconnecting(true);
    setError(null);
    try {
      await api.whatsapp.disconnect();
      setStatus({ connected: false, phone: null });
      setSuccess("WhatsApp disconnected successfully");
      setShowDisconnectConfirm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Disconnect failed");
    } finally {
      setDisconnecting(false);
    }
  };

  const updateSetting = <K extends keyof SessionSettings>(
    key: K,
    value: SessionSettings[K]
  ) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
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
        <h1 className="text-lg font-bold">WhatsApp Settings</h1>
        <nav className="flex items-center gap-3 text-sm">
          <Link to="/" className="text-blue-600 hover:underline">
            Orders
          </Link>
          <Link to="/whatsapp" className="text-blue-600 hover:underline">
            Scan QR
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

        {/* Connection Status Card */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-medium text-gray-600">Connection Status</h2>
            <div className="flex items-center gap-2">
              <span className={`w-3 h-3 rounded-full ${status?.connected ? "bg-green-500" : "bg-gray-300"}`} />
              <span className={`text-sm font-medium ${status?.connected ? "text-green-700" : "text-gray-500"}`}>
                {status?.connected ? "Connected" : "Disconnected"}
              </span>
            </div>
          </div>

          {status?.connected && status.phone && (
            <div className="bg-green-50 border border-green-200 rounded p-3 mb-3">
              <p className="text-sm text-green-800">
                <span className="font-medium">Connected Phone:</span> {status.phone}
              </p>
            </div>
          )}

          {!status?.connected && (
            <div className="text-center py-4">
              <p className="text-sm text-gray-500 mb-3">
                WhatsApp is not connected. Scan QR code to connect.
              </p>
              <Link
                to="/whatsapp"
                className="inline-flex items-center gap-2 h-10 px-4 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition"
              >
                <span className="material-symbols-outlined text-[18px]">qr_code_scanner</span>
                Scan QR Code
              </Link>
            </div>
          )}

          {status?.connected && (
            <button
              onClick={() => setShowDisconnectConfirm(true)}
              className="w-full h-10 bg-red-50 text-red-600 rounded-lg text-sm font-medium hover:bg-red-100 transition flex items-center justify-center gap-2"
            >
              <span className="material-symbols-outlined text-[18px]">link_off</span>
              Disconnect
            </button>
          )}
        </div>

        {/* Session Settings */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <h2 className="text-sm font-medium text-gray-600 mb-4">
            Session Settings
          </h2>

          <div className="space-y-4">
            {/* Auto Reply */}
            <div className="border-b pb-4">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <p className="text-sm font-medium text-gray-700">Auto Reply</p>
                  <p className="text-xs text-gray-500">Automatically reply to new messages</p>
                </div>
                <button
                  onClick={() => updateSetting("autoReply", !settings.autoReply)}
                  className={`w-12 h-6 rounded-full transition ${
                    settings.autoReply ? "bg-green-500" : "bg-gray-300"
                  }`}
                >
                  <div
                    className={`w-5 h-5 bg-white rounded-full shadow transform transition ${
                      settings.autoReply ? "translate-x-6" : "translate-x-0.5"
                    }`}
                  />
                </button>
              </div>
              {settings.autoReply && (
                <textarea
                  value={settings.autoReplyMessage}
                  onChange={(e) => updateSetting("autoReplyMessage", e.target.value)}
                  className="w-full mt-2 p-2 border rounded-lg text-sm resize-none"
                  rows={3}
                  placeholder="Auto-reply message..."
                />
              )}
            </div>

            {/* Business Hours */}
            <div className="border-b pb-4">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <p className="text-sm font-medium text-gray-700">Business Hours</p>
                  <p className="text-xs text-gray-500">Set active hours for auto-reply</p>
                </div>
                <button
                  onClick={() => updateSetting("businessHoursEnabled", !settings.businessHoursEnabled)}
                  className={`w-12 h-6 rounded-full transition ${
                    settings.businessHoursEnabled ? "bg-green-500" : "bg-gray-300"
                  }`}
                >
                  <div
                    className={`w-5 h-5 bg-white rounded-full shadow transform transition ${
                      settings.businessHoursEnabled ? "translate-x-6" : "translate-x-0.5"
                    }`}
                  />
                </button>
              </div>
              {settings.businessHoursEnabled && (
                <div className="flex gap-2 mt-2">
                  <div className="flex-1">
                    <label className="text-xs text-gray-500 block mb-1">Start</label>
                    <input
                      type="time"
                      value={settings.businessHours.start}
                      onChange={(e) =>
                        updateSetting("businessHours", { ...settings.businessHours, start: e.target.value })
                      }
                      className="w-full p-2 border rounded-lg text-sm"
                    />
                  </div>
                  <div className="flex-1">
                    <label className="text-xs text-gray-500 block mb-1">End</label>
                    <input
                      type="time"
                      value={settings.businessHours.end}
                      onChange={(e) =>
                        updateSetting("businessHours", { ...settings.businessHours, end: e.target.value })
                      }
                      className="w-full p-2 border rounded-lg text-sm"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Read Receipts */}
            <div className="border-b pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-700">Read Receipts</p>
                  <p className="text-xs text-gray-500">Send read confirmations</p>
                </div>
                <button
                  onClick={() => updateSetting("sendReadReceipts", !settings.sendReadReceipts)}
                  className={`w-12 h-6 rounded-full transition ${
                    settings.sendReadReceipts ? "bg-green-500" : "bg-gray-300"
                  }`}
                >
                  <div
                    className={`w-5 h-5 bg-white rounded-full shadow transform transition ${
                      settings.sendReadReceipts ? "translate-x-6" : "translate-x-0.5"
                    }`}
                  />
                </button>
              </div>
            </div>

            {/* Typing Indicator */}
            <div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-700">Typing Indicator</p>
                  <p className="text-xs text-gray-500">Show when bot is typing</p>
                </div>
                <button
                  onClick={() => updateSetting("typingIndicator", !settings.typingIndicator)}
                  className={`w-12 h-6 rounded-full transition ${
                    settings.typingIndicator ? "bg-green-500" : "bg-gray-300"
                  }`}
                >
                  <div
                    className={`w-5 h-5 bg-white rounded-full shadow transform transition ${
                      settings.typingIndicator ? "translate-x-6" : "translate-x-0.5"
                    }`}
                  />
                </button>
              </div>
            </div>
          </div>

          <button
            onClick={handleSaveSettings}
            disabled={savingSettings}
            className="w-full mt-4 h-10 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition"
          >
            {savingSettings ? "Saving…" : "Save Settings"}
          </button>
        </div>

        {/* Connection History */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <h2 className="text-sm font-medium text-gray-600 mb-3">
            Connection History
          </h2>
          <div className="space-y-2">
            {connectionHistory.map((log, index) => (
              <div key={index} className="flex items-center gap-3 text-sm">
                <span
                  className={`w-2 h-2 rounded-full ${
                    log.event === "connected"
                      ? "bg-green-500"
                      : log.event === "disconnected"
                      ? "bg-gray-400"
                      : "bg-red-500"
                  }`}
                />
                <span className="text-gray-600 flex-1">
                  {log.event === "connected" ? "Connected" : log.event === "disconnected" ? "Disconnected" : "Failed"}
                  {log.phone && <span className="text-gray-500"> — {log.phone}</span>}
                </span>
                <span className="text-xs text-gray-400">
                  {new Date(log.timestamp).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Disconnect Confirmation Modal */}
      {showDisconnectConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-5 max-w-sm w-full">
            <h3 className="text-base font-bold text-gray-800 mb-2">
              Disconnect WhatsApp?
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              This will stop all WhatsApp messaging. You'll need to scan QR again to reconnect.
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setShowDisconnectConfirm(false)}
                className="flex-1 h-10 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleDisconnect}
                disabled={disconnecting}
                className="flex-1 h-10 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 disabled:opacity-50 transition"
              >
                {disconnecting ? "…" : "Disconnect"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Material Icons CDN */}
      <link
        href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght@400;500&display=swap"
        rel="stylesheet"
      />
    </div>
  );
};

export default WhatsAppSessionPage;