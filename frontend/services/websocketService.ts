const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

type MessageHandler = (data: unknown) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private handlers: Map<string, MessageHandler[]> = new Map();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private token: string | null = null;

  connect(token?: string) {
    if (typeof window === "undefined") return;
    this.token = token || localStorage.getItem("access_token");
    const url = this.token ? `${WS_URL}/ws?token=${this.token}` : `${WS_URL}/ws`;

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log("[WS] Connected");
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        const handlers = this.handlers.get(message.type) || [];
        handlers.forEach((h) => h(message.data));
        // Also call wildcard handlers
        const wildcardHandlers = this.handlers.get("*") || [];
        wildcardHandlers.forEach((h) => h(message));
      } catch {
        console.error("[WS] Failed to parse message");
      }
    };

    this.ws.onerror = () => console.error("[WS] Error");

    this.ws.onclose = () => {
      console.log("[WS] Disconnected – reconnecting in 3s");
      this.reconnectTimer = setTimeout(() => this.connect(), 3000);
    };
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    this.ws?.close();
    this.ws = null;
  }

  on(type: string, handler: MessageHandler) {
    const existing = this.handlers.get(type) || [];
    this.handlers.set(type, [...existing, handler]);
  }

  off(type: string, handler: MessageHandler) {
    const existing = this.handlers.get(type) || [];
    this.handlers.set(type, existing.filter((h) => h !== handler));
  }

  send(data: unknown) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  ping() {
    this.send({ type: "PING" });
  }
}

export const wsService = new WebSocketService();
