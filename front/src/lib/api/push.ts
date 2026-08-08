import { apiGet, apiPostJson } from "./client";
import type { VapidPublicKey } from "./types";

export function getVapidPublicKey(): Promise<VapidPublicKey> {
  return apiGet<VapidPublicKey>("/push/vapid-public-key");
}

export function subscribePush(subscription: PushSubscriptionJSON): Promise<void> {
  return apiPostJson<void>("/push/subscribe", subscription);
}

export function unsubscribePush(endpoint: string): Promise<void> {
  return apiPostJson<void>("/push/unsubscribe", { endpoint });
}
