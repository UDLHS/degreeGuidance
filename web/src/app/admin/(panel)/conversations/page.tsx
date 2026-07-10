"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Flag, RefreshCw, User } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

type Item = {
  conversation_id: string;
  started_at: string;
  updated_at: string;
  message_count: number;
  flagged: boolean;
  student_email: string | null;
  preview: string;
};
type ListResponse = { total: number; items: Item[] };

const PAGE = 50;

export default function ConversationsPage() {
  const [data, setData] = useState<ListResponse | null>(null);
  const [q, setQ] = useState("");
  const [flaggedOnly, setFlaggedOnly] = useState(false);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setErr(null);
    const p = new URLSearchParams({ limit: String(PAGE), offset: String(offset) });
    if (q.trim()) p.set("q", q.trim());
    if (flaggedOnly) p.set("flagged", "true");
    const res = await fetch(`/api/bff/admin/conversations?${p.toString()}`, { cache: "no-store" });
    if (res.ok) setData(await res.json());
    else setErr(`Failed to load conversations (HTTP ${res.status})`);
    setLoading(false);
  }, [q, flaggedOnly, offset]);

  useEffect(() => {
    const t = setTimeout(load, q ? 300 : 0);
    return () => clearTimeout(t);
  }, [load, q]);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-medium">Conversations</h1>
        <p className="text-sm text-muted-foreground">
          Every AI-advisor chat, for quality review. Flag anything that needs a fix
          (wrong tone, missing data, a question worth a factsheet).
        </p>
        <p className="mt-1 text-xs text-muted-foreground/80">
          Privacy: students type freely here — treat contents as personal data and only
          review what you need to.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Input
          value={q}
          onChange={(e) => {
            setOffset(0);
            setQ(e.target.value);
          }}
          placeholder="Search message text…"
          className="max-w-xs"
        />
        <Button
          size="sm"
          variant={flaggedOnly ? "default" : "outline"}
          onClick={() => {
            setOffset(0);
            setFlaggedOnly((v) => !v);
          }}
        >
          <Flag className="mr-1 h-4 w-4" aria-hidden /> Flagged only
        </Button>
        <Button size="sm" variant="ghost" onClick={load} disabled={loading}>
          <RefreshCw className={cn("mr-1 h-4 w-4", loading && "animate-spin")} aria-hidden />
          Refresh
        </Button>
        {data ? (
          <span className="text-sm text-muted-foreground">{data.total} total</span>
        ) : null}
      </div>

      {err ? <p className="text-sm text-destructive">{err}</p> : null}

      <div className="space-y-2">
        {data?.items.map((c) => (
          <Link
            key={c.conversation_id}
            href={`/admin/conversations/${c.conversation_id}`}
            className="block rounded-lg border px-4 py-3 transition-colors hover:bg-accent/40"
          >
            <div className="flex flex-wrap items-center gap-2">
              {c.flagged ? (
                <span className="inline-flex items-center gap-1 rounded-md bg-red-100 px-1.5 py-0.5 text-[10px] font-medium text-red-800">
                  <Flag className="h-3 w-3" aria-hidden /> flagged
                </span>
              ) : null}
              <span
                className={cn(
                  "inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[10px] font-medium",
                  c.student_email ? "bg-blue-100 text-blue-800" : "bg-zinc-200 text-zinc-600",
                )}
              >
                <User className="h-3 w-3" aria-hidden />
                {c.student_email ?? "anonymous"}
              </span>
              <span className="text-xs text-muted-foreground">
                {c.message_count} messages · {new Date(c.updated_at).toLocaleString()}
              </span>
            </div>
            <p className="mt-1 truncate text-sm">{c.preview}</p>
          </Link>
        ))}
        {!loading && data && data.items.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">No conversations match.</p>
        ) : null}
      </div>

      {data && data.total > PAGE ? (
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            disabled={offset === 0}
            onClick={() => setOffset(Math.max(0, offset - PAGE))}
          >
            ← Newer
          </Button>
          <span className="text-xs text-muted-foreground">
            {offset + 1}–{Math.min(offset + PAGE, data.total)} of {data.total}
          </span>
          <Button
            size="sm"
            variant="outline"
            disabled={offset + PAGE >= data.total}
            onClick={() => setOffset(offset + PAGE)}
          >
            Older →
          </Button>
        </div>
      ) : null}
    </div>
  );
}
