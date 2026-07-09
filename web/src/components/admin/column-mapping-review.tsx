"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Archive, Check, CheckCheck, EyeOff, RotateCcw, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

type Column = {
  column_id: number;
  column_key: string;
  page_number: number;
  raw_label: string;
  markers: string | null;
  suggested_course_code: string | null;
  suggestion_confidence: number | null;
  mapped_course_code: string | null;
  status: "pending" | "confirmed" | "ignored" | "unmapped_kept";
  override_streams: string | null;
  suggested_override_streams: string[];
  has_data: boolean | null;
};

type ColumnsResponse = {
  run_status: string;
  cutoff_pages: string | null;
  total: number;
  counts: Record<string, number>;
  duplicate_mappings: Record<string, number>;
  items: Column[];
};

const STATUS_STYLES: Record<string, string> = {
  pending: "bg-amber-100 text-amber-800",
  confirmed: "bg-green-100 text-green-800",
  ignored: "bg-zinc-200 text-zinc-600",
  unmapped_kept: "bg-blue-100 text-blue-800",
};

const STATUS_LABEL: Record<string, string> = {
  unmapped_kept: "kept (no code)",
};

export function ColumnMappingReview({
  runId,
  onFinalized,
}: {
  runId: string;
  onFinalized: () => void;
}) {
  const [data, setData] = useState<ColumnsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [bulkBusy, setBulkBusy] = useState(false);
  const [finalizing, setFinalizing] = useState(false);
  const [pendingOnly, setPendingOnly] = useState(true);
  const [edits, setEdits] = useState<Record<number, string>>({});
  const [streamEdits, setStreamEdits] = useState<Record<number, string>>({});
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const load = useCallback(async () => {
    const res = await fetch(`/api/bff/admin/ingestions/${runId}/columns`, { cache: "no-store" });
    if (res.ok) setData(await res.json());
    setLoading(false);
  }, [runId]);

  useEffect(() => {
    load();
  }, [load]);

  async function patchColumn(col: Column, body: Record<string, unknown>) {
    setBusyId(col.column_id);
    setMsg(null);
    const res = await fetch(`/api/bff/admin/ingestions/${runId}/columns/${col.column_id}`, {
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

  async function confirmSuggested() {
    setBulkBusy(true);
    setMsg(null);
    const res = await fetch(`/api/bff/admin/ingestions/${runId}/columns/confirm-suggested`, {
      method: "POST",
    });
    const d = await res.json().catch(() => null);
    setBulkBusy(false);
    if (!res.ok) {
      setMsg({ ok: false, text: d?.detail ?? `Bulk confirm failed (${res.status}).` });
      return;
    }
    setMsg({ ok: true, text: `Confirmed ${d.confirmed} exact matches — ${d.remaining_pending} left for review.` });
    await load();
  }

  async function finalize() {
    if (!confirm("Finalize the column mapping? This writes the reviewable CSV, learns new aliases, and computes the change-set.")) return;
    setFinalizing(true);
    setMsg(null);
    const res = await fetch(`/api/bff/admin/ingestions/${runId}/mapping/confirm`, { method: "POST" });
    const d = await res.json().catch(() => null);
    setFinalizing(false);
    if (!res.ok) {
      setMsg({ ok: false, text: d?.detail ?? `Finalize failed (${res.status}).` });
      return;
    }
    const ch = Object.entries(d.changes ?? {}).map(([k, v]) => `${k}: ${v}`).join(", ");
    setMsg({
      ok: true,
      text: `Mapping confirmed — ${d.columns_used} columns used, ${d.aliases_learned} aliases learned. Changes: ${ch || "none"}.`,
    });
    onFinalized();
  }

  const pendingCount = data?.counts?.pending ?? 0;
  const items = useMemo(() => {
    if (!data) return [];
    return pendingOnly ? data.items.filter((c) => c.status === "pending") : data.items;
  }, [data, pendingOnly]);

  if (loading) return <p className="text-sm text-muted-foreground">Loading columns…</p>;
  if (!data || data.total === 0) return null;

  const dupEntries = Object.entries(data.duplicate_mappings ?? {});

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <CardTitle className="text-base">Column → course mapping</CardTitle>
            <CardDescription>
              {data.total} extracted columns from pages {data.cutoff_pages ?? "—"}. Confirm what each
              column is; nothing is committed until you finalize and promote.
            </CardDescription>
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            {Object.entries(data.counts).map(([s, n]) => (
              <span key={s} className={cn("rounded-md px-2 py-0.5 text-xs font-medium capitalize", STATUS_STYLES[s] ?? "bg-muted")}>
                {n} {STATUS_LABEL[s] ?? s}
              </span>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {dupEntries.length > 0 && (
          <p className="rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-800">
            Multiple columns target the same course: {dupEntries.map(([c, n]) => `${c} ×${n}`).join(", ")}.
            If these are genuinely the same course with different per-stream cutoffs (e.g. Commerce vs
            Bio/Physical Science), give each one distinct stream codes below instead of ignoring — otherwise
            keep one and set the other to Ignore.
          </p>
        )}

        <div className="flex flex-wrap items-center gap-2">
          <Button size="sm" variant="outline" onClick={confirmSuggested} disabled={bulkBusy || pendingCount === 0}>
            <CheckCheck className="mr-1 h-4 w-4" aria-hidden />
            {bulkBusy ? "Confirming…" : "Confirm all exact matches"}
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setPendingOnly((v) => !v)}>
            {pendingOnly ? `Showing ${items.length} pending — show all` : "Show pending only"}
          </Button>
          <div className="ml-auto">
            <Button size="sm" onClick={finalize} disabled={finalizing || pendingCount > 0}
              title={pendingCount > 0 ? `${pendingCount} column(s) still pending` : undefined}>
              <Check className="mr-1 h-4 w-4" aria-hidden />
              {finalizing ? "Finalizing…" : "Finalize mapping"}
            </Button>
          </div>
        </div>

        <div className="max-h-[520px] space-y-1.5 overflow-y-auto pr-1">
          {items.map((c) => {
            const editVal = edits[c.column_id] ?? "";
            const streamEditVal =
              streamEdits[c.column_id] ??
              c.override_streams ??
              c.suggested_override_streams.join(",") ??
              "";
            const isDuplicateTarget = !!(c.mapped_course_code && data.duplicate_mappings?.[c.mapped_course_code]);
            return (
              <div key={c.column_id} className="rounded-lg border px-3 py-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-[11px] text-muted-foreground">{c.column_key}</span>
                      <span className={cn("rounded-md px-1.5 py-0.5 text-[10px] font-medium capitalize", STATUS_STYLES[c.status])}>
                        {STATUS_LABEL[c.status] ?? c.status}
                      </span>
                      {c.mapped_course_code && (
                        <span className="font-mono text-xs font-semibold">→ {c.mapped_course_code}</span>
                      )}
                      {c.override_streams && (
                        <span className="rounded-md bg-sky-100 px-1.5 py-0.5 text-[10px] font-medium text-sky-800">
                          streams: {c.override_streams}
                        </span>
                      )}
                    </div>
                    <p className="mt-0.5 truncate text-sm">{c.raw_label}</p>
                    {c.status === "pending" && c.suggested_course_code && (
                      <p className="mt-0.5 text-xs text-muted-foreground">
                        <Sparkles className="mr-1 inline h-3 w-3" aria-hidden />
                        suggestion: <span className="font-mono">{c.suggested_course_code}</span>
                        {c.suggestion_confidence != null ? ` (${Number(c.suggestion_confidence).toFixed(2)})` : ""}
                      </p>
                    )}
                  </div>

                  <div className="flex shrink-0 items-center gap-1.5">
                    {c.status === "pending" ? (
                      <>
                        {c.suggested_course_code && (
                          <Button size="sm" variant="outline" disabled={busyId === c.column_id}
                            onClick={() => patchColumn(c, { mapped_course_code: c.suggested_course_code })}>
                            <Check className="mr-1 h-3.5 w-3.5" aria-hidden /> Use {c.suggested_course_code}
                          </Button>
                        )}
                        <Input
                          value={editVal}
                          onChange={(e) => setEdits((p) => ({ ...p, [c.column_id]: e.target.value }))}
                          placeholder="code…"
                          className="h-8 w-24 font-mono text-xs uppercase"
                        />
                        <Button size="sm" variant="outline" disabled={busyId === c.column_id || !editVal.trim()}
                          onClick={() => patchColumn(c, { mapped_course_code: editVal.trim().toUpperCase() })}>
                          Set
                        </Button>
                        {c.has_data && (
                          <Button size="sm" variant="outline" disabled={busyId === c.column_id}
                            title="Preserve these z-scores without a Uni-Code (for a course not in the book's code list)"
                            onClick={() => patchColumn(c, { status: "unmapped_kept" })}>
                            <Archive className="mr-1 h-3.5 w-3.5" aria-hidden /> Keep (no code)
                          </Button>
                        )}
                        <Button size="sm" variant="ghost" disabled={busyId === c.column_id}
                          onClick={() => {
                            if (c.has_data && !confirm(
                              `This column has real z-score values` +
                              (data.cutoff_pages ? ` (pages ${data.cutoff_pages})` : "") +
                              `. Ignoring drops that cutoff data. If it's a real course with no ` +
                              `Uni-Code, use "Keep (no code)" instead. Ignore anyway?`
                            )) return;
                            patchColumn(c, { status: "ignored" });
                          }}>
                          <EyeOff className="mr-1 h-3.5 w-3.5" aria-hidden /> Ignore
                        </Button>
                      </>
                    ) : (
                      <Button size="sm" variant="ghost" disabled={busyId === c.column_id}
                        onClick={() => patchColumn(c, { status: "pending" })}>
                        <RotateCcw className="mr-1 h-3.5 w-3.5" aria-hidden /> Reopen
                      </Button>
                    )}
                  </div>
                </div>

                {c.status === "confirmed" && (isDuplicateTarget || c.override_streams) && (
                  <div className="mt-2 flex flex-wrap items-center gap-1.5 border-t pt-2">
                    <span className="text-[11px] text-muted-foreground">
                      Same course as another column? Give this one its own stream(s) instead of ignoring:
                    </span>
                    <Input
                      value={streamEditVal}
                      onChange={(e) => setStreamEdits((p) => ({ ...p, [c.column_id]: e.target.value }))}
                      placeholder={c.suggested_override_streams.join(",") || "e.g. COMMERCE"}
                      className="h-7 w-56 font-mono text-[11px] uppercase"
                    />
                    {c.suggested_override_streams.length > 0 && streamEditVal !== c.suggested_override_streams.join(",") && (
                      <Button size="sm" variant="outline" className="h-7 px-2 text-[11px]"
                        disabled={busyId === c.column_id}
                        onClick={() => setStreamEdits((p) => ({ ...p, [c.column_id]: c.suggested_override_streams.join(",") }))}>
                        <Sparkles className="mr-1 h-3 w-3" aria-hidden /> Use {c.suggested_override_streams.join(",")}
                      </Button>
                    )}
                    <Button size="sm" variant="outline" className="h-7 px-2 text-[11px]"
                      disabled={busyId === c.column_id}
                      onClick={() => patchColumn(c, { override_streams: streamEditVal.trim().toUpperCase() })}>
                      Save streams
                    </Button>
                    {c.override_streams && (
                      <Button size="sm" variant="ghost" className="h-7 px-2 text-[11px]"
                        disabled={busyId === c.column_id}
                        onClick={() => { setStreamEdits((p) => ({ ...p, [c.column_id]: "" })); patchColumn(c, { override_streams: "" }); }}>
                        Clear
                      </Button>
                    )}
                  </div>
                )}
              </div>
            );
          })}
          {items.length === 0 && (
            <p className="py-6 text-center text-sm text-muted-foreground">
              {pendingOnly ? "No pending columns — ready to finalize." : "No columns."}
            </p>
          )}
        </div>

        {msg && <p className={cn("text-sm", msg.ok ? "text-green-700" : "text-destructive")}>{msg.text}</p>}
      </CardContent>
    </Card>
  );
}
