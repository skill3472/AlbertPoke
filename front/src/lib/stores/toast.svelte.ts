export type ToastKind = "success" | "error" | "info";

export interface Toast {
  id: number;
  message: string;
  kind: ToastKind;
}

let nextId = 0;

class ToastStore {
  items = $state<Toast[]>([]);

  push(message: string, kind: ToastKind = "info", durationMs = 3500): void {
    const id = nextId++;
    this.items.push({ id, message, kind });
    setTimeout(() => this.dismiss(id), durationMs);
  }

  dismiss(id: number): void {
    this.items = this.items.filter((t) => t.id !== id);
  }
}

export const toasts = new ToastStore();
