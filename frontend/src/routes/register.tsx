import { Link, createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { register } from "@/services/auth-service";
export const Route = createFileRoute("/register")({ component: RegisterPage });
function RegisterPage() { const navigate = useNavigate(); const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
 async function submit(e: React.FormEvent) { e.preventDefault(); setBusy(true); setError(""); try { await register(email, password); await navigate({ to: "/login" }); } catch (x) { setError(x instanceof Error ? x.message : "Unable to register."); } finally { setBusy(false); } }
 return <main className="flex min-h-screen items-center justify-center p-4"><Card className="w-full max-w-md"><CardHeader><CardTitle>Create account</CardTitle><CardDescription>Start tracking your expenses.</CardDescription></CardHeader><CardContent><form className="grid gap-4" onSubmit={submit}><div className="grid gap-2"><Label>Email</Label><Input type="email" value={email} onChange={e => setEmail(e.target.value)} required /></div><div className="grid gap-2"><Label>Password</Label><Input type="password" value={password} onChange={e => setPassword(e.target.value)} minLength={8} required /></div>{error && <p className="text-sm text-destructive">{error}</p>}<Button disabled={busy}>{busy ? "Creating…" : "Create account"}</Button><p className="text-sm text-muted-foreground">Already have an account? <Link to="/login" className="text-primary underline">Sign in</Link></p></form></CardContent></Card></main>; }
