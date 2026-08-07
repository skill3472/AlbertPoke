import { listPokeThreads } from "../api/pokes";

const POLL_INTERVAL_MS = 15_000;
const PREFERENCE_KEY = "albertpoke:notify";

function browserSupportsNotifications(): boolean {
  return typeof Notification !== "undefined";
}

class NotificationStore {
  permission = $state<NotificationPermission>(
    browserSupportsNotifications() ? Notification.permission : "denied",
  );
  enabled = $state(localStorage.getItem(PREFERENCE_KEY) === "1");

  private previousCanPoke = new Map<number, boolean>();
  private baselineSet = false;
  private timer: ReturnType<typeof setInterval> | null = null;

  get supported(): boolean {
    return browserSupportsNotifications();
  }

  async requestPermission(): Promise<void> {
    if (!this.supported) return;
    const result = await Notification.requestPermission();
    this.permission = result;
    this.enabled = result === "granted";
    localStorage.setItem(PREFERENCE_KEY, this.enabled ? "1" : "0");
    if (this.enabled) this.startPolling();
  }

  disable(): void {
    this.enabled = false;
    localStorage.setItem(PREFERENCE_KEY, "0");
    this.stopPolling();
  }

  startPolling(): void {
    if (this.timer !== null || !this.enabled || this.permission !== "granted") return;
    this.timer = setInterval(() => void this.poll(), POLL_INTERVAL_MS);
    void this.poll();
  }

  stopPolling(): void {
    if (this.timer !== null) {
      clearInterval(this.timer);
      this.timer = null;
    }
    this.baselineSet = false;
    this.previousCanPoke.clear();
  }

  private async poll(): Promise<void> {
    if (!this.enabled || this.permission !== "granted") return;

    let threads;
    try {
      threads = await listPokeThreads();
    } catch {
      return;
    }

    for (const thread of threads) {
      const wasAlreadyMyTurn = this.previousCanPoke.get(thread.user.id) === true;
      const theyJustPokedMe = thread.can_poke && !thread.last_poke_mine && !wasAlreadyMyTurn;
      if (this.baselineSet && theyJustPokedMe) {
        new Notification(`${thread.user.name} poked you!`, {
          body: `Streak: ${thread.streak}`,
        });
      }
      this.previousCanPoke.set(thread.user.id, thread.can_poke);
    }

    this.baselineSet = true;
  }
}

export const notifications = new NotificationStore();
