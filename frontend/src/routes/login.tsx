import { Link, createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/use-auth";

export const Route = createFileRoute("/login")({ component: LoginPage });
function LoginPage() {
  const { login } = useAuth(); const navigate = useNavigate();
  const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  async function submit(event: React.FormEvent) { event.preventDefault(); setBusy(true); setError(""); try { await login(email, password); await navigate({ to: "/" }); } catch (e) { setError(e instanceof Error ? e.message : "Unable to sign in."); } finally { setBusy(false); } }
  return <main className="flex min-h-screen items-center justify-center p-4"><Card className="w-full max-w-md"><CardHeader><CardTitle>Sign in</CardTitle><CardDescription>Access your expense dashboard.</CardDescription></CardHeader><CardContent><form className="grid gap-4" onSubmit={submit}><div className="grid gap-2"><Label>Email</Label><Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></div><div className="grid gap-2"><Label>Password</Label><Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></div>{error && <p className="text-sm text-destructive">{error}</p>}<Button type="submit" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</Button><p className="text-sm text-muted-foreground">New here? <Link to="/register" className="text-primary underline">Create an account</Link></p></form></CardContent></Card></main>;
}
