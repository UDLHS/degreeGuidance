"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";

import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

type Item = {
  course_number: string;
  course_name: string;
  course_count: number;
  has_factsheet: boolean;
  version: number | null;
  updated_at: string | null;
  index_status: "missing" | "not_indexed" | "stale" | "indexed";
  chunk_count: number;
};
type ListResponse = { total: number; counts: Record<string, number>; items: Item[] };

const STATUS_STYLE: Record<string, string> = {
  indexed: "bg-green-100 text-green-800",
  stale: "bg-amber-100 text-amber-800",
  not_indexed: "bg-blue-100 text-blue-800",
  missing: "bg-red-100 text-red-800",
};
const STATUS_LABEL: Record<string, string> = {
  indexed: "indexed",
  stale: "stale index",
  not_indexed: "not indexed",
  missing: "no factsheet",
};

export default function FactsheetsPage() {
  const [data, setData] = useState<ListResponse | null>(null);
  const [q, setQ] = useState("");
  const [filter, setFilter] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const load = useCallback(async () => {
    const res = await fetch("/api/bff/admin/factsheets", { cache: "no-store" });
    if (res.ok) setData(await res.json());
    else setErr(`Failed to load factsheets (HTTP ${res.status})`);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const items = useMemo(() => {
    if (!data) return [];
    let out = data.items;
    if (filter) out = out.filter((i) => i.index_status === filter);
    if (q.trim()) {
      const needle = q.trim().toLowerCase();
      out = out.filter(
        (i) =>
          i.course_number.includes(needle) || i.course_name.toLowerCase().includes(needle),
      );
    }
    return out;
  }, [data, q, filter]);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-medium">Factsheets</h1>
        <p className="text-sm text-muted-foreground">
          The knowledge the AI advisor and interest-ranking read. One factsheet per course
          number — covering every active course in the catalog, so new handbook years surface
          any gaps here automatically. Edits reindex that course&apos;s knowledge automatically.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search number or name…"
          className="max-w-xs"
        />
        {data
          ? Object.entries(data.counts).map(([s, n]) => (
              <button
                key={s}
                onClick={() => setFilter(filter === s ? null : s)}
                className={cn(
                  "rounded-md px-2 py-1 text-xs font-medium transition-opacity",
                  STATUS_STYLE[s] ?? "bg-muted",
                  filter && filter !== s && "opacity-40",
                )}
              >
                {n} {STATUS_LABEL[s] ?? s}
              </button>
            ))
          : null}
      </div>

      {err ? <p className="text-sm text-destructive">{err}</p> : null}

      <div className="space-y-1.5">
        {items.map((i) => (
          <Link
            key={i.course_number}
            href={`/admin/factsheets/${i.course_number}`}
            className="flex flex-wrap items-center justify-between gap-2 rounded-lg border px-4 py-2.5 transition-colors hover:bg-accent/40"
          >
            <div className="flex min-w-0 items-center gap-3">
              <span className="font-mono text-sm font-semibold">{i.course_number}</span>
              <span className="truncate text-sm">{i.course_name}</span>
              <span className="text-xs text-muted-foreground">
                {i.course_count} uni-code{i.course_count === 1 ? "" : "s"}
              </span>
            </div>
            <div className="flex items-center gap-2">
              {i.version ? (
                <span className="text-xs text-muted-foreground">
                  v{i.version} · {i.chunk_count} chunks
                </span>
              ) : null}
              <span
                className={cn(
                  "rounded-md px-1.5 py-0.5 text-[10px] font-medium",
                  STATUS_STYLE[i.index_status],
                )}
              >
                {STATUS_LABEL[i.index_status]}
              </span>
            </div>
          </Link>
        ))}
        {data && items.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">No matches.</p>
        ) : null}
      </div>
    </div>
  );
}
