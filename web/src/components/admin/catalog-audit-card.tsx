"use client";

import { useCallback, useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, EyeOff } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type AuditItem = {
  course_number: string;
  name: string | null;
  book_streams: string[];
  db_streams: string[];
  only_in_book: string[];
  only_in_db: string[];
  page_number: number | null;
  book_may_be_incomplete: boolean;
  severity: "invisible" | "over_granted" | string;
};
type AuditResponse = { exam_year: number | null; courses_in_book: number; items: AuditItem[] };

/** Phase 9.3b — the live catalog measured against THIS book.
 *
 * The change-set above protects courses arriving; this protects the ones
 * already here. Financial Economics/131 was served to all six streams for a
 * year when the book grants only Arts and Commerce — nobody was wrong on
 * purpose, nothing ever compared the two. Report-only: an admin decides which
 * side is right. */
export function CatalogAuditCard({ runId }: { runId: string }) {
  const [data, setData] = useState<AuditResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    const res = await fetch(`/api/bff/admin/ingestions/${runId}/catalog-audit`, {
      cache: "no-store",
    });
    if (res.ok) setData(await res.json());
    setLoading(false);
  }, [runId]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) return null;
  // No artifact (a run from before Section 2.2 was read) — say nothing rather
  // than imply the catalog was checked and found clean.
  if (!data || data.courses_in_book === 0) return null;

  const items = data.items;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Existing courses vs this book</CardTitle>
        <CardDescription>
          {items.length === 0 ? (
            <>
              All {data.courses_in_book} courses this book documents match what students are
              served today.
            </>
          ) : (
            <>
              {items.length} of {data.courses_in_book} courses this book documents{" "}
              <strong>disagree</strong> with what students are served today. Nothing here changes
              automatically — check the book page, then fix the course on{" "}
              <span className="font-medium">Courses</span>.
            </>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="flex items-center gap-2 text-sm text-green-700">
            <CheckCircle2 className="h-4 w-4" aria-hidden /> No disagreements.
          </p>
        ) : (
          <div className="space-y-2">
            {items.map((it) => {
              const invisible = it.severity === "invisible";
              return (
                <div
                  key={it.course_number}
                  className={cn(
                    "rounded-lg border p-3",
                    invisible ? "border-red-300 bg-red-50" : "border-amber-300 bg-amber-50",
                  )}
                >
                  <div className="flex flex-wrap items-center gap-2">
                    {invisible ? (
                      <EyeOff className="h-4 w-4 text-red-700" aria-hidden />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-amber-700" aria-hidden />
                    )}
                    <span className="font-mono text-xs font-semibold">{it.course_number}</span>
                    <span className="text-sm font-medium">{it.name}</span>
                    {it.page_number ? (
                      <span className="text-xs text-muted-foreground">book p.{it.page_number}</span>
                    ) : null}
                  </div>

                  {/* Say the consequence, not the diff — a stream code list
                      doesn't tell an admin who is being harmed. */}
                  <p className={cn("mt-1 text-xs", invisible ? "text-red-900" : "text-amber-900")}>
                    {invisible ? (
                      <>
                        The book lets <strong>{it.only_in_book.join(", ")}</strong> students apply.
                        We don&apos;t — so they never see this course.
                      </>
                    ) : (
                      <>
                        We show this to <strong>{it.only_in_db.join(", ")}</strong> students. The
                        book doesn&apos;t grant them entry.
                      </>
                    )}
                  </p>

                  <p className="mt-1 text-xs text-muted-foreground">
                    book: {it.book_streams.join(", ") || "—"} · we serve:{" "}
                    {it.db_streams.join(", ") || "—"}
                  </p>

                  {it.book_may_be_incomplete && (
                    <p className="mt-1 text-xs text-muted-foreground">
                      ⚠ The book also grants entry by subject list here, so what we could read is a
                      minimum — <strong>we are probably right and the book unreadable</strong>. Don&apos;t
                      narrow this one without reading p.{it.page_number}.
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
