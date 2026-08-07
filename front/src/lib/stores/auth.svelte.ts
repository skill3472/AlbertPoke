import { TOKEN_STORAGE_KEY } from "../api/client";
import { getUser } from "../api/users";
import type { UserRead } from "../api/types";

function decodeUserIdFromToken(token: string): number | null {
  const payload = token.split(".")[1];
  if (!payload) return null;
  try {
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const json = atob(base64);
    const data = JSON.parse(json) as { sub?: string };
    return data.sub !== undefined ? Number(data.sub) : null;
  } catch {
    return null;
  }
}

class AuthStore {
  token = $state<string | null>(localStorage.getItem(TOKEN_STORAGE_KEY));
  user = $state<UserRead | null>(null);
  ready = $state(false);

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
    const userId = decodeUserIdFromToken(token);
    this.user = userId !== null ? await getUser(userId) : null;
  }

  logout(): void {
    this.token = null;
    this.user = null;
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  }
}

export const auth = new AuthStore();
