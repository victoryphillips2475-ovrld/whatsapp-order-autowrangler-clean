/**
 * App root — React Router shell with protected route guard.
 *
 * Routes:
 *   /login           → LoginPage           (public)
 *   /register        → RegisterPage        (public)
 *   /                → OrdersPage          (protected)
 *   /whatsapp        → WhatsAppPage        (protected)
 *   /whatsapp/settings → WhatsAppSessionPage (protected)
 *   /dashboard       → DashboardPage       (protected)
 *   /analytics       → AnalyticsPage       (protected)
 *   /payments/:orderId → PaymentPage       (protected)
 *   /orders/:id/edit → OrderEditPage       (protected)
 *   /profile         → UserProfilePage     (protected)
 */

import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./auth";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import OrdersPage from "./pages/OrdersPage";
import WhatsAppPage from "./pages/WhatsAppPage";
import WhatsAppSessionPage from "./pages/WhatsAppSessionPage";
import DashboardPage from "./pages/DashboardPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import PaymentPage from "./pages/PaymentPage";
import OrderEditPage from "./pages/OrderEditPage";
import UserProfilePage from "./pages/UserProfilePage";

// ---------------------------------------------------------------------------
// Protected route wrapper — redirects to /login when unauthenticated
// ---------------------------------------------------------------------------

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-400">
        Loading…
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// ---------------------------------------------------------------------------
// App shell
// ---------------------------------------------------------------------------

const App: React.FC = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Protected routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <OrdersPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/whatsapp"
        element={
          <ProtectedRoute>
            <WhatsAppPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/whatsapp/settings"
        element={
          <ProtectedRoute>
            <WhatsAppSessionPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/analytics"
        element={
          <ProtectedRoute>
            <AnalyticsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/payments/:orderId"
        element={
          <ProtectedRoute>
            <PaymentPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/orders/:id/edit"
        element={
          <ProtectedRoute>
            <OrderEditPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <UserProfilePage />
          </ProtectedRoute>
        }
      />

      {/* Catch-all — redirect to orders */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
