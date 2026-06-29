"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Check, ChevronDown, MinusCircle, PlusCircle, TrendingUp, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

type ChangeType = "course_added" | "course_removed" | "cutoff_changed";
type ChangeStatus = "pending" | "approved" | "rejected" | "applied";

type CutoffDelta = { district: string; old: number | null; new: number | null };

type Change = {
  change_id: number;
  change_type: ChangeType;
  course_code: string;
  summary: string | null;
  before_value: Record<string, unknown> | null;
  after_value: Record<string, unknown> | null;
  status: ChangeStatus;
};

type ChangesResponse = { total: number; counts: Record<string, number>; items: Change[] };
type University = { university_id: number; university_code: string | null };

const STATUS_STYLES: Record<ChangeStatus, string> = {
  pending: "bg-amber-100 text-amber-800",
  approved: "bg-blue-100 text-blue-800",
  rejected: "bg-zinc-200 text-zinc-600",
  applied: "bg-green-100 text-green-800",
};

const GROUPS: { type: ChangeType; label: string; icon: typeof PlusCircle; accent: string }[] = [
  { type: "course_added", label: "New courses", icon: PlusCircle, accent: "text-green-700" },
  { type: "course_removed", label: "Removed courses", icon: MinusCircle, accent: "text-red-700" },
  { type: "cutoff_changed", label: "Cutoff changes", icon: TrendingUp, accent: "text-amber-700" },
];

function Badge({ status }: { status: ChangeStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium capitalize",
        STATUS_STYLES[status],
      )}
    >
      {status}
    </span>
  );
}

export function ChangeSetReview({ runId }: { runId: string }) {
  const [data, setData] = useState<ChangesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [universities, setUniversities] = useState<University[]>([]);
  const [forms, setForms] = useState<Record<number, { university_id: string; name_en: string }>>({});
  const [busyId, setBusyId] = useState<number | null>(null);
  const [applying, setApplying] = useState(false);
  const [open, setOpen] = useState<Record<number, boolean>>({});
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const load = useCallback(async () => {
    const res = await fetch(`/api/bff/admin/ingestions/${runId}/changes`, { cache: "no-store" });
    if (res.ok) {
      const d: ChangesResponse = await res.json();
      setData(d);
      // seed the inline add-course forms from any details already on the change
      setForms((prev) => {
        const next = { ...prev };
        for (const c of d.items) {
          if (c.change_type === "course_added" && !next[c.change_id]) {
            next[c.change_id] = {
              university_id: String((c.after_value?.university_id as number) ?? ""),
              name_en: String((c.after_value?.name_en as string) ?? ""),
            };
          }
        }
        return next;
      });
    }
    setLoading(false);
  }, [runId]);

  useEffect(() => {
    load();
  }, [load]);

  // university dropdown — deduped from the courses list (no dedicated endpoint)
  useEffect(() => {
    (async () => {
      const res = await fetch("/api/bff/admin/courses?limit=200", { cache: "no-store" });
      if (!res.ok) return;
      const d = await res.json();
      const seen = new Map<number, University>();
      for (const c of d.items ?? []) {
        if (!seen.has(c.university_id))
          seen.set(c.university_id, { university_id: c.university_id, university_code: c.university_code });
      }
      setUniversities(
        Array.from(seen.values()).sort((a, b) =>
          (a.university_code ?? "").localeCompare(b.university_code ?? ""),
        ),
      );
    })();
  }, []);

  async function review(change: Change, status: "approved" | "rejected") {
    setBusyId(change.change_id);
    setMsg(null);
    const body: Record<string, unknown> = { status };
    if (change.change_type === "course_added" && status === "approved") {
      const f = forms[change.change_id];
      body.university_id = f?.university_id ? Number(f.university_id) : null;
      body.name_en = f?.name_en?.trim() || null;
    }
    const res = await fetch(`/api/bff/admin/ingestions/${runId}/changes/${change.change_id}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    setBusyId(null);
    if (!res.ok) {
      const e = await res.json().catch(() => null);
      setMsg({ ok: false, text: e?.detail ?? `Update failed (${res.status}).` });
      return;
    }
    await load();
  }

  async function apply() {
    if (!confirm("Apply all approved changes? Removed courses will be hidden from students and new course stubs created.")) return;
    setApplying(true);
    setMsg(null);
    const res = await fetch(`/api/bff/admin/ingestions/${runId}/changes/apply`, { method: "POST" });
    const d = await res.json().catch(() => null);
    setApplying(false);
    if (!res.ok) {
      setMsg({ ok: false, text: d?.detail ?? `Apply failed (${res.status}).` });
      return;
    }
    const skipped = (d.skipped ?? []) as { course_code: string; reason: string }[];
    setMsg({
      ok: true,
      text:
        `Applied: ${d.applied_removed} removed, ${d.applied_added} added.` +
        (skipped.length ? ` Skipped ${skipped.length}: ${skipped.map((s) => `${s.course_code} (${s.reason})`).join(", ")}` : ""),
    });
    await load();
  }

  const approvedApplyable = useMemo(
    () =>
      (data?.items ?? []).filter(
        (c) => c.status === "approved" && (c.change_type === "course_added" || c.change_type === "course_removed"),
      ).length,
    [data],
  );

  if (loading) return <p className="text-sm text-muted-foreground">Loading change-set…</p>;
  if (!data || data.total === 0)
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Handbook changes</CardTitle>
          <CardDescription>No differences from the current data were detected in this handbook.</CardDescription>
        </CardHeader>
      </Card>
    );

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <CardTitle className="text-base">Handbook changes</CardTitle>
            <CardDescription>
              Review what changed vs the live data, then apply. Nothing changes for students until you apply.
            </CardDescription>
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            {(Object.entries(data.counts) as [ChangeStatus, number][]).map(([s, n]) => (
              <span key={s} className={cn("rounded-md px-2 py-0.5 text-xs font-medium capitalize", STATUS_STYLES[s])}>
                {n} {s}
              </span>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {GROUPS.map(({ type, label, icon: Icon, accent }) => {
          const items = data.items.filter((c) => c.change_type === type);
          if (items.length === 0) return null;
          return (
            <div key={type}>
              <div className={cn("mb-2 flex items-center gap-2 text-sm font-semibold", accent)}>
                <Icon className="h-4 w-4" aria-hidden /> {label}
                <span className="text-muted-foreground">({items.length})</span>
              </div>
              <div className="space-y-2">
                {items.map((c) => {
                  const isAdded = c.change_type === "course_added";
                  const isCutoff = c.change_type === "cutoff_changed";
                  const actionable = c.status === "pending" || c.status === "approved" || c.status === "rejected";
                  const form = forms[c.change_id] ?? { university_id: "", name_en: "" };
                  const addReady = !isAdded || (form.university_id && form.name_en.trim());
                  const details = (c.after_value?.details as CutoffDelta[] | undefined) ?? [];
                  return (
                    <div key={c.change_id} className="rounded-lg border p-3">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-xs font-semibold">{c.course_code}</span>
                            <Badge status={c.status} />
                          </div>
                          <p className="mt-0.5 text-sm text-muted-foreground">{c.summary}</p>

                          {isCutoff && details.length > 0 && (
                            <button
                              type="button"
                              onClick={() => setOpen((o) => ({ ...o, [c.change_id]: !o[c.change_id] }))}
                              className="mt-1 inline-flex items-center gap-1 text-xs text-primary"
                            >
                              <ChevronDown
                                className={cn("h-3 w-3 transition-transform", open[c.change_id] && "rotate-180")}
                                aria-hidden
                              />
                              {open[c.change_id] ? "Hide" : "Show"} {details.length} district changes
                            </button>
                          )}
                          {isCutoff && open[c.change_id] && (
                            <div className="mt-2 grid grid-cols-2 gap-x-6 gap-y-0.5 text-xs sm:grid-cols-3">
                              {details.map((d) => (
                                <div key={d.district} className="flex justify-between gap-2">
                                  <span className="text-muted-foreground">{d.district}</span>
                                  <span className="font-mono">
                                    {d.old ?? "—"} → {d.new ?? "—"}
                                  </span>
                                </div>
                              ))}
                            </div>
                          )}

                          {isAdded && c.status !== "applied" && (
                            <div className="mt-2 flex flex-wrap items-center gap-2">
                              <Select
                                value={form.university_id}
                                onValueChange={(v) =>
                                  setForms((p) => ({ ...p, [c.change_id]: { ...form, university_id: v } }))
                                }
                              >
                                <SelectTrigger className="h-8 w-[150px] text-xs">
                                  <SelectValue placeholder="University…" />
                                </SelectTrigger>
                                <SelectContent>
                                  {universities.map((u) => (
                                    <SelectItem key={u.university_id} value={String(u.university_id)}>
                                      {u.university_code ?? `#${u.university_id}`}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                              <Input
                                value={form.name_en}
                                onChange={(e) =>
                                  setForms((p) => ({ ...p, [c.change_id]: { ...form, name_en: e.target.value } }))
                                }
                                placeholder="Course name"
                                className="h-8 w-[240px] text-xs"
                              />
                            </div>
                          )}
                        </div>

                        {actionable && c.status !== "applied" && (
                          <div className="flex shrink-0 items-center gap-1.5">
                            {c.status !== "approved" && (
                              <Button
                                size="sm"
                                variant="outline"
                                disabled={busyId === c.change_id || !addReady}
                                onClick={() => review(c, "approved")}
                                title={isAdded && !addReady ? "Pick a university and enter a name first" : undefined}
                              >
                                <Check className="mr-1 h-3.5 w-3.5" aria-hidden /> Approve
                              </Button>
                            )}
                            {c.status !== "rejected" && (
                              <Button
                                size="sm"
                                variant="ghost"
                                disabled={busyId === c.change_id}
                                onClick={() => review(c, "rejected")}
                              >
                                <X className="mr-1 h-3.5 w-3.5" aria-hidden /> Reject
                              </Button>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}

        <div className="flex flex-wrap items-center gap-3 border-t pt-4">
          <Button onClick={apply} disabled={applying || approvedApplyable === 0}>
            {applying ? "Applying…" : `Apply ${approvedApplyable} approved change${approvedApplyable === 1 ? "" : "s"}`}
          </Button>
          <span className="text-xs text-muted-foreground">
            Removed → hidden from students (kept for the AI). Added → created as inactive, complete later on Courses.
          </span>
        </div>
        {msg && <p className={cn("text-sm", msg.ok ? "text-green-700" : "text-destructive")}>{msg.text}</p>}
      </CardContent>
    </Card>
  );
}
