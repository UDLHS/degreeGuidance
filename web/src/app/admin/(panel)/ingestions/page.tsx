"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Upload } from "lucide-react";

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

type Run = {
  run_id: string;
  run_type: string;
  status: string;
  year: number | null;
  records_processed: number | null;
  records_failed: number | null;
  source_label: string | null;
  started_at: string;
};

const STATUS_STYLES: Record<string, string> = {
  success: "bg-green-100 text-green-800",
  running: "bg-amber-100 text-amber-800",
  partial: "bg-amber-100 text-amber-800",
  failed: "bg-red-100 text-red-800",
};

function StatusPill({ status }: { status: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium",
        STATUS_STYLES[status] ?? "bg-muted text-muted-foreground",
      )}
    >
      {status}
    </span>
  );
}

export default function IngestionsPage() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);
  const [file, setFile] = useState<File | null>(null);
  const [year, setYear] = useState("2023");
  const [uploading, setUploading] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/bff/admin/ingestions?limit=50", { cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        setRuns(data.items ?? []);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function onUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setMsg(null);
    const fd = new FormData();
    fd.append("file", file);
    fd.append("exam_year", year);
    const res = await fetch("/api/bff/admin/ingestions", { method: "POST", body: fd });
    const data = await res.json().catch(() => null);
    setUploading(false);
    if (res.ok) {
      setMsg({
        ok: true,
        text:
          data?.run_type === "pdf_extraction"
            ? `PDF uploaded — extraction running (run ${String(data.run_id).slice(0, 8)}…).`
            : `CSV ingested: ${data.processed} processed, ${data.failed} failed.`,
      });
      setFile(null);
      const input = document.getElementById("file") as HTMLInputElement | null;
      if (input) input.value = "";
      load();
    } else {
      setMsg({ ok: false, text: data?.detail ?? `Upload failed (${res.status}).` });
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-medium">Ingestions</h1>
        <p className="text-sm text-muted-foreground">
          Upload a handbook PDF (extracted in the background) or a reviewed CSV (committed immediately).
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">New ingestion</CardTitle>
          <CardDescription>Accepted: .pdf (async extraction) or .csv (sync Step 4 load).</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onUpload} className="flex flex-wrap items-end gap-3">
            <div className="min-w-56 flex-1 space-y-1.5">
              <Label htmlFor="file">Handbook PDF or reviewed CSV</Label>
              <Input
                id="file"
                type="file"
                accept=".csv,.pdf"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              />
            </div>
            <div className="w-28 space-y-1.5">
              <Label htmlFor="year">Exam year</Label>
              <Input
                id="year"
                type="number"
                value={year}
                onChange={(e) => setYear(e.target.value)}
                min={2010}
                max={2030}
              />
            </div>
            <Button type="submit" disabled={!file || uploading}>
              <Upload className="mr-1 h-4 w-4" aria-hidden />
              {uploading ? "Uploading…" : "Upload"}
            </Button>
          </form>
          {msg ? (
            <p className={cn("mt-3 text-sm", msg.ok ? "text-green-700" : "text-destructive")}>{msg.text}</p>
          ) : null}
        </CardContent>
      </Card>

      <div>
        <div className="mb-2 flex items-center justify-between">
          <p className="text-sm font-medium">Recent runs</p>
          <Button variant="ghost" size="sm" onClick={load} disabled={loading}>
            {loading ? "Loading…" : "Refresh"}
          </Button>
        </div>
        <div className="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Source</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Year</TableHead>
                <TableHead className="text-right">Rows</TableHead>
                <TableHead className="text-right">View</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {runs.length === 0 && !loading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-sm text-muted-foreground">
                    No ingestion runs yet.
                  </TableCell>
                </TableRow>
              ) : (
                runs.map((r) => (
                  <TableRow key={r.run_id}>
                    <TableCell className="font-mono text-xs">
                      {r.source_label ?? r.run_id.slice(0, 8)}
                    </TableCell>
                    <TableCell className="text-sm">{r.run_type}</TableCell>
                    <TableCell>
                      <StatusPill status={r.status} />
                    </TableCell>
                    <TableCell className="text-sm">{r.year ?? "—"}</TableCell>
                    <TableCell className="text-right text-sm">
                      {r.records_processed ?? "—"}
                      {r.records_failed ? (
                        <span className="text-destructive"> / {r.records_failed}</span>
                      ) : null}
                    </TableCell>
                    <TableCell className="text-right">
                      <Link href={`/admin/ingestions/${r.run_id}`} className="text-sm text-primary">
                        View
                      </Link>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          Run detail, parse-error review, CSV download, and promote are coming next.
        </p>
      </div>
    </div>
  );
}
