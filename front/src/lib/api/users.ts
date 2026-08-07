import { apiGet, apiPostForm, apiPostJson } from "./client";
import type { AltchaChallenge, Token, UserRead } from "./types";

export function getCaptchaChallenge(): Promise<AltchaChallenge> {
  return apiGet<AltchaChallenge>("/users/captcha");
}

export function searchUsers(query: string): Promise<UserRead[]> {
  return apiGet<UserRead[]>("/users/search", { query });
}

export function registerUser(name: string, password: string, altcha: string): Promise<UserRead> {
  return apiPostJson<UserRead>("/users/register", { name, password, altcha });
}

export function login(name: string, password: string, altcha: string): Promise<Token> {
  const form = new URLSearchParams();
  form.set("username", name);
  form.set("password", password);
  form.set("altcha", altcha);
  return apiPostForm<Token>("/users/login", form);
}

export function getUser(id: number): Promise<UserRead> {
  return apiGet<UserRead>(`/users/get/${id}`);
}
