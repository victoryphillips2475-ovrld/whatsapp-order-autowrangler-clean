/**
 * Core data models mirroring the FastAPI backend Pydantic schemas.
 *
 * These types are used by the API service layer and UI components to
 * ensure type safety across the full stack.
 */

// ---------------------------------------------------------------------------
// Orders
// ---------------------------------------------------------------------------

/** Individual line item within an order. */
export interface OrderItem {
  product: string;
  quantity: number;
  price: number;
}

/** Single order as returned by the backend. */
export interface Order {
  id: string;
  customer_name: string;
  customer_phone: string;
  items: OrderItem[];
  total: number;
  status: "pending" | "confirmed" | "paid" | "fulfilled" | "cancelled";
  created_at: string; // ISO-8601
  notes?: string | null;
  payment_link?: string | null;
}

/** Paginated order list response. */
export interface OrderListResponse {
  orders: Order[];
  total: number;
  page: number;
  page_size: number;
}

/** Payload for creating an order manually. */
export interface CreateOrderPayload {
  customer_name: string;
  customer_phone: string;
  items: OrderItem[];
  notes?: string;
}

/** Payload for confirming an order. */
export interface ConfirmOrderPayload {
  message?: string;
}

/** Payload for updating an order. */
export interface UpdateOrderPayload {
  customer_name?: string;
  customer_phone?: string;
  items?: OrderItem[];
  notes?: string;
  status?: "pending" | "confirmed" | "paid" | "fulfilled" | "cancelled";
}

// ---------------------------------------------------------------------------
// Auth / Users
// ---------------------------------------------------------------------------

/** Merchant registration payload. */
export interface RegisterPayload {
  name: string;
  phone: string;
  password: string;
}

/** Merchant login payload. */
export interface LoginPayload {
  phone: string;
  password: string;
}

/** Public merchant profile (no password exposed). */
export interface User {
  id: string;
  name: string;
  phone: string;
  whatsapp_connected: boolean;
  plan: string;
  created_at: string; // ISO-8601
}

/** JWT token response from login. */
export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number; // seconds
}

// ---------------------------------------------------------------------------
// WhatsApp
// ---------------------------------------------------------------------------

/** QR code response from the WhatsApp endpoint. */
export interface QRResponse {
  qr_code_base64: string;
  session_id: string;
  expires_in: number; // seconds
}

/** WhatsApp connection status. */
export interface WhatsAppStatus {
  connected: boolean;
  phone: string | null;
}

// ---------------------------------------------------------------------------
// Payments
// ---------------------------------------------------------------------------

/** Request to generate a payment link. */
export interface PaymentLinkRequest {
  order_id: string;
}

/** Payload for updating user profile. */
export interface UpdateUserPayload {
  name?: string;
  phone?: string;
}

/** Payload for changing password. */
export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}

/** Payload for updating WhatsApp settings. */
export interface WhatsAppSettingsPayload {
  auto_reply?: boolean;
  auto_reply_message?: string;
  business_hours_enabled?: boolean;
  business_hours?: { start: string; end: string };
  send_read_receipts?: boolean;
  typing_indicator?: boolean;
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

/** Dashboard summary statistics. */
export interface DashboardStats {
  [key: string]: unknown; // Flexible — the backend returns a dict
}
