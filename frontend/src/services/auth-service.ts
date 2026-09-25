import { api, auth } from "@/services/api-client";

export interface AuthUser { id: string; email: string; is_active: boolean }
export async function login(email: string, password: string) {
  const token = await api<{ access_token: string }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
  auth.setToken(token.access_token);
  return api<AuthUser>("/auth/user");
}
export const register = (email: string, password: string) =>
  api<AuthUser>("/auth/register", { method: "POST", body: JSON.stringify({ email, password }) });
