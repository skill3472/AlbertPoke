import { apiGet, apiPutJson } from "./client";
import type { UserSettings } from "./types";

export function getSettings(): Promise<UserSettings> {
  return apiGet<UserSettings>("/settings");
}

export function updateSettings(settings: UserSettings): Promise<UserSettings> {
  return apiPutJson<UserSettings>("/settings", settings);
}
