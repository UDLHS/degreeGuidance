"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Download, Play } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChangeSetReview } from "@/components/admin/change-set-review";
import { ColumnMappingReview } from "@/components/admin/column-mapping-review";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

type ParseError = {
  error_id: number;
  error_type: string | null;
  raw_block: string | null;
  error_message: string | null;
  page_number: number | null;
};

type Detail = {
  run_id: string;
  run_type: string;
  status: string;
  year: number | null;
  records_processed: number | null;
  records_failed: number | null;
  source_label: string | null;
  notes: string | null;
  error_log: string | null;
  started_at: string;
  completed_at: string | null;
  cutoff_pages: string | null;
  parse_error_count: number;
  parse_errors: ParseError[];
};

const STATUS_STYLES: Record<string, string> = {
  success: "bg-green-100 text-green-800",
  running: "bg-amber-100 text-amber-800",
  partial: "bg-amber-100 text-amber-800",
  failed: "bg-red-100 text-red-800",
  needs_pages: "bg-red-100 text-red-800",
  needs_mapping: "bg-blue-100 text-blue-800",
};

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex justify-between gap-4 py-1.5 text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span className="text-right">{value}</span>
    </div>
  );
}

export default function RunDetailPage({ params }: { params: { runId: string } }) {
  const { runId } = params;
  const [detail, setDetail] = useState<Detail | null>(null);
  const [loading, setLoading] = useState(true);
  const [promoting, setPromoting] = useState(false);
  const [reviewFile, setReviewFile] = useState<File | null>(null);
  const [pagesSpec, setPagesSpec] = useState("");
  const [reextracting, setReextracting] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  // Post-promote review card (Phase 7.4) — returned by /promote.
  const [checklist, setChecklist] = useState<{
    promoted_year: number;
    students_now_see: number | null;
    is_default_year: boolean;
    coverage_gap_count: number;
    coverage_gaps: string[];
    stream_override_rows: number;
    codeless_rows: number;
    archived: string[];
    // Phase 8.3 — this book's newly-added courses and their onboarding state
    new_courses_total?: number;
    new_courses_onboarded?: number;
    new_courses_pending?: string[];
  } | null>(null);

  const load = useCallback(async () => {
    const res = await fetch(`/api/bff/admin/ingestions/${runId}`, { cache: "no-store" });
    if (res.ok) setDetail(await res.json());
    setLoading(false);
  }, [runId]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (detail?.status !== "running") return;
    const t = setInterval(load, 3000);
    return () => clearInterval(t);
  }, [detail?.status, load]);

  async function reextract() {
    if (!pagesSpec.trim()) return;
    setReextracting(true);
    setMsg(null);
    const res = await fetch(`/api/bff/admin/ingestions/${runId}/extract`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ cutoff_pages: pagesSpec.trim() }),
    });
    const data = await res.json().catch(() => null);
    setReextracting(false);
    if (res.ok) {
      setMsg({ ok: true, text: `Re-extracting pages ${pagesSpec.trim()} — this page refreshes automatically.` });
      setPagesSpec("");
    } else {
      setMsg({ ok: false, text: data?.detail ?? `Re-extract failed (${res.status}).` });
    }
    load();
  }

  async function promote() {
    setPromoting(true);
    setMsg(null);
    setChecklist(null);
    const fd = new FormData();
    if (reviewFile) fd.append("file", reviewFile);
    const res = await fetch(`/api/bff/admin/ingestions/${runId}/promote`, { method: "POST", body: fd });
    const data = await res.json().catch(() => null);
    setPromoting(false);
    if (res.ok) {
      setMsg({
        ok: true,
        text: `Promoted: ${data.processed} rows committed${data.failed ? `, ${data.failed} failed` : ""}. New run ${String(data.run_id).slice(0, 8)}…`,
      });
      if (data.checklist) setChecklist(data.checklist);
      setReviewFile(null);
    } else {
      setMsg({ ok: false, text: data?.detail ?? `Promote failed (${res.status}).` });
    }
    load();
  }

  if (loading) return <p className="text-sm text-muted-foreground">Loading…</p>;
  if (!detail)
    return (
      <div className="space-y-4">
        <Link href="/admin/ingestions" className="inline-flex items-center text-sm text-primary">
          <ArrowLeft className="mr-1 h-4 w-4" aria-hidden /> Back
        </Link>
        <p className="text-sm text-destructive">Run not found.</p>
      </div>
    );

  const isExtraction = detail.run_type === "pdf_extraction";
  const canPromote = isExtraction && detail.status === "success";
  const hasUnknownCourse = detail.parse_errors.some((e) => e.error_type === "unknown_course_alias");

  return (
    <div className="max-w-3xl space-y-6">
      <Link href="/admin/ingestions" className="inline-flex items-center text-sm text-primary">
        <ArrowLeft className="mr-1 h-4 w-4" aria-hidden /> Back to ingestions
      </Link>

      <div className="flex items-center gap-3">
        <h1 className="font-mono text-lg">{detail.run_id.slice(0, 8)}…</h1>
        <span
          className={cn(
            "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium",
            STATUS_STYLES[detail.status] ?? "bg-muted text-muted-foreground",
          )}
        >
          {detail.status}
        </span>
        <span className="text-sm text-muted-foreground">{detail.run_type}</span>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Run summary</CardTitle>
        </CardHeader>
        <CardContent className="divide-y">
          <Row label="Source" value={detail.source_label ?? "—"} />
          <Row label="Exam year" value={detail.year ?? "—"} />
          {detail.cutoff_pages ? <Row label="Cutoff pages" value={detail.cutoff_pages} /> : null}
          <Row label="Processed" value={detail.records_processed ?? "—"} />
          <Row label="Failed" value={detail.records_failed ?? "—"} />
          <Row label="Started" value={new Date(detail.started_at).toLocaleString()} />
          <Row
            label="Completed"
            value={detail.completed_at ? new Date(detail.completed_at).toLocaleString() : "—"}
          />
          {detail.notes ? <Row label="Notes" value={detail.notes} /> : null}
          {detail.error_log ? (
            <Row label="Error" value={<span className="text-destructive">{detail.error_log}</span>} />
          ) : null}
        </CardContent>
      </Card>

      {detail.status === "running" ? (
        <p className="text-sm text-muted-foreground">Extraction in progress — this page refreshes automatically.</p>
      ) : null}

      {isExtraction && (detail.status === "needs_pages" || detail.status === "needs_mapping") ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {detail.status === "needs_pages"
                ? "Cutoff table pages needed"
                : "Wrong pages? Re-extract"}
            </CardTitle>
            <CardDescription>
              {detail.status === "needs_pages"
                ? "Auto-detection couldn't parse a cutoff grid in this handbook. Open the PDF, find the cutoff tables, and enter their page range."
                : `Extracted from pages ${detail.cutoff_pages ?? "—"}. If tables live elsewhere too, re-extract with the full range — the mapping below resets.`}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap items-end gap-3">
            <div className="w-64 space-y-1.5">
              <Label htmlFor="pages">Page range(s), e.g. 179-188 or 150-156,179-188</Label>
              <Input
                id="pages"
                value={pagesSpec}
                onChange={(e) => setPagesSpec(e.target.value)}
                placeholder={detail.cutoff_pages ?? "179-188"}
              />
            </div>
            <Button onClick={reextract} disabled={reextracting || !pagesSpec.trim()}>
              {reextracting ? "Starting…" : "Re-extract"}
            </Button>
          </CardContent>
        </Card>
      ) : null}

      {isExtraction && detail.status === "needs_mapping" ? (
        <ColumnMappingReview runId={runId} onFinalized={load} />
      ) : null}

      {canPromote ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Review &amp; promote</CardTitle>
            <CardDescription>
              Download the extracted CSV, review it, then commit it to live cutoffs. Optionally re-upload a corrected CSV.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button asChild variant="outline">
              <a href={`/api/bff/admin/ingestions/${runId}/csv`}>
                <Download className="mr-1 h-4 w-4" aria-hidden /> Download CSV
              </a>
            </Button>
            <div className="space-y-1.5">
              <Label htmlFor="review">Reviewed CSV (optional — omit to promote the extracted CSV as-is)</Label>
              <Input
                id="review"
                type="file"
                accept=".csv"
                onChange={(e) => setReviewFile(e.target.files?.[0] ?? null)}
              />
            </div>
            <Button onClick={promote} disabled={promoting}>
              <Play className="mr-1 h-4 w-4" aria-hidden />
              {promoting ? "Promoting…" : "Promote to live cutoffs"}
            </Button>
            {msg ? (
              <p className={cn("text-sm", msg.ok ? "text-green-700" : "text-destructive")}>{msg.text}</p>
            ) : null}
          </CardContent>
        </Card>
      ) : null}

      {checklist ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Post-promote checklist — {checklist.promoted_year}</CardTitle>
            <CardDescription>Review these before you consider the yearly update done.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <p>
              ✅ Students now see <strong>{checklist.students_now_see}</strong> by default
              {checklist.is_default_year
                ? " (this promote)."
                : ` — this promote (${checklist.promoted_year}) is a previous year, selectable via the year switcher.`}
            </p>
            <p className={cn(checklist.coverage_gap_count > 0 && "text-amber-700")}>
              {checklist.coverage_gap_count > 0 ? "⚠️" : "✅"} {checklist.coverage_gap_count} active
              course(s) without {checklist.promoted_year} cutoffs
              {checklist.coverage_gaps.length
                ? ` — ${checklist.coverage_gaps.join(", ")}${checklist.coverage_gap_count > checklist.coverage_gaps.length ? ", …" : ""}. Verify each is expected (new course / variant code / no intake).`
                : "."}
            </p>
            <p>
              ✅ {checklist.stream_override_rows} per-stream override cutoff(s) ·{" "}
              {checklist.codeless_rows} codeless cutoff(s) preserved.
            </p>
            {(checklist.new_courses_total ?? 0) > 0 ? (
              <p
                className={cn(
                  (checklist.new_courses_pending?.length ?? 0) > 0 && "text-amber-700",
                )}
              >
                {(checklist.new_courses_pending?.length ?? 0) > 0 ? "⚠️" : "✅"} New courses in
                this book: <strong>{checklist.new_courses_onboarded}</strong> of{" "}
                <strong>{checklist.new_courses_total}</strong> fully onboarded
                {checklist.new_courses_pending?.length
                  ? ` — pending: ${checklist.new_courses_pending.join(", ")}. Finish them on the Courses page ("Needs onboarding").`
                  : "."}
              </p>
            ) : null}
            <p className="text-xs text-muted-foreground">
              Archived {checklist.archived.length} file(s): {checklist.archived.join(" · ") || "—"}
            </p>
          </CardContent>
        </Card>
      ) : null}

      {isExtraction && detail.status === "success" ? <ChangeSetReview runId={runId} /> : null}

      {detail.parse_error_count > 0 ? (
        <div>
          <p className="mb-2 text-sm font-medium">Parse errors ({detail.parse_error_count})</p>
          {hasUnknownCourse ? (
            <p className="mb-2 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-800">
              Some labels did not resolve to a known course — these are likely new courses. Add them on the{" "}
              <Link href="/admin/courses" className="underline">
                Courses
              </Link>{" "}
              page (with alias + flags), then re-promote.
            </p>
          ) : null}
          <div className="rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Type</TableHead>
                  <TableHead>Label / block</TableHead>
                  <TableHead>Message</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {detail.parse_errors.map((e) => (
                  <TableRow key={e.error_id}>
                    <TableCell className="text-xs">{e.error_type ?? "—"}</TableCell>
                    <TableCell className="font-mono text-xs">{e.raw_block ?? "—"}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">{e.error_message ?? "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      ) : null}
    </div>
  );
}
