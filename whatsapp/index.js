require('dotenv').config();
const { default: makeWASocket, useMultiFileAuthState, fetchLatestBaileysVersion, DisconnectReason, Browsers } = require('@adiwajshing/baileys');
const qrcode = require('qrcode-terminal');
const path = require('path');
const fs = require('fs');

// Directory for storing auth credentials (session files)
const AUTH_DIR = path.resolve(__dirname, 'session');
// Ensure session directory exists before loading auth state
if (!fs.existsSync(AUTH_DIR)) {
  fs.mkdirSync(AUTH_DIR, { recursive: true });
}

// ---------------------------------------------------------------------------
// Message deduplication — track forwarded message IDs
// ---------------------------------------------------------------------------
const _forwardedIds = new Set();
const DEDUP_MAX_SIZE = 10000; // prevent unbounded memory growth

function _isDuplicate(msgId) {
  if (_forwardedIds.has(msgId)) return true;
  _forwardedIds.add(msgId);
  // Evict oldest entries when set grows too large
  if (_forwardedIds.size > DEDUP_MAX_SIZE) {
    const iter = _forwardedIds.values();
    for (let i = 0; i < DEDUP_MAX_SIZE / 2; i++) {
      _forwardedIds.delete(iter.next().value);
    }
  }
  return false;
}

// ---------------------------------------------------------------------------
// Reconnection with exponential backoff
// ---------------------------------------------------------------------------
const MAX_RECONNECT_ATTEMPTS = 10;
const BASE_RECONNECT_DELAY_MS = 2000;
let _reconnectAttempts = 0;
let _firstConnection = true;
let _sock = null;

async function startWhatsApp() {
  // Load or create authentication state (stores keys, credentials, etc.)
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);

  // Get the latest Baileys version to ensure compatibility
  const { version } = await fetchLatestBaileysVersion();

  _sock = makeWASocket({
    version,
    auth: state,
    printQRInTerminal: true, // Prints QR code for scanning when auth is needed
    browser: Browsers.macOS('Chrome'), // Identify client; adjust as needed
  });

  // Persist credentials on any update
  _sock.ev.on('creds.update', saveCreds);

  // Connection lifecycle handling
  _sock.ev.on('connection.update', ({ connection, lastDisconnect }) => {
    if (connection === 'close') {
      const statusCode = lastDisconnect?.error?.output?.statusCode ?? lastDisconnect?.error?.statusCode;
      const reason = String(lastDisconnect?.error?.reason ?? lastDisconnect?.error?.message ?? 'unknown');
      console.log('Connection closed, reason:', reason, 'statusCode:', statusCode);

      // Reconnect unless intentional logout (5xx or 401 = logged out from another device)
      const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
      if (shouldReconnect && _reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        const delay = BASE_RECONNECT_DELAY_MS * Math.pow(2, _reconnectAttempts);
        _reconnectAttempts++;
        console.log(`Reconnecting in ${delay}ms (attempt ${_reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
        setTimeout(() => {
          startWhatsApp().catch((err) => {
            console.error('Reconnection attempt failed:', err);
          });
        }, delay);
      } else if (_reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        console.error('Max reconnection attempts reached. Exiting.');
        process.exit(1);
      }
    } else if (connection === 'open') {
      if (_firstConnection) {
        console.log('WhatsApp connection established');
        _firstConnection = false;
      } else {
        console.log('WhatsApp reconnected');
      }
      _reconnectAttempts = 0;
    }
  });

  // Forward incoming text messages to FastAPI backend (if configured)
  _sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (type !== 'notify' && type !== 'append') return;
    for (const msg of messages) {
      if (msg.key.fromMe) continue;

      // Message dedup — skip already-forwarded messages
      const msgId = msg.key.id;
      if (!msgId || _isDuplicate(msgId)) continue;

      // Handle both regular text messages and extended text messages
      const text = msg.message?.conversation
        || msg.message?.extendedTextMessage?.text
        || msg.message?.imageMessage?.caption
        || '';
      if (!text) continue;
      console.log('Received message from', msg.key.remoteJid, ':', text);

      const endpoint = process.env.FASTAPI_URL || 'http://localhost:8000';
      const webhookSecret = process.env.WEBHOOK_SECRET || '';
      const FETCH_TIMEOUT_MS = 10_000;
      try {
        await fetch(`${endpoint}/api/v1/webhooks/incoming`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Webhook-Secret': webhookSecret,
          },
          body: JSON.stringify({
            from: msg.key.remoteJid,
            body: text,
            timestamp: msg.messageTimestamp,
          }),
          signal: AbortSignal.timeout(FETCH_TIMEOUT_MS),
        });
      } catch (e) {
        console.error('Failed to forward incoming message to FastAPI:', e);
      }
    }
  });
}

// ---------------------------------------------------------------------------
// Startup with retry/backoff
// ---------------------------------------------------------------------------
const MAX_STARTUP_ATTEMPTS = 5;
const BASE_STARTUP_DELAY_MS = 3000;

async function startWithRetry(attempt = 1) {
  try {
    await startWhatsApp();
  } catch (err) {
    console.error(`startWhatsApp() failed (attempt ${attempt}/${MAX_STARTUP_ATTEMPTS}):`, err);
    if (attempt < MAX_STARTUP_ATTEMPTS) {
      const delay = BASE_STARTUP_DELAY_MS * attempt;
      console.log(`Retrying startup in ${delay}ms...`);
      await new Promise((resolve) => setTimeout(resolve, delay));
      return startWithRetry(attempt + 1);
    }
    console.error('All startup attempts failed. Exiting.');
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------
// Graceful shutdown — logout of WhatsApp session on SIGTERM/SIGINT
// ---------------------------------------------------------------------------
async function gracefulShutdown(signal) {
  console.log(`Received ${signal}. Shutting down gracefully...`);
  if (_sock) {
    try {
      await _sock.logout();
      console.log('WhatsApp session logged out.');
    } catch (err) {
      console.error('Error during WhatsApp logout:', err);
    }
  }
  process.exit(0);
}

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Start the service
startWithRetry().catch((err) => {
  console.error('Fatal error during WhatsApp service startup:', err);
  process.exit(1);
});
