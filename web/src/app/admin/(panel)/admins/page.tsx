"use client";

import { useCallback, useEffect, useState } from "react";
import { ShieldCheck, UserPlus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

type AdminUser = {
  user_id: string;
  email: string;
  display_name: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
};
type ListResponse = { total: number; items: AdminUser[] };

export default function AdminsPage() {
  const [data, setData] = useState<ListResponse | null>(null);
  const [me, setMe] = useState<string | null>(null); // my user_id (self-deactivate guard)
  const [err, setErr] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  // add-admin form
  const [showForm, setShowForm] = useState(false);
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [creating, setCreating] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const load = useCallback(async () => {
    const [usersRes, meRes] = await Promise.all([
      fetch("/api/bff/admin/users", { cache: "no-store" }),
      fetch("/api/bff/auth/me", { cache: "no-store" }),
    ]);
    if (usersRes.ok) setData(await usersRes.json());
    else setErr(`Failed to load admins (HTTP ${usersRes.status})`);
    if (meRes.ok) setMe((await meRes.json()).user_id ?? null);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function createAdmin(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    if (password !== confirm) {
      setMsg({ ok: false, text: "Passwords do not match." });
      return;
    }
    setCreating(true);
    const res = await fetch("/api/bff/admin/users", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        email: email.trim(),
        display_name: displayName.trim() || null,
        password,
      }),
    });
    const d = await res.json().catch(() => null);
    setCreating(false);
    if (!res.ok) {
      setMsg({ ok: false, text: d?.detail ?? `Create failed (${res.status}).` });
      return;
    }
    setMsg({ ok: true, text: `Admin ${d.email} created.` });
    setEmail("");
    setDisplayName("");
    setPassword("");
    setConfirm("");
    setShowForm(false);
    await load();
  }

  async function setActive(u: AdminUser, active: boolean) {
    if (
      !active &&
      !confirm2(`Deactivate ${u.email}? They will be signed out and unable to log in.`)
    )
      return;
    setBusyId(u.user_id);
    setMsg(null);
    const res = await fetch(`/api/bff/admin/users/${u.user_id}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ is_active: active }),
    });
    setBusyId(null);
    if (!res.ok) {
      const d = await res.json().catch(() => null);
      setMsg({ ok: false, text: d?.detail ?? `Update failed (${res.status}).` });
      return;
    }
    await load();
  }

  // window.confirm shadowed by our state variable name — small helper.
  function confirm2(text: string) {
    return window.confirm(text);
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-medium">Admins</h1>
          <p className="text-sm text-muted-foreground">
            Everyone here has full, equal access to the admin panel. Accounts are deactivated,
            never deleted, so their audit history stays intact.
          </p>
        </div>
        <Button size="sm" onClick={() => setShowForm((v) => !v)}>
          <UserPlus className="mr-1 h-4 w-4" aria-hidden /> Add admin
        </Button>
      </div>

      {showForm ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">New admin account</CardTitle>
            <CardDescription>
              They can sign in immediately at /admin/login with this email and password.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={createAdmin} className="flex max-w-md flex-col gap-3">
              <Input
                type="email"
                required
                placeholder="email@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <Input
                placeholder="Display name (optional)"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
              />
              <Input
                type="password"
                required
                minLength={8}
                placeholder="Password (min 8 characters)"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <Input
                type="password"
                required
                minLength={8}
                placeholder="Confirm password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
              />
              <div className="flex gap-2">
                <Button type="submit" size="sm" disabled={creating}>
                  {creating ? "Creating…" : "Create admin"}
                </Button>
                <Button type="button" size="sm" variant="ghost" onClick={() => setShowForm(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      ) : null}

      {msg ? (
        <p className={cn("text-sm", msg.ok ? "text-green-700" : "text-destructive")}>{msg.text}</p>
      ) : null}
      {err ? <p className="text-sm text-destructive">{err}</p> : null}

      <div className="space-y-2">
        {data?.items.map((u) => (
          <div
            key={u.user_id}
            className={cn(
              "flex flex-wrap items-center justify-between gap-3 rounded-lg border px-4 py-3",
              !u.is_active && "opacity-60",
            )}
          >
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <ShieldCheck
                  className={cn("h-4 w-4", u.is_active ? "text-green-600" : "text-zinc-400")}
                  aria-hidden
                />
                <span className="font-medium">{u.email}</span>
                {u.user_id === me ? (
                  <span className="rounded-md bg-blue-100 px-1.5 py-0.5 text-[10px] font-medium text-blue-800">
                    you
                  </span>
                ) : null}
                <span className="rounded-md bg-zinc-100 px-1.5 py-0.5 text-[10px] font-medium text-zinc-600">
                  {u.role}
                </span>
                {!u.is_active ? (
                  <span className="rounded-md bg-red-100 px-1.5 py-0.5 text-[10px] font-medium text-red-800">
                    deactivated
                  </span>
                ) : null}
              </div>
              <p className="mt-0.5 text-xs text-muted-foreground">
                {u.display_name ? `${u.display_name} · ` : ""}
                last login:{" "}
                {u.last_login ? new Date(u.last_login).toLocaleString() : "never"} · added{" "}
                {new Date(u.created_at).toLocaleDateString()}
              </p>
            </div>
            <div>
              {u.is_active ? (
                <Button
                  size="sm"
                  variant="outline"
                  disabled={busyId === u.user_id || u.user_id === me}
                  title={u.user_id === me ? "You cannot deactivate your own account" : undefined}
                  onClick={() => setActive(u, false)}
                >
                  Deactivate
                </Button>
              ) : (
                <Button
                  size="sm"
                  variant="outline"
                  disabled={busyId === u.user_id}
                  onClick={() => setActive(u, true)}
                >
                  Reactivate
                </Button>
              )}
            </div>
          </div>
        ))}
        {data && data.items.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">No admin accounts.</p>
        ) : null}
      </div>
    </div>
  );
}
