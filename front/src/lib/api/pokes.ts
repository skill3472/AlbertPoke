import { apiGet, apiPostEmpty } from "./client";
import type { PokeResponse, PokeStatus, PokeThread } from "./types";

export function listPokeThreads(): Promise<PokeThread[]> {
  return apiGet<PokeThread[]>("/pokes/threads");
}

export function checkPoke(targetUserId: number): Promise<PokeStatus> {
  return apiGet<PokeStatus>("/pokes/check", { target_user_id: targetUserId });
}

export function sendPoke(pokedUserId: number): Promise<PokeResponse> {
  return apiPostEmpty<PokeResponse>("/pokes/poke", { poked_user_id: pokedUserId });
}
