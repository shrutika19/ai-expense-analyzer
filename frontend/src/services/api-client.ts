const BASE_URL = import.meta.env.VITE_API_BASE_URL;
const TOKEN_KEY = "expense_analyzer_token";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) { super(message); this.status = status; }
}

export const auth = {
  token: () => localStorage.getItem(TOKEN_KEY),
  setToken: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

function errorMessage(payload: unknown, fallback: string): string {
  if (!payload || typeof payload !== "object") return fallback;
  const data = payload as { message?: unknown; detail?: unknown; error?: unknown };
  if (typeof data.message === "string") return data.message;
  if (data.error && typeof data.error === "object" && typeof (data.error as { message?: unknown }).message === "string") {
    return (data.error as { message: string }).message;
  }
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail.map((item) => {
      if (item && typeof item === "object" && typeof (item as { msg?: unknown }).msg === "string") return (item as { msg: string }).msg;
      return "Invalid input.";
    }).join(" ");
  }
  return fallback;
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const token = auth.token();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
  let response: Response;
  try { response = await fetch(`${BASE_URL}/api/v1${path}`, { ...init, headers }); }
  catch { throw new ApiError(0, "Network error. Check your connection and try again."); }
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const message = errorMessage(payload, "Request failed.");
    if (response.status === 401) auth.clear();
    throw new ApiError(response.status, message);
  }
  return response.json() as Promise<T>;
}
