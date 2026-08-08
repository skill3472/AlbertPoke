// Mirrors the Pydantic models in the backend (src/users, src/friends, src/pokes).

export interface UserRead {
  id: number;
  name: string;
}

export interface FriendBrief {
  id: number;
  name: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface FriendAddResult {
  friend_id: number;
  mutual: boolean;
}

export interface MutualFriendsResult {
  mutual: boolean;
}

export interface PokeResponse {
  user_id: number;
  success: boolean;
  current_streak: number;
}

export interface PokeStatus {
  can_poke: boolean;
  streak: number;
  mutual: boolean;
  cooldown_seconds: number;
}

export interface PokeThread {
  user: FriendBrief;
  streak: number;
  can_poke: boolean;
  last_poke_mine: boolean;
  mutual: boolean;
  cooldown_seconds: number;
}

export interface VapidPublicKey {
  public_key: string;
}

export type PokeLayout = "list" | "tiles";

export interface UserSettings {
  poke_layout: PokeLayout;
}

export interface PokeEvent {
  type: "poke";
  from_user_id: number;
  from_user_name: string;
  streak: number;
  can_poke: boolean;
  cooldown_seconds: number;
}

export interface AltchaChallenge {
  algorithm: string;
  challenge: string;
  maxnumber?: number;
  salt: string;
  signature: string;
}
