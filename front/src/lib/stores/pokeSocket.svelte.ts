import { TOKEN_STORAGE_KEY } from "../api/client";
import type { PokeEvent } from "../api/types";

const MAX_RECONNECT_DELAY_MS = 30_000;

type Listener = (event: PokeEvent) => void;

/**
 * Live feed of pokes received by the current user, so PokePage can flip a
 * friend's button back to "ready" the instant they poke back, without a refresh.
 * Backs off and reconnects on drop; auth is a `?token=` query param since the
 * WebSocket API can't set an Authorization header.
 */
class PokeSocketStore {
  connected = $state(false);

  private socket: WebSocket | null = null;
  private listeners = new Set<Listener>();
  private reconnectDelayMs = 1000;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private shouldConnect = false;

  connect(): void {
    if (this.shouldConnect) return;
    this.shouldConnect = true;
    document.addEventListener("visibilitychange", this.handleVisibilityChange);
    this.open();
  }

  disconnect(): void {
    this.shouldConnect = false;
    document.removeEventListener("visibilitychange", this.handleVisibilityChange);
    if (this.reconnectTimer !== null) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = null;
    this.socket?.close();
    this.socket = null;
    this.connected = false;
  }

  // Backgrounded tabs can have their reconnect timer throttled by the browser well past
  // its nominal delay, and can lose the socket outright without a timely `onclose`. Coming
  // back to the tab is the moment a resync matters most, so reconnect immediately instead
  // of waiting out a stale backoff.
  private handleVisibilityChange = (): void => {
    if (document.visibilityState !== "visible" || !this.shouldConnect || this.socket !== null) {
      return;
    }
    if (this.reconnectTimer !== null) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = null;
    this.reconnectDelayMs = 1000;
    this.open();
  };

  /** Registers a poke listener; call the returned function to unregister it. */
  onPoke(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private open(): void {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (!token) return;

    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(
      `${protocol}//${location.host}/api/pokes/ws?token=${encodeURIComponent(token)}`,
    );
    this.socket = socket;

    socket.onopen = () => {
      this.connected = true;
      this.reconnectDelayMs = 1000;
    };

    socket.onmessage = (event: MessageEvent<string>) => {
      let data: PokeEvent;
      try {
        data = JSON.parse(event.data) as PokeEvent;
      } catch {
        return;
      }
      this.listeners.forEach((listener) => listener(data));
    };

    socket.onclose = () => {
      this.connected = false;
      if (this.socket === socket) this.socket = null;
      if (this.shouldConnect) this.scheduleReconnect();
    };

    socket.onerror = () => socket.close();
  }

  private scheduleReconnect(): void {
    this.reconnectTimer = setTimeout(() => {
      this.open();
      this.reconnectDelayMs = Math.min(this.reconnectDelayMs * 2, MAX_RECONNECT_DELAY_MS);
    }, this.reconnectDelayMs);
  }
}

export const pokeSocket = new PokeSocketStore();
