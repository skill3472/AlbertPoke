import { getVapidPublicKey, subscribePush, unsubscribePush } from "../api/push";

const PREFERENCE_KEY = "albertpoke:notify";
const SW_URL = "/sw.js";

function browserSupportsPush(): boolean {
  return (
    typeof Notification !== "undefined" && "serviceWorker" in navigator && "PushManager" in window
  );
}

function urlBase64ToUint8Array(base64Url: string): Uint8Array<ArrayBuffer> {
  const padding = "=".repeat((4 - (base64Url.length % 4)) % 4);
  const base64 = (base64Url + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(base64);
  const bytes = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) {
    bytes[i] = raw.charCodeAt(i);
  }
  return bytes;
}

class NotificationStore {
  permission = $state<NotificationPermission>(
    browserSupportsPush() ? Notification.permission : "denied",
  );
  enabled = $state(localStorage.getItem(PREFERENCE_KEY) === "1");

  get supported(): boolean {
    return browserSupportsPush();
  }

  /** Prompts for permission and, if granted, registers a real push subscription. */
  async requestPermission(): Promise<void> {
    if (!this.supported) return;
    const result = await Notification.requestPermission();
    this.permission = result;

    if (result !== "granted") {
      this.setEnabled(false);
      return;
    }

    try {
      await this.subscribe();
      this.setEnabled(true);
    } catch {
      this.setEnabled(false);
    }
  }

  async disable(): Promise<void> {
    this.setEnabled(false);
    await this.unsubscribe();
  }

  /**
   * Re-establishes the push subscription on app load if it was previously enabled.
   * Push subscriptions can be dropped by the browser (e.g. expired keys), so this
   * re-subscribes silently - no permission prompt, since it's already granted.
   */
  async ensureSubscribed(): Promise<void> {
    if (!this.supported || !this.enabled || this.permission !== "granted") return;
    try {
      await this.subscribe();
    } catch {
      // Best-effort; the user can re-enable manually from their profile if this fails.
    }
  }

  private setEnabled(value: boolean): void {
    this.enabled = value;
    localStorage.setItem(PREFERENCE_KEY, value ? "1" : "0");
  }

  private async subscribe(): Promise<void> {
    const registration = await navigator.serviceWorker.register(SW_URL);
    await navigator.serviceWorker.ready;

    let subscription = await registration.pushManager.getSubscription();
    if (!subscription) {
      const { public_key } = await getVapidPublicKey();
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(public_key),
      });
    }

    await subscribePush(subscription.toJSON() as PushSubscriptionJSON);
  }

  private async unsubscribe(): Promise<void> {
    if (!this.supported) return;
    const registration = await navigator.serviceWorker.getRegistration(SW_URL);
    const subscription = await registration?.pushManager.getSubscription();
    if (!subscription) return;

    const endpoint = subscription.endpoint;
    await subscription.unsubscribe();
    await unsubscribePush(endpoint).catch(() => {
      // Local unsubscribe already succeeded; a failure here just leaves a stale
      // row server-side, which is pruned automatically the next time a push to
      // it comes back expired.
    });
  }
}

export const notifications = new NotificationStore();
