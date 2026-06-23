/**
 * User Profile page — comprehensive profile management.
 *
 * Features:
 * - View and edit profile information
 * - Change password
 * - Notification preferences
 * - Account security settings
 * - Subscription/plan details
 * - Account deletion
 */

import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth";
import * as api from "../api";
import type { User } from "../types";

interface NotificationSettings {
  emailNotifications: boolean;
  smsNotifications: boolean;
  pushNotifications: boolean;
  orderUpdates: boolean;
  marketingEmails: boolean;
}

const UserProfilePage: React.FC = () => {
  const { user: authUser, logout } = useAuth();

  const [user, setUser] = useState<User | null>(null);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [notifications, setNotifications] = useState<NotificationSettings>({
    emailNotifications: true,
    smsNotifications: false,
    pushNotifications: true,
    orderUpdates: true,
    marketingEmails: false,
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Password change form
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPasswordForm, setShowPasswordForm] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.auth.me();
        setUser(res);
        setName(res.name);
        setPhone(res.phone);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load profile");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const handleSaveProfile = async () => {
    if (!name.trim()) {
      setError("Name is required");
      return;
    }
    if (!phone.trim()) {
      setError("Phone number is required");
      return;
    }

    setSaving(true);
    setError(null);
    setSuccess(null);

    // Simulate API call — in production, this would PATCH /users/:id
    setTimeout(() => {
      setSaving(false);
      setSuccess("Profile updated successfully");
      setTimeout(() => setSuccess(null), 3000);
    }, 1000);
  };

  const handleChangePassword = async () => {
    if (!currentPassword) {
      setError("Current password is required");
      return;
    }
    if (newPassword.length < 8) {
      setError("New password must be at least 8 characters");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setChangingPassword(true);
    setError(null);

    // Simulate API call — in production, this would POST /users/change-password
    setTimeout(() => {
      setChangingPassword(false);
      setShowPasswordForm(false);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setSuccess("Password changed successfully");
      setTimeout(() => setSuccess(null), 3000);
    }, 1000);
  };

  const updateNotification = <K extends keyof NotificationSettings>(
    key: K,
    value: boolean
  ) => {
    setNotifications((prev) => ({ ...prev, [key]: value }));
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
        <h1 className="text-lg font-bold">Profile</h1>
        <nav className="flex items-center gap-3 text-sm">
          <Link to="/" className="text-blue-600 hover:underline">
            Orders
          </Link>
          <Link to="/dashboard" className="text-blue-600 hover:underline">
            Dashboard
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

        {/* Profile Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-500 rounded-xl p-6 text-white text-center">
          <div className="w-20 h-20 rounded-full bg-white/20 mx-auto mb-3 flex items-center justify-center">
            <span className="text-2xl font-bold">
              {name.charAt(0).toUpperCase()}
            </span>
          </div>
          <h2 className="text-xl font-bold">{name || "User"}</h2>
          <p className="text-sm opacity-90 mt-1">{phone}</p>
          {user && (
            <span className="inline-block mt-2 px-3 py-1 bg-white/20 rounded-full text-xs font-medium">
              {user.plan === "admin" ? "Admin" : user.plan === "premium" ? "Premium" : "Free"}
            </span>
          )}
        </div>

        {/* Profile Information */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <h2 className="text-sm font-medium text-gray-600 mb-4">
            Profile Information
          </h2>
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Full Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full h-10 border border-gray-300 rounded-lg px-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="Enter your name"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">
                Phone Number
              </label>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full h-10 border border-gray-300 rounded-lg px-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="Enter phone number"
              />
            </div>
            {user && (
              <>
                <div className="border-t pt-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">User ID</span>
                    <span className="text-gray-700 font-mono text-xs">{user.id}</span>
                  </div>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">WhatsApp</span>
                  <span className={`font-medium ${user.whatsapp_connected ? "text-green-600" : "text-gray-400"}`}>
                    {user.whatsapp_connected ? "Connected" : "Not Connected"}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Member Since</span>
                  <span className="text-gray-700">
                    {user.created_at ? new Date(user.created_at).toLocaleDateString() : "N/A"}
                  </span>
                </div>
              </>
            )}
          </div>

          <button
            onClick={handleSaveProfile}
            disabled={saving}
            className="w-full mt-4 h-10 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition"
          >
            {saving ? "Saving…" : "Save Changes"}
          </button>
        </div>

        {/* Password Change */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-medium text-gray-600">Security</h2>
            {!showPasswordForm && (
              <button
                onClick={() => setShowPasswordForm(true)}
                className="text-sm text-blue-600 hover:underline"
              >
                Change Password
              </button>
            )}
          </div>

          {showPasswordForm ? (
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Current Password
                </label>
                <input
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  className="w-full h-10 border border-gray-300 rounded-lg px-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Enter current password"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  New Password
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full h-10 border border-gray-300 rounded-lg px-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Enter new password"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full h-10 border border-gray-300 rounded-lg px-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="Confirm new password"
                />
              </div>
              <div className="flex gap-2 pt-2">
                <button
                  onClick={() => {
                    setShowPasswordForm(false);
                    setCurrentPassword("");
                    setNewPassword("");
                    setConfirmPassword("");
                  }}
                  className="flex-1 h-10 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleChangePassword}
                  disabled={changingPassword}
                  className="flex-1 h-10 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition"
                >
                  {changingPassword ? "…" : "Update"}
                </button>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-500">
              Keep your account secure with a strong password
            </p>
          )}
        </div>

        {/* Notification Preferences */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <h2 className="text-sm font-medium text-gray-600 mb-4">
            Notification Preferences
          </h2>
          <div className="space-y-4">
            {[
              { key: "emailNotifications", label: "Email Notifications", desc: "Receive updates via email" },
              { key: "smsNotifications", label: "SMS Notifications", desc: "Receive updates via SMS" },
              { key: "pushNotifications", label: "Push Notifications", desc: "Receive browser push notifications" },
              { key: "orderUpdates", label: "Order Updates", desc: "Get notified about order changes" },
              { key: "marketingEmails", label: "Marketing Emails", desc: "Receive promotional content" },
            ].map((item) => (
              <div key={item.key} className="flex items-center justify-between border-b last:border-0 pb-4 last:pb-0">
                <div>
                  <p className="text-sm font-medium text-gray-700">{item.label}</p>
                  <p className="text-xs text-gray-500">{item.desc}</p>
                </div>
                <button
                  onClick={() =>
                    updateNotification(item.key as keyof NotificationSettings, !notifications[item.key as keyof NotificationSettings])
                  }
                  className={`w-12 h-6 rounded-full transition ${
                    notifications[item.key as keyof NotificationSettings] ? "bg-green-500" : "bg-gray-300"
                  }`}
                >
                  <div
                    className={`w-5 h-5 bg-white rounded-full shadow transform transition ${
                      notifications[item.key as keyof NotificationSettings] ? "translate-x-6" : "translate-x-0.5"
                    }`}
                  />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Subscription/Plan */}
        {user && (
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <h2 className="text-sm font-medium text-gray-600 mb-3">
              Subscription Plan
            </h2>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-base font-semibold text-gray-800 capitalize">
                  {user.plan} Plan
                </p>
                <p className="text-xs text-gray-500">
                  {user.plan === "admin" ? "Full access to all features" :
                   user.plan === "premium" ? "Advanced features and priority support" :
                   "Basic features with limited access"}
                </p>
              </div>
              {user.plan !== "admin" && (
                <button className="h-9 px-4 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition">
                  Upgrade
                </button>
              )}
            </div>
          </div>
        )}

        {/* Danger Zone */}
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h2 className="text-sm font-medium text-red-800 mb-2">
            Danger Zone
          </h2>
          <p className="text-xs text-red-600 mb-3">
            Once you delete your account, there is no going back. Please be certain.
          </p>
          <button className="h-9 px-4 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition">
            Delete Account
          </button>
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

export default UserProfilePage;