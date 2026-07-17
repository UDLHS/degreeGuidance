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
// Phase 9.6 — aptitude flags measured against the book's own test table
type AptitudeItem = {
  course_code: string;
  name: string | null;
  book_requires: boolean;
  db_requires: boolean;
  page_number: number | null;
  severity: "unwarned" | "over_warned" | string;
};
type AuditResponse = {
  exam_year: number | null;
  courses_in_book: number;
  items: AuditItem[];
  aptitude_items?: AptitudeItem[];
};

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
  // than imply the catalog was checked and found clean. The aptitude table is
  // read independently, so its findings still show if only §2.2 came up empty.
  if (!data || (data.courses_in_book === 0 && (data.aptitude_items ?? []).length === 0))
    return null;

  const items = data.items;
  const aptitude = data.aptitude_items ?? [];

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

        {/* Phase 9.6 — the aptitude flag vs the book's own test table. This
            drives the student-facing conditional badge, so both directions
            hurt: unwarned students skip a compulsory test; over-warned ones
            may not apply at all. */}
        {aptitude.length > 0 && (
          <div className="mt-4 space-y-2 border-t pt-4">
            <p className="text-sm font-medium">
              Aptitude-test flags: {aptitude.length} course
              {aptitude.length === 1 ? "" : "s"} disagree with the book&apos;s test table
              {aptitude[0]?.page_number ? ` (p.${aptitude[0].page_number})` : ""}
            </p>
            {aptitude.map((a) => (
              <div
                key={a.course_code}
                className={cn(
                  "rounded-lg border p-3",
                  a.severity === "unwarned"
                    ? "border-red-300 bg-red-50"
                    : "border-amber-300 bg-amber-50",
                )}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs font-semibold">{a.course_code}</span>
                  <span className="text-sm font-medium">{a.name}</span>
                </div>
                <p
                  className={cn(
                    "mt-1 text-xs",
                    a.severity === "unwarned" ? "text-red-900" : "text-amber-900",
                  )}
                >
                  {a.severity === "unwarned" ? (
                    <>
                      The book requires a practical/aptitude test — <strong>we never tell the
                      student</strong>. They would list it, skip the test, and be deemed
                      ineligible after the one yearly application closes.
                    </>
                  ) : (
                    <>
                      We warn about a practical/aptitude test <strong>the book&apos;s table no
                      longer lists</strong> — a hurdle that may not exist can scare a student
                      off applying.
                    </>
                  )}
                </p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
