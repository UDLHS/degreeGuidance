"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Download, Play } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
  parse_error_count: number;
  parse_errors: ParseError[];
};

const STATUS_STYLES: Record<string, string> = {
  success: "bg-green-100 text-green-800",
  running: "bg-amber-100 text-amber-800",
  partial: "bg-amber-100 text-amber-800",
  failed: "bg-red-100 text-red-800",
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
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

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

  async function promote() {
    setPromoting(true);
    setMsg(null);
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
