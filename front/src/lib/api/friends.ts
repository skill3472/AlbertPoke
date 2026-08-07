import { apiGet, apiPostEmpty } from "./client";
import type { FriendAddResult, FriendBrief, MutualFriendsResult } from "./types";

export function listFriends(): Promise<FriendBrief[]> {
  return apiGet<FriendBrief[]>("/friends/list");
}

export function addFriend(friendUserId: number): Promise<FriendAddResult> {
  return apiPostEmpty<FriendAddResult>(`/friends/add/${friendUserId}`);
}

export function checkMutualFriends(userAId: number, userBId: number): Promise<MutualFriendsResult> {
  return apiGet<MutualFriendsResult>(`/friends/mutual/${userAId}/${userBId}`);
}
