import { TOKEN_STORAGE_KEY, setUnauthorizedHandler } from "../api/client";
import { getUser } from "../api/users";
import type { UserRead } from "../api/types";
import { toasts } from "./toast.svelte";

function decodeTokenPayload(token: string): { sub?: string; exp?: number } | null {
  const payload = token.split(".")[1];
  if (!payload) return null;
  try {
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = atob(base64);
    return JSON.parse(json) as { sub?: string; exp?: number };
  } catch {
    return null;
  }
}

function decodeUserIdFromToken(token: string): number | null {
  const data = decodeTokenPayload(token);
  return data?.sub !== undefined ? Number(data.sub) : null;
}

/** setTimeout's delay is a 32-bit int; treat anything past that as "don't bother scheduling". */
const MAX_TIMEOUT_MS = 2 ** 31 - 1;

class AuthStore {
  token = $state<string | null>(localStorage.getItem(TOKEN_STORAGE_KEY));
  user = $state<UserRead | null>(null);
  ready = $state(false);

  private expiryTimer: ReturnType<typeof setTimeout> | null = null;

  get isAuthenticated(): boolean {
    return this.token !== null;
  }

  /** Resolves the logged-in user from a stored token. Call once at startup. */
  async init(): Promise<void> {
    if (this.token === null) {
      this.ready = true;
      return;
    }
    const userId = decodeUserIdFromToken(this.token);
    if (userId === null) {
      this.logout();
      this.ready = true;
      return;
    }
    this.scheduleExpiry(this.token);
    try {
      this.user = await getUser(userId);
    } catch {
      this.logout();
    } finally {
      this.ready = true;
    }
  }

  async loginWithToken(token: string): Promise<void> {
    this.token = token;
    localStorage.setItem(TOKEN_STORAGE_KEY, token);
    this.scheduleExpiry(token);
    const userId = decodeUserIdFromToken(token);
    this.user = userId !== null ? await getUser(userId) : null;
  }

  logout(): void {
    this.token = null;
    this.user = null;
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    this.clearExpiryTimer();
  }

  /** Called when a request comes back 401 (expired/invalid token), or when the token's own exp elapses. */
  sessionExpired(): void {
    if (!this.isAuthenticated) return;
    this.logout();
    toasts.push("Your session expired — please log in again.", "info");
  }

  /** Arms a timer to log the user out the moment the token's `exp` claim elapses, even if idle. */
  private scheduleExpiry(token: string): void {
    this.clearExpiryTimer();
    const exp = decodeTokenPayload(token)?.exp;
    if (exp === undefined) return;
    const delayMs = exp * 1000 - Date.now();
    if (delayMs <= 0) {
      this.sessionExpired();
      return;
    }
    if (delayMs > MAX_TIMEOUT_MS) return;
    this.expiryTimer = setTimeout(() => this.sessionExpired(), delayMs);
  }

  private clearExpiryTimer(): void {
    if (this.expiryTimer !== null) clearTimeout(this.expiryTimer);
    this.expiryTimer = null;
  }
}

export const auth = new AuthStore();
setUnauthorizedHandler(() => auth.sessionExpired());
