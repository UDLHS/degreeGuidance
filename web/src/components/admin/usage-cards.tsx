"use client";

import { useEffect, useState } from "react";
import { Activity, Flag, MessagesSquare, Wrench } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type Usage = {
  conversations: { total: number; last_7_days: number; today: number; flagged: number };
  messages: { total: number; last_7_days: number };
  tool_usage: Record<string, number>;
  eligibility: {
    total: number;
    last_7_days: number;
    today: number;
    avg_latency_ms: number;
    by_year_viewed: Record<string, number>;
  };
};

/** Live usage snapshot (Phase 2 §2.2). Everything here is derived from the
 * data at query time — years and tools appear/disappear with the data, never
 * hardcoded, so future handbook uploads need no UI change. */
export function UsageCards() {
  const [u, setU] = useState<Usage | null>(null);
  const [err, setErr] = useState(false);

  useEffect(() => {
    fetch("/api/bff/admin/usage", { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : Promise.reject(r)))
      .then(setU)
      .catch(() => setErr(true));
  }, []);

  if (err) return null; // dashboard stays useful without the cards
  if (!u) return <p className="text-sm text-muted-foreground">Loading usage…</p>;

  const tools = Object.entries(u.tool_usage);
  const toolMax = Math.max(1, ...tools.map(([, n]) => n));
  const years = Object.entries(u.eligibility.by_year_viewed)
    .filter(([y]) => y !== "0")
    .sort((a, b) => Number(b[0]) - Number(a[0]));

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-sm font-medium">
            <MessagesSquare className="h-4 w-4 text-muted-foreground" aria-hidden />
            AI conversations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-semibold tabular-nums">{u.conversations.total}</div>
          <p className="text-xs text-muted-foreground">
            {u.conversations.last_7_days} in the last 7 days · {u.conversations.today} today
          </p>
          {u.conversations.flagged > 0 ? (
            <p className="mt-1 inline-flex items-center gap-1 text-xs font-medium text-red-700">
              <Flag className="h-3 w-3" aria-hidden /> {u.conversations.flagged} flagged for review
            </p>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-sm font-medium">
            <Activity className="h-4 w-4 text-muted-foreground" aria-hidden />
            Eligibility checks
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-semibold tabular-nums">{u.eligibility.total}</div>
          <p className="text-xs text-muted-foreground">
            {u.eligibility.last_7_days} in the last 7 days · avg {u.eligibility.avg_latency_ms}ms
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-sm font-medium">
            <Wrench className="h-4 w-4 text-muted-foreground" aria-hidden />
            Agent tool usage
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-1.5">
          {tools.length === 0 ? (
            <p className="text-xs text-muted-foreground">No tool calls yet.</p>
          ) : (
            tools.map(([tool, n]) => (
              <div key={tool} className="flex items-center gap-2">
                <span className="w-32 truncate font-mono text-[11px] text-muted-foreground">
                  {tool}
                </span>
                <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-primary/70"
                    style={{ width: `${(n / toolMax) * 100}%` }}
                  />
                </div>
                <span className="w-6 text-right text-[11px] tabular-nums">{n}</span>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Years students view</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1">
          {years.length === 0 ? (
            <p className="text-xs text-muted-foreground">No checks recorded yet.</p>
          ) : (
            years.map(([y, n]) => (
              <div key={y} className="flex items-center justify-between text-sm">
                <span className="tabular-nums text-muted-foreground">{y}</span>
                <span className="font-medium tabular-nums">{n}</span>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
