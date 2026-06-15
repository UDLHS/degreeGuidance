"use client";

import { useCallback, useEffect, useState } from "react";
import { Check, Pencil, Plus, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type Alias = {
  alias_id: number;
  course_code: string;
  alias_text: string;
  source: string | null;
  confidence: number | null;
  is_verified: boolean;
};

type Form = {
  course_code: string;
  alias_text: string;
  source: string;
  confidence: string;
  is_verified: boolean;
};

const EMPTY: Form = { course_code: "", alias_text: "", source: "admin", confidence: "", is_verified: true };

export default function AliasesPage() {
  const [items, setItems] = useState<Alias[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [verified, setVerified] = useState("all");
  const [open, setOpen] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState<Form>(EMPTY);
  const [saving, setSaving] = useState(false);
  const [dialogErr, setDialogErr] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    const p = new URLSearchParams({ limit: "100" });
    if (q.trim()) p.set("q", q.trim());
    if (verified !== "all") p.set("is_verified", verified);
    const res = await fetch(`/api/bff/admin/aliases?${p.toString()}`, { cache: "no-store" });
    if (res.ok) {
      const d = await res.json();
      setItems(d.items ?? []);
      setTotal(d.total ?? 0);
    }
    setLoading(false);
  }, [q, verified]);

  useEffect(() => {
    load();
  }, [load]);

  function openCreate() {
    setEditId(null);
    setForm(EMPTY);
    setDialogErr(null);
    setOpen(true);
  }

  function openEdit(a: Alias) {
    setEditId(a.alias_id);
    setForm({
      course_code: a.course_code,
      alias_text: a.alias_text,
      source: a.source ?? "",
      confidence: a.confidence != null ? String(a.confidence) : "",
      is_verified: a.is_verified,
    });
    setDialogErr(null);
    setOpen(true);
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setDialogErr(null);
    const body: Record<string, unknown> = {
      alias_text: form.alias_text,
      source: form.source || null,
      is_verified: form.is_verified,
    };
    if (form.confidence !== "") body.confidence = Number(form.confidence);
    const isCreate = editId === null;
    if (isCreate) body.course_code = form.course_code.trim().toUpperCase();
    const res = await fetch(
      isCreate ? "/api/bff/admin/aliases" : `/api/bff/admin/aliases/${editId}`,
      {
        method: isCreate ? "POST" : "PATCH",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      },
    );
    const data = await res.json().catch(() => null);
    setSaving(false);
    if (res.ok) {
      setOpen(false);
      load();
    } else {
      setDialogErr(typeof data?.detail === "string" ? data.detail : `Failed (${res.status}).`);
    }
  }

  async function verify(a: Alias) {
    await fetch(`/api/bff/admin/aliases/${a.alias_id}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ is_verified: true }),
    });
    load();
  }

  async function del(a: Alias) {
    if (!window.confirm(`Delete alias "${a.alias_text}" (${a.course_code})?`)) return;
    await fetch(`/api/bff/admin/aliases/${a.alias_id}`, { method: "DELETE" });
    load();
  }

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-medium">Aliases</h1>
          <p className="text-sm text-muted-foreground">
            OCR label → course-code mappings ({total} total). Verify, correct, or add.
          </p>
        </div>
        <Button onClick={openCreate}>
          <Plus className="mr-1 h-4 w-4" aria-hidden /> Add alias
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Input
          placeholder="Search alias text…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        <Select value={verified} onValueChange={setVerified}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="true">Verified</SelectItem>
            <SelectItem value="false">Unverified</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="ghost" size="sm" onClick={load} disabled={loading}>
          {loading ? "Loading…" : "Refresh"}
        </Button>
      </div>

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Alias text</TableHead>
              <TableHead>Course</TableHead>
              <TableHead>Source</TableHead>
              <TableHead>Verified</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.length === 0 && !loading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-sm text-muted-foreground">
                  No aliases match.
                </TableCell>
              </TableRow>
            ) : (
              items.map((a) => (
                <TableRow key={a.alias_id}>
                  <TableCell className="text-sm">{a.alias_text}</TableCell>
                  <TableCell className="font-mono text-xs">{a.course_code}</TableCell>
                  <TableCell className="text-xs text-muted-foreground">{a.source ?? "—"}</TableCell>
                  <TableCell>
                    <span
                      className={
                        a.is_verified
                          ? "rounded-md bg-green-100 px-2 py-0.5 text-xs text-green-800"
                          : "rounded-md bg-amber-100 px-2 py-0.5 text-xs text-amber-800"
                      }
                    >
                      {a.is_verified ? "verified" : "unverified"}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      {!a.is_verified ? (
                        <Button variant="ghost" size="sm" onClick={() => verify(a)} title="Verify">
                          <Check className="h-4 w-4" aria-hidden />
                        </Button>
                      ) : null}
                      <Button variant="ghost" size="sm" onClick={() => openEdit(a)} title="Edit">
                        <Pencil className="h-4 w-4" aria-hidden />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => del(a)} title="Delete">
                        <Trash2 className="h-4 w-4" aria-hidden />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <form onSubmit={submit}>
            <DialogHeader>
              <DialogTitle>{editId === null ? "Add alias" : "Edit alias"}</DialogTitle>
              <DialogDescription>
                {editId === null
                  ? "Map an OCR label to an existing course code."
                  : "Correct the alias text, source, confidence, or verified state."}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-3 py-4">
              {editId === null ? (
                <div className="space-y-1.5">
                  <Label htmlFor="cc">Course code</Label>
                  <Input
                    id="cc"
                    value={form.course_code}
                    onChange={(e) => setForm({ ...form, course_code: e.target.value })}
                    placeholder="001A"
                    required
                  />
                </div>
              ) : null}
              <div className="space-y-1.5">
                <Label htmlFor="at">Alias text</Label>
                <Input
                  id="at"
                  value={form.alias_text}
                  onChange={(e) => setForm({ ...form, alias_text: e.target.value })}
                  required
                />
              </div>
              <div className="flex gap-3">
                <div className="flex-1 space-y-1.5">
                  <Label htmlFor="src">Source</Label>
                  <Input
                    id="src"
                    value={form.source}
                    onChange={(e) => setForm({ ...form, source: e.target.value })}
                  />
                </div>
                <div className="w-32 space-y-1.5">
                  <Label htmlFor="conf">Confidence</Label>
                  <Input
                    id="conf"
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={form.confidence}
                    onChange={(e) => setForm({ ...form, confidence: e.target.value })}
                  />
                </div>
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.is_verified}
                  onChange={(e) => setForm({ ...form, is_verified: e.target.checked })}
                />
                Verified
              </label>
              {dialogErr ? <p className="text-sm text-destructive">{dialogErr}</p> : null}
            </div>
            <DialogFooter>
              <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={saving}>
                {saving ? "Saving…" : "Save"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
