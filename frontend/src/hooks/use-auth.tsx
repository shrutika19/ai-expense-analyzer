import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { api, auth } from "@/services/api-client";
import { login as requestLogin, type AuthUser } from "@/services/auth-service";

type AuthState = { user: AuthUser | null; loading: boolean; login: (email: string, password: string) => Promise<void>; logout: () => void };
const AuthContext = createContext<AuthState | null>(null);
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  // Start in loading state when a persisted JWT exists. This prevents the
  // protected shell from redirecting before the session validation finishes.
  const [loading, setLoading] = useState(() => Boolean(auth.token()));
  useEffect(() => {
    if (!auth.token()) return;
    api<AuthUser>("/auth/user").then(setUser).catch(auth.clear).finally(() => setLoading(false));
  }, []);
  const value = useMemo(() => ({ user, loading, login: async (email: string, password: string) => setUser(await requestLogin(email, password)), logout: () => { auth.clear(); setUser(null); } }), [user, loading]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export function useAuth() { const context = useContext(AuthContext); if (!context) throw new Error("useAuth requires AuthProvider"); return context; }
