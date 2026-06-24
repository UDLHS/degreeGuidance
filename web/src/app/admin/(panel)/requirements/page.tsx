"use client";

import { useCallback, useEffect, useState } from "react";
import { ChevronDown, ChevronRight, Search } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

type Requirement = {
  course_number: string;
  course_name: string | null;
  source_section: string | null;
  notes: string | null;
  ol_requirements: string | null;
  subject_rule: Record<string, unknown>;
  eligible_stream_codes: string[];
};

const STREAM_LABEL: Record<string, string> = {
  PHYSICAL_SCIENCE: "Physical Sci",
  BIO_SCIENCE: "Bio Sci",
  COMMERCE: "Commerce",
  ARTS: "Arts",
  ENGINEERING_TECH: "Engineering Tech",
  BIOSYSTEMS_TECH: "Biosystems Tech",
};

function RuleTree({ node, depth = 0 }: { node: unknown; depth?: number }) {
  if (typeof node !== "object" || node === null) {
    return <span className="text-[#2b5fd0]">{JSON.stringify(node)}</span>;
  }

  const obj = node as Record<string, unknown>;
  const type = obj["type"] as string | undefined;

  if (!type) {
    return (
      <pre className="whitespace-pre-wrap break-words text-[12px] text-[#44546f]">
        {JSON.stringify(node, null, 2)}
      </pre>
    );
  }

  const indent = depth * 16;

  if (type === "and" || type === "or") {
    const conditions = obj["conditions"] as unknown[] | undefined;
    return (
      <div style={{ paddingLeft: depth > 0 ? indent : 0 }}>
        <span
          className={`font-bold ${type === "and" ? "text-[#0f9aa6]" : "text-[#7a5cd6]"}`}
        >
          {type.toUpperCase()}
        </span>
        <div className="ml-4 mt-1 flex flex-col gap-1 border-l-2 border-[#eef2f8] pl-3">
          {(conditions ?? []).map((c, i) => (
            <RuleTree key={i} node={c} depth={depth + 1} />
          ))}
        </div>
      </div>
    );
  }

  if (type === "stream_is") {
    const streams = (obj["streams"] as string[]) ?? [];
    return (
      <div style={{ paddingLeft: indent }}>
        <span className="font-semibold text-[#b07407]">stream_is</span>
        <span className="ml-2 text-[#7c89a0]">
          [{streams.map((s) => STREAM_LABEL[s] ?? s).join(", ")}]
        </span>
      </div>
    );
  }

  if (type === "subject_min_grade") {
    return (
      <div style={{ paddingLeft: indent }}>
        <span className="font-semibold text-[#44546f]">{obj["subject"] as string}</span>
        <span className="ml-2 text-[#9aa7be]">≥ grade</span>
        <span className="ml-1 font-bold text-[#2b5fd0]">{obj["min_grade"] as string}</span>
      </div>
    );
  }

  if (type === "one_of_min_grade") {
    const subjects = (obj["subjects"] as string[]) ?? [];
    return (
      <div style={{ paddingLeft: indent }}>
        <span className="font-semibold text-[#44546f]">one_of</span>
        <span className="ml-2 text-[#9aa7be]">≥ grade</span>
        <span className="ml-1 font-bold text-[#2b5fd0]">{obj["min_grade"] as string}</span>
        <span className="ml-2 text-[#7c89a0]">[{subjects.join(", ")}]</span>
      </div>
    );
  }

  if (type === "count_from_list") {
    const subjects = (obj["subjects"] as string[]) ?? [];
    return (
      <div style={{ paddingLeft: indent }}>
        <span className="font-semibold text-[#44546f]">count_from_list</span>
        <span className="ml-2 text-[#9aa7be]">≥</span>
        <span className="ml-1 font-bold text-[#2b5fd0]">{obj["count"] as number}</span>
        <span className="ml-1 text-[#9aa7be]">of</span>
        <span className="ml-2 text-[#7c89a0]">[{subjects.join(", ")}]</span>
        {obj["min_grade"] ? (
          <span className="ml-2 text-[#9aa7be]">grade ≥ {obj["min_grade"] as string}</span>
        ) : null}
      </div>
    );
  }

  if (type === "any_n_subjects") {
    return (
      <div style={{ paddingLeft: indent }}>
        <span className="font-semibold text-[#44546f]">any_n_subjects</span>
        <span className="ml-2 text-[#9aa7be]">≥</span>
        <span className="ml-1 font-bold text-[#2b5fd0]">{obj["n"] as number}</span>
        <span className="ml-1 text-[#9aa7be]">subjects, grade ≥</span>
        <span className="ml-1 font-bold text-[#2b5fd0]">{(obj["min_grade"] as string) ?? "S"}</span>
      </div>
    );
  }

  // fallback for any unknown node type
  return (
    <pre className="whitespace-pre-wrap break-words text-[12px] text-[#44546f]">
      {JSON.stringify(node, null, 2)}
    </pre>
  );
}

function RequirementRow({ r }: { r: Requirement }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <tr
        className="cursor-pointer border-b border-[#eef2f8] hover:bg-[#f8fafd]"
        onClick={() => setOpen((v) => !v)}
      >
        <td className="py-3 pl-4 pr-2 font-mono text-sm font-semibold text-[#44546f]">
          {r.course_number}
        </td>
        <td className="py-3 pr-3 text-sm text-[#44546f]">
          {r.course_name ?? <span className="italic text-[#9aa7be]">—</span>}
        </td>
        <td className="py-3 pr-3">
          <div className="flex flex-wrap gap-1">
            {r.eligible_stream_codes.map((code) => (
              <Badge key={code} variant="outline" className="text-[11px]">
                {STREAM_LABEL[code] ?? code}
              </Badge>
            ))}
          </div>
        </td>
        <td className="py-3 pr-3 font-mono text-xs text-[#7c89a0]">{r.source_section ?? "—"}</td>
        <td className="py-3 pr-4 text-xs text-[#9aa7be]">
          {r.notes ? (
            <span className="line-clamp-2 max-w-[260px]">{r.notes}</span>
          ) : (
            <span className="italic">—</span>
          )}
        </td>
        <td className="py-3 pr-3 text-[#9aa7be]">
          {open ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </td>
      </tr>
      {open ? (
        <tr className="border-b border-[#eef2f8] bg-[#f8fafd]">
          <td colSpan={6} className="px-5 py-4">
            <div className="mb-3 text-[11px] font-bold uppercase tracking-[.5px] text-[#9aa7be]">
              Subject Rule
            </div>
            <div className="mb-4 rounded-xl bg-white p-4 text-[13px] shadow-inner ring-1 ring-[#eef2f8]">
              <RuleTree node={r.subject_rule} />
            </div>
            {r.ol_requirements ? (
              <div>
                <div className="mb-1 text-[11px] font-bold uppercase tracking-[.5px] text-[#9aa7be]">
                  O/L Requirements
                </div>
                <p className="text-[13px] text-[#44546f]">{r.ol_requirements}</p>
              </div>
            ) : null}
            {r.notes ? (
              <div className="mt-3">
                <div className="mb-1 text-[11px] font-bold uppercase tracking-[.5px] text-[#9aa7be]">
                  Notes
                </div>
                <p className="text-[13px] text-[#44546f]">{r.notes}</p>
              </div>
            ) : null}
          </td>
        </tr>
      ) : null}
    </>
  );
}

export default function RequirementsPage() {
  const [rows, setRows] = useState<Requirement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [debouncedQ, setDebouncedQ] = useState("");

  useEffect(() => {
    const t = setTimeout(() => setDebouncedQ(q), 300);
    return () => clearTimeout(t);
  }, [q]);

  const load = useCallback(async (query: string) => {
    setLoading(true);
    setError(null);
    try {
      const url = "/api/bff/admin/requirements" + (query ? `?q=${encodeURIComponent(query)}` : "");
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setRows(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(debouncedQ);
  }, [debouncedQ, load]);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-medium">Subject Rules</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Curated §2.2 eligibility rules — hand-transcribed from the 2024 handbook. Read-only;
          edits go through data/seeds/course_requirements_data.py + a migration.
        </p>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          className="pl-9"
          placeholder="Filter by number, name, or section…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </div>

      {error ? (
        <p className="text-sm text-destructive">{error}</p>
      ) : loading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-[#eef2f8]">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-[#eef2f8] bg-[#f8fafd] text-[11px] font-bold uppercase tracking-[.5px] text-[#9aa7be]">
                <th className="py-3 pl-4 pr-2">No.</th>
                <th className="py-3 pr-3">Course</th>
                <th className="py-3 pr-3">Eligible Streams</th>
                <th className="py-3 pr-3">§ Section</th>
                <th className="py-3 pr-4">Notes</th>
                <th className="py-3 pr-3" />
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-10 text-center text-sm text-muted-foreground">
                    No rules found.
                  </td>
                </tr>
              ) : (
                rows.map((r) => <RequirementRow key={r.course_number} r={r} />)
              )}
            </tbody>
          </table>
          {rows.length > 0 ? (
            <div className="border-t border-[#eef2f8] px-4 py-2 text-xs text-muted-foreground">
              {rows.length} rule{rows.length === 1 ? "" : "s"}
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
