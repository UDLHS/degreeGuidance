"use client";

import { useCallback, useEffect, useState } from "react";
import { ChevronDown, ChevronRight, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type SourceItem = {
  source_id: number;
  source_type: string;
  course_number: string | null;
  title: string;
  indexed_at: string;
  chunk_count: number;
  embedded_count: number;
  stale: boolean;
  orphaned: boolean;
};
type Knowledge = {
  totals: Record<string, number>;
  items: SourceItem[];
  never_indexed: string[];
};
type ChunkItem = {
  chunk_index: number;
  heading: string | null;
  token_count: number | null;
  has_embedding: boolean;
  content: string;
};

export default function KnowledgePage() {
  const [data, setData] = useState<Knowledge | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [open, setOpen] = useState<number | null>(null);
  const [chunks, setChunks] = useState<Record<number, ChunkItem[]>>({});
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const load = useCallback(async () => {
    const res = await fetch("/api/bff/admin/knowledge", { cache: "no-store" });
    if (res.ok) setData(await res.json());
    else setErr(`Failed to load knowledge base (HTTP ${res.status})`);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function toggle(sourceId: number) {
    if (open === sourceId) {
      setOpen(null);
      return;
    }
    setOpen(sourceId);
    if (!chunks[sourceId]) {
      const res = await fetch(`/api/bff/admin/knowledge/${sourceId}/chunks`, {
        cache: "no-store",
      });
      if (res.ok) setChunks((p) => ({ ...p, [sourceId]: [] as ChunkItem[] }));
      if (res.ok) {
        const d = await res.json();
        setChunks((p) => ({ ...p, [sourceId]: d }));
      }
    }
  }

  async function reindexStale() {
    setBusy(true);
    setMsg(null);
    const res = await fetch("/api/bff/admin/knowledge/reindex-stale", { method: "POST" });
    const d = await res.json().catch(() => null);
    setBusy(false);
    if (res.ok) {
      setMsg(
        d.enqueued === 0
          ? "Nothing stale — the knowledge base matches every factsheet."
          : `Queued ${d.enqueued} course(s) for re-embedding — refresh in a minute.`,
      );
    } else {
      setMsg(d?.detail ?? `Reindex failed (${res.status}).`);
    }
  }

  const staleCount = (data?.totals.stale ?? 0) + (data?.totals.never_indexed ?? 0);

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-medium">Knowledge base</h1>
          <p className="text-sm text-muted-foreground">
            What the AI advisor actually retrieves from — each factsheet, chunked and
            embedded. Stale = the factsheet was edited but this index hasn&apos;t caught up.
          </p>
        </div>
        <Button size="sm" variant={staleCount ? "default" : "outline"} onClick={reindexStale} disabled={busy}>
          <RefreshCw className={cn("mr-1 h-4 w-4", busy && "animate-spin")} aria-hidden />
          Reindex stale{staleCount ? ` (${staleCount})` : ""}
        </Button>
      </div>

      {data ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {Object.entries(data.totals).map(([k, v]) => (
            <Card key={k}>
              <CardHeader className="pb-1">
                <CardTitle className="text-xs font-medium capitalize text-muted-foreground">
                  {k.replace(/_/g, " ")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <span
                  className={cn(
                    "text-xl font-semibold tabular-nums",
                    (k === "stale" || k === "never_indexed") && v > 0 && "text-amber-600",
                  )}
                >
                  {v}
                </span>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : null}

      {msg ? <p className="text-sm text-green-700">{msg}</p> : null}
      {err ? <p className="text-sm text-destructive">{err}</p> : null}
      {data && data.never_indexed.length > 0 ? (
        <p className="rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-800">
          Never indexed: {data.never_indexed.join(", ")}
        </p>
      ) : null}

      <ArticlesPanel onChanged={load} />

      <div className="space-y-1.5">
        {data?.items.map((s) => (
          <div key={s.source_id} className="rounded-lg border">
            <button
              onClick={() => toggle(s.source_id)}
              className="flex w-full flex-wrap items-center justify-between gap-2 px-4 py-2.5 text-left hover:bg-accent/40"
            >
              <div className="flex min-w-0 items-center gap-2">
                {open === s.source_id ? (
                  <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" aria-hidden />
                ) : (
                  <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" aria-hidden />
                )}
                <span className="font-mono text-sm font-semibold">{s.course_number ?? "—"}</span>
                <span className="truncate text-sm">{s.title}</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>
                  {s.chunk_count} chunks · {s.embedded_count} embedded
                </span>
                <span>{new Date(s.indexed_at).toLocaleDateString()}</span>
                {s.stale ? (
                  <span className="rounded-md bg-amber-100 px-1.5 py-0.5 text-[10px] font-medium text-amber-800">
                    stale
                  </span>
                ) : s.orphaned ? (
                  <span className="rounded-md bg-zinc-200 px-1.5 py-0.5 text-[10px] font-medium text-zinc-600">
                    orphaned
                  </span>
                ) : (
                  <span className="rounded-md bg-green-100 px-1.5 py-0.5 text-[10px] font-medium text-green-800">
                    fresh
                  </span>
                )}
              </div>
            </button>
            {open === s.source_id ? (
              <div className="space-y-2 border-t px-4 py-3">
                {(chunks[s.source_id] ?? []).map((c) => (
                  <div key={c.chunk_index} className="rounded-md bg-muted/40 p-3">
                    <div className="mb-1 flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
                      <span className="font-mono">#{c.chunk_index}</span>
                      {c.heading ? <span className="font-medium">{c.heading}</span> : null}
                      <span>{c.token_count ?? "?"} tokens</span>
                      {!c.has_embedding ? (
                        <span className="rounded bg-red-100 px-1 text-red-800">no embedding</span>
                      ) : null}
                    </div>
                    <p className="line-clamp-4 whitespace-pre-wrap text-xs leading-relaxed">
                      {c.content}
                    </p>
                  </div>
                ))}
                {chunks[s.source_id]?.length === 0 ? (
                  <p className="text-xs text-muted-foreground">No chunks.</p>
                ) : null}
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Articles (Phase 8.6) — admin-authored knowledge beyond courses ───────────

type ArticleItem = {
  article_id: number;
  title: string;
  version: number;
  updated_at: string;
  index_status: "indexed" | "stale" | "never_indexed";
};

function ArticlesPanel({ onChanged }: { onChanged: () => void }) {
  const [items, setItems] = useState<ArticleItem[]>([]);
  const [editorOpen, setEditorOpen] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [panelMsg, setPanelMsg] = useState<string | null>(null);

  const loadArticles = useCallback(async () => {
    const res = await fetch("/api/bff/admin/articles", { cache: "no-store" });
    if (res.ok) setItems((await res.json()).items ?? []);
  }, []);

  useEffect(() => {
    loadArticles();
  }, [loadArticles]);

  function openNew() {
    setEditId(null);
    setTitle("");
    setContent("");
    setPanelMsg(null);
    setEditorOpen(true);
  }

  async function openExisting(id: number) {
    const res = await fetch(`/api/bff/admin/articles/${id}`, { cache: "no-store" });
    if (!res.ok) return;
    const d = await res.json();
    setEditId(id);
    setTitle(d.title);
    setContent(d.content);
    setPanelMsg(null);
    setEditorOpen(true);
  }

  async function save() {
    setSaving(true);
    const res = await fetch(
      editId === null ? "/api/bff/admin/articles" : `/api/bff/admin/articles/${editId}`,
      {
        method: editId === null ? "POST" : "PUT",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ title, content }),
      },
    );
    setSaving(false);
    if (res.ok) {
      setEditorOpen(false);
      setPanelMsg("Saved — re-embedding queued; the advisor picks it up in about a minute.");
      loadArticles();
      onChanged();
    } else {
      const d = await res.json().catch(() => null);
      setPanelMsg(typeof d?.detail === "string" ? d.detail : `Save failed (${res.status}).`);
    }
  }

  async function remove(id: number) {
    if (!confirm("Delete this article? Its knowledge-base entries are removed immediately."))
      return;
    const res = await fetch(`/api/bff/admin/articles/${id}`, { method: "DELETE" });
    if (res.ok) {
      setPanelMsg("Article deleted (index cleaned).");
      loadArticles();
      onChanged();
    } else {
      setPanelMsg(`Delete failed (${res.status}).`);
    }
  }

  const STATUS_BADGE: Record<ArticleItem["index_status"], string> = {
    indexed: "bg-green-100 text-green-800",
    stale: "bg-amber-100 text-amber-800",
    never_indexed: "bg-zinc-200 text-zinc-600",
  };

  return (
    <div className="rounded-lg border p-4">
      <div className="mb-1 flex items-center justify-between gap-2">
        <p className="text-sm font-semibold">Articles — knowledge beyond courses</p>
        <Button size="sm" onClick={openNew}>
          New article
        </Button>
      </div>
      <p className="mb-3 text-xs text-muted-foreground">
        Aptitude-test guides, UGC procedures, scholarship rules, deadlines… anything the AI
        advisor should know that isn&apos;t a course factsheet. Saving re-embeds automatically.
      </p>
      {panelMsg ? <p className="mb-2 text-xs text-green-700">{panelMsg}</p> : null}
      {items.length === 0 ? (
        <p className="text-xs text-muted-foreground">No articles yet.</p>
      ) : (
        <div className="space-y-1.5">
          {items.map((a) => (
            <div
              key={a.article_id}
              className="flex flex-wrap items-center justify-between gap-2 rounded-md border px-3 py-2"
            >
              <button
                onClick={() => openExisting(a.article_id)}
                className="min-w-0 flex-1 truncate text-left text-sm font-medium hover:underline"
              >
                {a.title}
              </button>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>v{a.version}</span>
                <span>{new Date(a.updated_at).toLocaleDateString()}</span>
                <span
                  className={cn(
                    "rounded-md px-1.5 py-0.5 text-[10px] font-medium",
                    STATUS_BADGE[a.index_status],
                  )}
                >
                  {a.index_status.replace("_", " ")}
                </span>
                <Button variant="ghost" size="sm" onClick={() => remove(a.article_id)}>
                  Delete
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {editorOpen ? (
        <div className="mt-3 space-y-2 rounded-md border bg-muted/30 p-3">
          <p className="text-sm font-semibold">{editId === null ? "New article" : "Edit article"}</p>
          <input
            className="w-full rounded-md border px-3 py-1.5 text-sm"
            placeholder="Title, e.g. Aptitude tests — how they work"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <textarea
            className="h-64 w-full rounded-md border px-3 py-2 font-mono text-xs"
            placeholder={"Markdown. Use ## section headings — each becomes one retrieval chunk."}
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
          <div className="flex justify-end gap-2">
            <Button variant="ghost" size="sm" onClick={() => setEditorOpen(false)}>
              Cancel
            </Button>
            <Button size="sm" onClick={save} disabled={saving || !title.trim() || !content.trim()}>
              {saving ? "Saving…" : "Save & re-embed"}
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
