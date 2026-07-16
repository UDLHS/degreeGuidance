"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Check, RefreshCw, Save, Sparkles, X } from "lucide-react";

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

// A machine-written draft awaiting a human (Phase 9.4). It lives in its own
// table and can NEVER be indexed — approving it here is the only door.
type Draft = {
  course_number: string;
  status: "queued" | "ready" | "failed" | "rejected";
  content: string | null;
  error: string | null;
  provenance: {
    run_id?: string | null;
    book_found?: boolean;
    book_page?: number | null;
    book_streams?: string[];
    book_streams_may_be_incomplete?: boolean;
    proposed_intake?: number | null;
    web_results?: number;
    web_note?: string;
    model?: string;
    generated_at?: string;
  } | null;
  updated_at: string;
};

export default function FactsheetEditPage() {
  const { courseNumber } = useParams<{ courseNumber: string }>();
  const [detail, setDetail] = useState<Detail | null>(null);
  const [content, setContent] = useState("");
  const [isNew, setIsNew] = useState(false);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [draftLoaded, setDraftLoaded] = useState(false);
  const [busy, setBusy] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

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

  const loadDraft = useCallback(async () => {
    const res = await fetch(`/api/bff/admin/factsheets/${courseNumber}/draft`, {
      cache: "no-store",
    });
    if (res.ok) setDraft(await res.json());
    else if (res.status === 404) setDraft(null);
  }, [courseNumber]);

  useEffect(() => {
    load();
    loadDraft();
  }, [load, loadDraft]);

  // While a draft is generating, poll until it lands (ready/failed).
  useEffect(() => {
    if (draft?.status === "queued" && !pollRef.current) {
      pollRef.current = setInterval(loadDraft, 5000);
    }
    if (draft?.status !== "queued" && pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [draft?.status, loadDraft]);

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

  async function generateDraft() {
    setBusy(true);
    setMsg(null);
    const res = await fetch(`/api/bff/admin/factsheets/${courseNumber}/generate-draft`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({}),
    });
    const d = await res.json().catch(() => null);
    setBusy(false);
    if (!res.ok) {
      setMsg({ ok: false, text: d?.detail ?? `Could not start generation (${res.status}).` });
      return;
    }
    setDraft(d);
    setDraftLoaded(false);
    setMsg({
      ok: true,
      text: "Draft generation started — it reads the handbook facts first, then the web. Usually under a minute.",
    });
  }

  function reviewDraft() {
    if (!draft?.content) return;
    setContent(draft.content);
    setDraftLoaded(true);
    setMsg({
      ok: true,
      text: "Draft loaded into the editor. Check every fact against the handbook page shown, edit freely, then Approve & publish.",
    });
  }

  async function approveDraft() {
    setBusy(true);
    setMsg(null);
    const res = await fetch(`/api/bff/admin/factsheets/${courseNumber}/draft/approve`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      // what the admin sees in the editor is exactly what goes live
      body: JSON.stringify({ content }),
    });
    const d = await res.json().catch(() => null);
    setBusy(false);
    if (!res.ok) {
      setMsg({ ok: false, text: d?.detail ?? `Approve failed (${res.status}).` });
      return;
    }
    setDetail(d);
    setIsNew(false);
    setDraft(null);
    setDraftLoaded(false);
    setMsg({
      ok: true,
      text: `Approved as v${d.version} — reindex queued; the AI advisor sees it within a minute.`,
    });
  }

  async function rejectDraft() {
    setBusy(true);
    setMsg(null);
    const res = await fetch(`/api/bff/admin/factsheets/${courseNumber}/draft/reject`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({}),
    });
    setBusy(false);
    if (!res.ok) {
      const d = await res.json().catch(() => null);
      setMsg({ ok: false, text: d?.detail ?? `Reject failed (${res.status}).` });
      return;
    }
    await loadDraft();
    setDraftLoaded(false);
    setMsg({ ok: true, text: "Draft rejected — it was never indexed. Generate a new one anytime." });
  }

  const dirty = detail ? content !== detail.content : content.trim().length > 0;
  const generating = draft?.status === "queued";
  const p = draft?.provenance;

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
          {!generating ? (
            <Button size="sm" variant="outline" onClick={generateDraft} disabled={busy}>
              <Sparkles className="mr-1 h-4 w-4" aria-hidden />
              {draft ? "Regenerate draft" : "Generate draft"}
            </Button>
          ) : null}
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

      {draft && draft.status !== "rejected" ? (
        <div
          className={cn(
            "rounded-lg border p-4",
            draft.status === "failed"
              ? "border-red-300 bg-red-50 dark:bg-red-950/20"
              : "border-violet-300 bg-violet-50 dark:bg-violet-950/20",
          )}
        >
          {draft.status === "queued" ? (
            <p className="text-sm">
              <span className="font-medium">Generating a draft…</span> reading the handbook facts
              first, then the catalog, then the web. This page updates itself.
            </p>
          ) : draft.status === "failed" ? (
            <div className="space-y-2">
              <p className="text-sm font-medium">Draft generation failed</p>
              <p className="font-mono text-xs">{draft.error}</p>
              <Button size="sm" variant="outline" onClick={generateDraft} disabled={busy}>
                <RefreshCw className="mr-1 h-4 w-4" aria-hidden /> Retry
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              <div>
                <p className="text-sm font-medium">
                  A machine-written draft is ready for review
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  It is NOT visible to students or the AI advisor until you approve it. Facts came
                  from{" "}
                  {p?.book_found
                    ? `the handbook (page ${p.book_page ?? "?"})`
                    : "the catalog only — no ingested handbook mentions this course"}
                  {typeof p?.web_results === "number"
                    ? `, plus ${p.web_results} web result${p.web_results === 1 ? "" : "s"} for background`
                    : ""}
                  . {p?.web_note ? `${p.web_note}. ` : ""}
                  Check every claim before approving — the model wrote the prose, not the facts.
                </p>
                {p?.book_streams_may_be_incomplete ? (
                  <p className="mt-1 text-xs font-medium text-amber-700">
                    The book also grants entry by subject list without naming a stream — the
                    draft&apos;s stream list may be incomplete. Verify against the page.
                  </p>
                ) : null}
              </div>
              <div className="flex flex-wrap gap-2">
                <Button size="sm" variant="outline" onClick={reviewDraft} disabled={busy}>
                  Review in editor
                </Button>
                <Button size="sm" onClick={approveDraft} disabled={busy || !draftLoaded}>
                  <Check className="mr-1 h-4 w-4" aria-hidden /> Approve &amp; publish
                </Button>
                <Button size="sm" variant="outline" onClick={rejectDraft} disabled={busy}>
                  <X className="mr-1 h-4 w-4" aria-hidden /> Reject
                </Button>
              </div>
              {!draftLoaded ? (
                <p className="text-xs text-muted-foreground">
                  Approve unlocks after you load the draft into the editor — what you see there is
                  exactly what goes live.
                </p>
              ) : null}
            </div>
          )}
        </div>
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
