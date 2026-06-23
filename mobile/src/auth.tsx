/**
 * Auth context — provides the current user, login/register/logout
 * actions, and a loading gate for the protected route shell.
 *
 * Token is persisted in localStorage via `api.ts` helpers.
 * On mount, if a token exists, we validate it by calling GET /auth/me.
 */

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import type { User, LoginPayload, RegisterPayload } from "./types";
import * as api from "./api";

// ---------------------------------------------------------------------------
// Context shape
// ---------------------------------------------------------------------------

interface AuthState {
  user: User | null;
  loading: boolean;           // true during initial token validation
  login: (p: LoginPayload) => Promise<void>;
  register: (p: RegisterPayload) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------

export const AuthProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  /** Fetch /auth/me to validate token and populate user. */
  const refreshUser = useCallback(async () => {
    try {
      const me = await api.auth.me();
      setUser(me);
    } catch {
      setUser(null);
      api.clearToken();
    }
  }, []);

  // On mount, attempt silent login from stored token.
  useEffect(() => {
    if (api.isAuthenticated()) {
      refreshUser().finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [refreshUser]);

  const login = useCallback(
    async (payload: LoginPayload) => {
      await api.auth.login(payload);
      await refreshUser();
    },
    [refreshUser],
  );

  const register = useCallback(
    async (payload: RegisterPayload) => {
      await api.auth.register(payload);
      // After registration, auto-login
      await api.auth.login({
        phone: payload.phone,
        password: payload.password,
      });
      await refreshUser();
    },
    [refreshUser],
  );

  const logout = useCallback(() => {
    api.auth.logout();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, loading, login, register, logout, refreshUser }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}
