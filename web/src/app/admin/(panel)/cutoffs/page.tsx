"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Download } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

type YearInfo = { year: number; courses: number; cells: number; with_values: number };
type District = { district_id: number; code: string; name_en: string };
type Row = {
  course_code: string;
  course_number: string | null;
  name_en: string;
  university_code: string | null;
  is_active: boolean;
  is_unmapped?: boolean;
  values: Record<string, number | null>;
  notes: Record<string, string>;
};
type Matrix = {
  year: number;
  districts: District[];
  rows: Row[];
  total_courses: number;
  total_unmapped?: number;
};

// z-scores run ~0–2.6; map to a light green scale so the grid is scannable.
function cellBg(z: number | null): string {
  if (z == null) return "";
  const t = Math.max(0, Math.min(1, (z - 0.5) / 2.0));
  const light = Math.round(96 - t * 34); // 96% -> 62% lightness
  return `hsl(145 45% ${light}%)`;
}

export default function CutoffsPage() {
  const [years, setYears] = useState<YearInfo[]>([]);
  const [year, setYear] = useState<string>("");
  const [q, setQ] = useState("");
  const [data, setData] = useState<Matrix | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const res = await fetch("/api/bff/admin/cutoffs/years", { cache: "no-store" });
      if (!res.ok) {
        setErr(`Failed to load years (HTTP ${res.status})`);
        return;
      }
      const d: YearInfo[] = await res.json();
      setYears(d);
      if (d.length && !year) setYear(String(d[0].year));
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const load = useCallback(async () => {
    if (!year) return;
    setLoading(true);
    setErr(null);
    const p = new URLSearchParams({ year });
    if (q.trim()) p.set("q", q.trim());
    const res = await fetch(`/api/bff/admin/cutoffs/matrix?${p.toString()}`, { cache: "no-store" });
    if (res.ok) setData(await res.json());
    else setErr(`Failed to load cutoffs (HTTP ${res.status})`);
    setLoading(false);
  }, [year, q]);

  useEffect(() => {
    const t = setTimeout(load, q ? 300 : 0); // debounce the search
    return () => clearTimeout(t);
  }, [load, q]);

  const yearMeta = useMemo(() => years.find((y) => String(y.year) === year), [years, year]);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-medium">Cutoffs</h1>
        <p className="text-sm text-muted-foreground">
          Z-score cutoffs by exam year — every course × all 25 districts in one grid.
        </p>
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <div className="space-y-1.5">
          <label className="text-xs text-muted-foreground">Exam year</label>
          <Select value={year} onValueChange={setYear}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Year" />
            </SelectTrigger>
            <SelectContent>
              {years.map((y) => (
                <SelectItem key={y.year} value={String(y.year)}>
                  {y.year} ({y.courses} courses)
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="min-w-56 flex-1 space-y-1.5">
          <label className="text-xs text-muted-foreground">Search course / code / university</label>
          <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="e.g. Medicine, 001A, CMB" />
        </div>
        <Button asChild variant="outline" disabled={!year}>
          <a href={`/api/bff/admin/cutoffs/export?year=${year}`}>
            <Download className="mr-1 h-4 w-4" aria-hidden /> Export CSV
          </a>
        </Button>
      </div>

      {yearMeta ? (
        <p className="text-xs text-muted-foreground">
          {yearMeta.courses} courses · {yearMeta.with_values} cutoffs
          {data ? ` · showing ${data.rows.length}` : ""}
          {yearMeta.cells - yearMeta.with_values > 0
            ? ` · ${yearMeta.cells - yearMeta.with_values} NQC/blank`
            : ""}
        </p>
      ) : null}

      {err ? <p className="text-sm text-destructive">{err}</p> : null}

      {loading && !data ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : data ? (
        <div className="relative max-h-[70vh] overflow-auto rounded-lg border">
          <table className="border-collapse text-xs">
            <thead>
              <tr>
                <th className="sticky left-0 top-0 z-20 border-b border-r bg-muted px-3 py-2 text-left font-medium">
                  Course
                </th>
                {data.districts.map((d) => (
                  <th
                    key={d.district_id}
                    title={d.name_en}
                    className="sticky top-0 z-10 border-b bg-muted px-2 py-2 text-center font-medium"
                  >
                    <span className="block max-w-[64px] truncate">{d.name_en}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.rows.map((r) => (
                <tr key={r.is_unmapped ? `u:${r.name_en}` : r.course_code} className="hover:bg-accent/30">
                  <th
                    className={cn(
                      "sticky left-0 z-10 border-b border-r bg-background px-3 py-1.5 text-left font-normal",
                      !r.is_active && !r.is_unmapped && "opacity-50",
                    )}
                  >
                    <span className="font-mono font-semibold">{r.course_code}</span>
                    {r.is_unmapped ? (
                      <span className="ml-1 rounded bg-blue-100 px-1 py-0.5 text-[9px] font-medium text-blue-800">
                        no code
                      </span>
                    ) : null}
                    <span className="ml-2 text-muted-foreground">
                      {r.name_en.length > 42 ? r.name_en.slice(0, 42) + "…" : r.name_en}
                    </span>
                    {r.university_code ? (
                      <span className="ml-1 text-muted-foreground/70">({r.university_code})</span>
                    ) : null}
                  </th>
                  {data.districts.map((d) => {
                    const z = r.values[String(d.district_id)] ?? null;
                    const note = r.notes[String(d.district_id)];
                    return (
                      <td
                        key={d.district_id}
                        title={note ?? undefined}
                        className="border-b px-2 py-1.5 text-center tabular-nums"
                        style={{ backgroundColor: cellBg(z) }}
                      >
                        {z != null ? z.toFixed(4) : note === "NQC" ? "NQC" : "—"}
                      </td>
                    );
                  })}
                </tr>
              ))}
              {data.rows.length === 0 ? (
                <tr>
                  <td colSpan={data.districts.length + 1} className="px-3 py-6 text-center text-muted-foreground">
                    No cutoffs match.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      ) : years.length === 0 && !err ? (
        <p className="text-sm text-muted-foreground">No cutoff data yet — promote a handbook first.</p>
      ) : null}
    </div>
  );
}
