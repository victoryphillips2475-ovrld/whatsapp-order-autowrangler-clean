/**
 * API client for the WAW FastAPI backend.
 *
 * All endpoints are typed against the models in types.ts.
 * JWT token is persisted in localStorage and attached automatically.
 * The base URL is determined at build time via VITE_API_URL or falls
 * back to the Vite dev proxy (same origin /api/v1).
 */

import type {
  Order,
  OrderListResponse,
  CreateOrderPayload,
  UpdateOrderPayload,
  ConfirmOrderPayload,
  RegisterPayload,
  LoginPayload,
  User,
  TokenResponse,
  QRResponse,
  WhatsAppStatus,
  WhatsAppSettingsPayload,
  PaymentLinkRequest,
  UpdateUserPayload,
  ChangePasswordPayload,
  DashboardStats,
} from "./types";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const BASE = import.meta.env.VITE_API_URL || "/api/v1";
const TOKEN_KEY = "orderstream_jwt";

function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

// ---------------------------------------------------------------------------
// Low-level fetch wrapper
// ---------------------------------------------------------------------------

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers,
    signal: AbortSignal.timeout(30_000),
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // non-JSON body — use default
    }
    // Auto-logout on 401
    if (res.status === 401) {
      clearToken();
    }
    throw new ApiError(res.status, detail);
  }

  // 204 No Content — return null for void endpoints
  if (res.status === 204) {
    return null as T;
  }

  return res.json() as Promise<T>;
}

// Convenience methods
const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export const auth = {
  register: (payload: RegisterPayload) =>
    api.post<User>("/auth/register", payload),

  login: (payload: LoginPayload) =>
    api.post<TokenResponse>("/auth/login", payload).then((res) => {
      setToken(res.access_token);
      return res;
    }),

  me: () => api.get<User>("/auth/me"),

  logout: () => {
    clearToken();
  },
};

// ---------------------------------------------------------------------------
// Orders
// ---------------------------------------------------------------------------

export const orders = {
  list: (params?: {
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<OrderListResponse> => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set("status", params.status);
    if (params?.page) qs.set("page", String(params.page));
    if (params?.page_size) qs.set("page_size", String(params.page_size));
    const query = qs.toString();
    return api.get<OrderListResponse>(`/orders/${query ? `?${query}` : ""}`);
  },

  get: (id: string) => api.get<Order>(`/orders/${id}`),

  create: (payload: CreateOrderPayload) =>
    api.post<Order>("/orders/", payload),

  update: (id: string, payload: UpdateOrderPayload) =>
    api.post<Order>(`/orders/${id}`, payload), // Using POST as PUT for now

  confirm: (id: string, payload?: ConfirmOrderPayload) =>
    api.post<Order>(`/orders/${id}/confirm`, payload || {}),

  fulfill: (id: string) => api.post<Order>(`/orders/${id}/fulfill`),
};

// ---------------------------------------------------------------------------
// Payments
// ---------------------------------------------------------------------------

export const payments = {
  createLink: (orderId: string) =>
    api.post<Order>("/payments/link", { order_id: orderId } as PaymentLinkRequest),
};

// ---------------------------------------------------------------------------
// WhatsApp
// ---------------------------------------------------------------------------

export const whatsapp = {
  getQR: () => api.get<QRResponse>("/whatsapp/qr"),

  getStatus: () => api.get<WhatsAppStatus>("/whatsapp/status"),

  disconnect: () => api.post<{ message: string }>("/whatsapp/disconnect"),

  updateSettings: (payload: WhatsAppSettingsPayload) =>
    api.post<{ message: string }>("/whatsapp/settings", payload),
};

// ---------------------------------------------------------------------------
// Users / Profile
// ---------------------------------------------------------------------------

export const users = {
  update: (payload: UpdateUserPayload) =>
    api.post<User>("/users/update", payload),

  changePassword: (payload: ChangePasswordPayload) =>
    api.post<{ message: string }>("/users/change-password", payload),
};

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export const dashboard = {
  stats: () => api.get<DashboardStats>("/dashboard/stats"),
};

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

export const health = {
  check: () => api.get<{ status: string }>("/health"),
};

// Re-export error class for consumers
export { ApiError };
