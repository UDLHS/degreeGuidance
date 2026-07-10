"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, RefreshCw, Save } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type Detail = {
  course_number: string;
  content: string;
  version: number;
  content_hash: string;
  updated_at: string;
  index_status: string;
  chunk_count: number;
};

export default function FactsheetEditPage() {
  const { courseNumber } = useParams<{ courseNumber: string }>();
  const [detail, setDetail] = useState<Detail | null>(null);
  const [content, setContent] = useState("");
  const [isNew, setIsNew] = useState(false);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const load = useCallback(async () => {
    const res = await fetch(`/api/bff/admin/factsheets/${courseNumber}`, { cache: "no-store" });
    if (res.ok) {
      const d: Detail = await res.json();
      setDetail(d);
      setContent(d.content);
      setIsNew(false);
    } else if (res.status === 404) {
      setIsNew(true);
      setContent(`# Course ${courseNumber}\n\n## Overview\n\n(write the factsheet here)\n`);
    } else {
      setMsg({ ok: false, text: `Failed to load (HTTP ${res.status})` });
    }
  }, [courseNumber]);

  useEffect(() => {
    load();
  }, [load]);

  async function save() {
    setSaving(true);
    setMsg(null);
    const res = await fetch(`/api/bff/admin/factsheets/${courseNumber}`, {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ content }),
    });
    const d = await res.json().catch(() => null);
    setSaving(false);
    if (!res.ok) {
      setMsg({ ok: false, text: d?.detail ?? `Save failed (${res.status}).` });
      return;
    }
    setDetail(d);
    setIsNew(false);
    setMsg({
      ok: true,
      text: `Saved v${d.version} — reindex queued; the AI advisor sees this within a minute.`,
    });
  }

  async function reindex() {
    setMsg(null);
    const res = await fetch(`/api/bff/admin/factsheets/${courseNumber}/reindex`, {
      method: "POST",
    });
    if (res.ok) setMsg({ ok: true, text: "Reindex queued." });
    else setMsg({ ok: false, text: `Reindex failed (${res.status}).` });
  }

  const dirty = detail ? content !== detail.content : content.trim().length > 0;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <Link
            href="/admin/factsheets"
            className="mb-2 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" aria-hidden /> Back to factsheets
          </Link>
          <h1 className="font-mono text-xl font-medium">Factsheet {courseNumber}</h1>
          {detail ? (
            <p className="text-xs text-muted-foreground">
              v{detail.version} · {detail.index_status} · {detail.chunk_count} chunks · updated{" "}
              {new Date(detail.updated_at).toLocaleString()}
            </p>
          ) : isNew ? (
            <p className="text-xs text-muted-foreground">No factsheet yet — writing a new one.</p>
          ) : null}
        </div>
        <div className="flex gap-2">
          {detail ? (
            <Button size="sm" variant="outline" onClick={reindex}>
              <RefreshCw className="mr-1 h-4 w-4" aria-hidden /> Reindex
            </Button>
          ) : null}
          <Button size="sm" onClick={save} disabled={saving || !dirty || content.trim().length < 50}>
            <Save className="mr-1 h-4 w-4" aria-hidden />
            {saving ? "Saving…" : isNew ? "Create factsheet" : "Save new version"}
          </Button>
        </div>
      </div>

      {msg ? (
        <p className={cn("text-sm", msg.ok ? "text-green-700" : "text-destructive")}>{msg.text}</p>
      ) : null}

      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        rows={30}
        spellCheck={false}
        className="w-full rounded-md border bg-background p-4 font-mono text-[13px] leading-relaxed"
      />
      <p className="text-xs text-muted-foreground">
        Markdown, chunked by <code>## headings</code> for the knowledge base — keep section
        structure. Saving bumps the version, audits the change, and reindexes this course only.
      </p>
    </div>
  );
}
