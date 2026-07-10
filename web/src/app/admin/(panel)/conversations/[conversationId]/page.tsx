"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Flag, User, Wrench } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type Msg = {
  role: "user" | "assistant" | "system";
  content: string;
  tool_calls: string[] | null;
  created_at: string;
};
type Detail = {
  conversation_id: string;
  started_at: string;
  updated_at: string;
  flagged: boolean;
  student_email: string | null;
  messages: Msg[];
};

export default function ConversationDetailPage() {
  const { conversationId } = useParams<{ conversationId: string }>();
  const [data, setData] = useState<Detail | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const res = await fetch(`/api/bff/admin/conversations/${conversationId}`, {
      cache: "no-store",
    });
    if (res.ok) setData(await res.json());
    else setErr(`Failed to load conversation (HTTP ${res.status})`);
  }, [conversationId]);

  useEffect(() => {
    load();
  }, [load]);

  async function toggleFlag() {
    if (!data) return;
    setBusy(true);
    const res = await fetch(`/api/bff/admin/conversations/${conversationId}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ flagged: !data.flagged }),
    });
    setBusy(false);
    if (res.ok) setData(await res.json());
  }

  if (err) return <p className="text-sm text-destructive">{err}</p>;
  if (!data) return <p className="text-sm text-muted-foreground">Loading…</p>;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <Link
            href="/admin/conversations"
            className="mb-2 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" aria-hidden /> Back to conversations
          </Link>
          <h1 className="font-mono text-lg font-medium">{data.conversation_id.slice(0, 8)}…</h1>
          <p className="text-sm text-muted-foreground">
            <User className="mr-1 inline h-3.5 w-3.5" aria-hidden />
            {data.student_email ?? "anonymous session"} · started{" "}
            {new Date(data.started_at).toLocaleString()}
          </p>
        </div>
        <Button size="sm" variant={data.flagged ? "destructive" : "outline"} onClick={toggleFlag} disabled={busy}>
          <Flag className="mr-1 h-4 w-4" aria-hidden />
          {data.flagged ? "Unflag" : "Flag for review"}
        </Button>
      </div>

      <div className="space-y-3">
        {data.messages.map((m, i) => (
          <div
            key={i}
            className={cn(
              "max-w-[860px] rounded-xl border px-4 py-3",
              m.role === "user" ? "ml-auto bg-accent/40" : "bg-background",
            )}
          >
            <div className="mb-1 flex flex-wrap items-center gap-2">
              <span
                className={cn(
                  "rounded-md px-1.5 py-0.5 text-[10px] font-medium uppercase",
                  m.role === "user" ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800",
                )}
              >
                {m.role}
              </span>
              <span className="text-[11px] text-muted-foreground">
                {new Date(m.created_at).toLocaleString()}
              </span>
              {m.tool_calls?.map((t, j) => (
                <span
                  key={j}
                  className="inline-flex items-center gap-1 rounded-md bg-purple-100 px-1.5 py-0.5 text-[10px] font-medium text-purple-800"
                  title="Tool the agent called to produce this reply"
                >
                  <Wrench className="h-3 w-3" aria-hidden /> {t}
                </span>
              ))}
            </div>
            <p className="whitespace-pre-wrap text-sm leading-relaxed">{m.content}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
