"use client";

import { useEffect, useState } from "react";

import type {
  CutoffHistory,
  RecommendationResponse,
  ScoredRecommendation,
} from "@/lib/guidance-types";

type TabKey = "safe" | "consider" | "ambitious";

// Band colours reference the --dg-* tokens so tabs adapt to light/dark.
const TAB_META: Record<TabKey, { label: string; color: string; bg: string; desc: string }> = {
  safe: {
    label: "Safe",
    color: "var(--dg-safe-fg)",
    bg: "var(--dg-safe-bg)",
    desc: "You're comfortably above the cutoff — eligible with room to spare.",
  },
  consider: {
    label: "Consider",
    color: "var(--dg-con-fg)",
    bg: "var(--dg-con-bg)",
    desc: "Eligible — your score clears the cutoff, some more narrowly than others.",
  },
  ambitious: {
    label: "Ambitious",
    color: "var(--dg-amb-fg)",
    bg: "var(--dg-amb-bg)",
    desc: "Above your score — sometimes reached in the later UGC selection rounds.",
  },
};
const TAB_ORDER: TabKey[] = ["safe", "consider", "ambitious"];

const STREAM_SHORT: Record<string, string> = {
  PHYSICAL_SCIENCE: "Physical Sci",
  BIO_SCIENCE: "Bio Sci",
  COMMERCE: "Commerce",
  ARTS: "Arts",
  ENGINEERING_TECH: "Engineering Tech",
  BIOSYSTEMS_TECH: "Biosystems Tech",
};

const DIMENSION_LABEL: Record<string, string> = {
  z_margin: "Z-score margin",
  university: "University preference",
  interest: "Interest fit",
  career: "Career fit",
  industry: "Industry demand",
};

const DIMENSION_DESC: Record<string, string> = {
  z_margin:   "How safely your score clears the cutoff",
  university: "Matches your preferred universities",
  interest:   "Content aligns with what you described",
  career:     "Career paths this degree leads to",
  industry:   "Job-market demand for this sector in Sri Lanka",
};

// Semantic category colours for the score-breakdown bars — kept distinct
// (not themed) so each dimension stays recognisable across light/dark.
const DIMENSION_COLOR: Record<string, string> = {
  z_margin:   "#3b5bd0",   // blue
  university: "#0f9aa6",   // teal
  interest:   "#7a5cd6",   // purple
  career:     "#16a06b",   // green
  industry:   "#d97706",   // amber
};

// Dimensions that can legitimately score 0 as an *active mismatch* signal
// (not just "inert / not applicable"). When raw_score === 0 for these, the
// student DID express a preference but this course doesn't match it.
const MISMATCH_DIMS = new Set(["career", "industry"]);

function whyRankedHere(breakdown: { name: string; raw_score: number; contribution: number }[]): string | null {
  const chips: string[] = [];
  // Career match — explicit goal alignment
  const career = breakdown.find((d) => d.name === "career");
  if (career && career.raw_score >= 0.5) chips.push("Career match");
  // Industry demand / sector alignment
  const industry = breakdown.find((d) => d.name === "industry");
  if (industry && industry.raw_score >= 0.75) chips.push("High-demand sector");
  else if (industry && industry.raw_score >= 0.5) chips.push("Growing sector");
  // Interest content fit
  const interest = breakdown.find((d) => d.name === "interest");
  if (interest && interest.raw_score >= 0.4) chips.push("Interest fit");
  // University preference
  const uni = breakdown.find((d) => d.name === "university");
  if (uni && uni.raw_score >= 1.0) chips.push("Preferred university");
  return chips.length ? chips.join(" · ") : null;
}

export function ResultsView({
  results,
  zScore,
  districtName,
  streamName,
  districtCode,
  streamCode,
  availableYears,
  yearLoading,
  onYearChange,
  onEdit,
  accent,
}: {
  results: RecommendationResponse;
  zScore: number;
  districtName: string;
  streamName: string;
  districtCode: string;
  streamCode: string;
  /** Promoted exam years, newest first (empty = switcher hidden). */
  availableYears: number[];
  yearLoading: boolean;
  onYearChange: (year: number) => void;
  onEdit: () => void;
  accent: string;
}) {
  const byBucket: Record<string, ScoredRecommendation[]> = {};
  for (const r of results.recommendations) {
    (byBucket[r.bucket] ??= []).push(r);
  }

  // A run restored from localStorage may predate the later-rounds fields —
  // never let a missing field crash the page (a mid-deploy student would hit
  // exactly that). Defaults keep the tab honest: empty list, stated window.
  const laterRound = results.later_round ?? [];
  const laterRoundCount = results.later_round_count ?? laterRound.length;
  const laterRoundMargin = results.later_round_margin ?? 0.15;

  // Tabs: default to the first group that has anything to show.
  const [tab, setTab] = useState<TabKey>("safe");
  useEffect(() => {
    const first =
      TAB_ORDER.find((k) =>
        k === "ambitious" ? laterRoundCount > 0 : (byBucket[k]?.length ?? 0) > 0,
      ) ?? "safe";
    setTab(first);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [results]);

  // Cutoff history for trend chips — one bulk call per (district, stream),
  // stream-aware (matches the engine's override semantics). Failure is
  // non-fatal: cards simply render without trend chips.
  const [history, setHistory] = useState<CutoffHistory | null>(null);
  useEffect(() => {
    if (!districtCode || !streamCode) return;
    let cancelled = false;
    fetch(
      `/api/public/cutoff-history?district_code=${encodeURIComponent(districtCode)}&stream_code=${encodeURIComponent(streamCode)}`,
    )
      .then((r) => (r.ok ? r.json() : Promise.reject(r)))
      .then((d: CutoffHistory) => {
        if (!cancelled) setHistory(d);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [districtCode, streamCode]);

  const viewedYear = results.exam_year_used;
  const latestYear = availableYears.length ? availableYears[0] : viewedYear;

  return (
    <main className="mx-auto w-full max-w-[1000px] flex-1 px-6">
      <div className="py-9 pb-[120px]">
        <div className="mb-4 flex flex-wrap items-start justify-between gap-6">
          <div>
            <h1
              className="mb-[14px] text-4xl font-bold leading-[1.12] tracking-[-.5px] sm:text-[42px]"
              style={{ fontFamily: "var(--font-spectral), Georgia, serif" }}
            >
              Your degree matches
            </h1>
            <div className="flex flex-wrap gap-[9px]">
              <Pill label="Z-score" value={zScore.toFixed(2)} />
              <Pill label="District" value={districtName} />
              <Pill label="Stream" value={streamName} />
              {availableYears.length > 1 ? (
                <label
                  className="inline-flex items-center gap-[7px] rounded-full px-[15px] py-2 text-sm font-semibold"
                  style={{ background: "var(--dg-surface)", border: "1px solid var(--dg-border)" }}
                >
                  <span className="font-medium" style={{ color: "var(--dg-muted)" }}>Viewing</span>
                  <select
                    value={viewedYear}
                    disabled={yearLoading}
                    onChange={(e) => {
                      const y = Number(e.target.value);
                      if (y !== viewedYear) onYearChange(y);
                    }}
                    className="cursor-pointer bg-transparent font-semibold outline-none disabled:cursor-wait disabled:opacity-60"
                    style={{ color: accent }}
                    aria-label="Exam year to view cutoffs for"
                  >
                    {availableYears.map((y) => (
                      <option key={y} value={y}>
                        {y} cutoffs{y === latestYear ? " (latest)" : ""}
                      </option>
                    ))}
                  </select>
                  {yearLoading ? <span style={{ color: "var(--dg-muted)" }}>…</span> : null}
                </label>
              ) : (
                <Pill label="Cutoffs" value={String(viewedYear)} />
              )}
              <button
                onClick={onEdit}
                className="rounded-full px-[15px] py-2 text-sm font-semibold"
                style={{ border: "1px dashed var(--dg-border)", color: accent }}
              >
                Edit answers
              </button>
            </div>
          </div>
        </div>

        {viewedYear !== latestYear ? (
          <p
            className="mb-4 max-w-[640px] rounded-xl px-4 py-3 text-sm"
            style={{ background: "var(--dg-con-bg)", color: "var(--dg-con-fg)" }}
          >
            You&apos;re viewing <strong>{viewedYear}</strong> cutoffs for reference. Z-scores are
            standardised per exam year and cutoffs shift every year — use this to understand
            trends, not as this year&apos;s answer.
            {results.confidence_message ? ` ${results.confidence_message}` : ""}
          </p>
        ) : results.confidence_message ? (
          <p
            className="mb-4 max-w-[640px] rounded-xl px-4 py-3 text-sm"
            style={{ background: "var(--dg-con-bg)", color: "var(--dg-con-fg)" }}
          >
            {results.confidence_message}
          </p>
        ) : null}

        <p className="mb-3 max-w-[640px] text-base leading-[1.55]" style={{ color: "var(--dg-ink)" }}>
          We found {results.recommendations.length} programme
          {results.recommendations.length === 1 ? "" : "s"} you&apos;re eligible for in{" "}
          {streamName} from {districtName}, based on the verified {results.exam_year_used}{" "}
          cutoffs.
          {results.mode === "normal"
            ? " Ranked by how safely your Z-score clears each cutoff."
            : " Ranked by your preferences and Z-score margin."}
        </p>

        <p className="mb-3 max-w-[640px] text-[12.5px] leading-[1.5]" style={{ color: "var(--dg-muted)" }}>
          Guidance only — the final selection is made by the University Grants Commission.
          Always verify against the official UGC handbook before applying.
        </p>

        {results.conditional_count > 0 ? (
          <p className="mb-8 max-w-[640px] text-sm" style={{ color: "var(--dg-muted)" }}>
            {results.conditional_count} of these also require an aptitude or practical test —
            marked below.
          </p>
        ) : (
          <div className="mb-8" />
        )}

        {/* Three tabs (user decision 2026-07-13): Safe / Consider / Ambitious.
            Ambitious = courses ABOVE the student's z (later-rounds window),
            never eligibility. Order inside each group: higher cutoff first. */}
        <div className="mb-6 flex flex-wrap gap-2">
          {TAB_ORDER.map((key) => {
            const meta = TAB_META[key];
            const count =
              key === "ambitious" ? laterRoundCount : (byBucket[key]?.length ?? 0);
            const active = tab === key;
            return (
              <button
                key={key}
                onClick={() => setTab(key)}
                className="inline-flex items-center gap-2 rounded-full border px-[16px] py-[8px] text-sm font-bold transition-colors"
                style={
                  active
                    ? { color: meta.color, background: meta.bg, borderColor: meta.color }
                    : { color: "var(--dg-muted)", background: "var(--dg-surface)", borderColor: "var(--dg-border)" }
                }
              >
                <span className="h-[9px] w-[9px] rounded-full" style={{ background: active ? meta.color : "var(--dg-border)" }} />
                {meta.label}
                <span
                  className="rounded-full px-[7px] py-[1px] text-[12px] tabular-nums"
                  style={active ? { background: "#ffffff55" } : { background: "var(--dg-surface2)" }}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {tab !== "ambitious" ? (
          <section className="mb-10">
            <p className="mb-4 text-sm" style={{ color: "var(--dg-muted)" }}>{TAB_META[tab].desc}</p>
            {(byBucket[tab]?.length ?? 0) === 0 ? (
              <p
                className="rounded-xl px-5 py-6 text-sm"
                style={{ border: "1px dashed var(--dg-border)", background: "var(--dg-surface)", color: "var(--dg-muted)" }}
              >
                Nothing in this group for your answers.
              </p>
            ) : (
              <div className="flex flex-col gap-[14px]">
                {(byBucket[tab] ?? []).map((d) => (
                  <CourseCard
                    key={d.course_code}
                    d={d}
                    accent={accent}
                    series={history?.courses[d.course_code]}
                    viewedYear={viewedYear}
                  />
                ))}
              </div>
            )}
          </section>
        ) : (
          <section className="mb-10">
            <p className="mb-4 max-w-[680px] text-sm leading-[1.5]" style={{ color: "var(--dg-muted)" }}>
              These cutoffs are <strong>above your Z-score</strong> (within +
              {laterRoundMargin.toFixed(2)}). In past years, seats freed up after the
              first round of UGC selections have admitted students to such courses in the later
              selection rounds — so they can still be worth listing in your application order.
              Not guaranteed, and not an eligibility promise.
            </p>
            {laterRoundCount === 0 ? (
              <p
                className="rounded-xl px-5 py-6 text-sm"
                style={{ border: "1px dashed var(--dg-border)", background: "var(--dg-surface)", color: "var(--dg-muted)" }}
              >
                No courses sit within +{laterRoundMargin.toFixed(2)} of your score.
              </p>
            ) : (
              <div className="flex flex-col gap-2">
                {laterRound.map((it) => (
                  <div
                    key={it.course_code + it.university_code}
                    className="flex flex-wrap items-center justify-between gap-2 rounded-xl px-5 py-3 text-sm"
                    style={{ border: "1px solid var(--dg-amb-bd)", background: "var(--dg-surface)" }}
                  >
                    <span className="min-w-0 font-medium" style={{ color: "var(--dg-ink)" }}>
                      {it.course_name}
                      {it.requires_aptitude_test ? (
                        <span
                          className="ml-2 rounded-full px-2 py-[2px] text-[11.5px] font-semibold"
                          style={{ background: "var(--dg-con-bg)", color: "var(--dg-con-fg)" }}
                        >
                          aptitude test
                        </span>
                      ) : null}
                    </span>
                    <span className="flex items-center gap-3 tabular-nums">
                      <span style={{ color: "var(--dg-muted)" }}>cutoff {it.cutoff_z_score.toFixed(4)}</span>
                      <span
                        className="rounded-full px-2 py-[2px] text-[12px] font-semibold"
                        style={{ background: "var(--dg-amb-bg)", color: "var(--dg-amb-fg)" }}
                      >
                        +{it.gap_above.toFixed(4)} above you
                      </span>
                    </span>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {results.also_offered_no_cutoff_count > 0 ? (
          <section className="mt-4">
            <div className="mb-3 text-sm font-bold" style={{ color: "var(--dg-ink)" }}>
              Also offered in your stream — no {results.exam_year_used} cutoff in your district
            </div>
            <p className="mb-4 max-w-[640px] text-sm leading-[1.5]" style={{ color: "var(--dg-muted)" }}>
              These programmes are part of the catalog but had no recorded intake for your
              district in {results.exam_year_used}, so we can&apos;t compute eligibility from a
              Z-score. Check directly with the university.
            </p>
            <div className="flex flex-col gap-2">
              {results.also_offered_no_cutoff.map((it) => (
                <div
                  key={it.course_code + it.university_code}
                  className="flex items-center justify-between rounded-xl px-5 py-3 text-sm"
                  style={{ border: "1px solid var(--dg-border)", background: "var(--dg-surface)" }}
                >
                  <span className="font-medium" style={{ color: "var(--dg-ink)" }}>{it.course_name}</span>
                  <span style={{ color: "var(--dg-muted)" }}>{it.university_name}</span>
                </div>
              ))}
            </div>
          </section>
        ) : null}
      </div>
    </main>
  );
}

function Pill({ label, value }: { label: string; value: string }) {
  return (
    <span
      className="inline-flex items-center gap-[7px] rounded-full px-[15px] py-2 text-sm font-semibold"
      style={{ background: "var(--dg-surface)", border: "1px solid var(--dg-border)", color: "var(--dg-ink)" }}
    >
      <span className="font-medium" style={{ color: "var(--dg-muted)" }}>{label}</span> {value}
    </span>
  );
}

/** Delta chip + year-by-year popover for one course's cutoff history
 * (Phase 2 plan §1.4). `series` is stream-aware ({"2024": 1.2409, ...}).
 * Rising cutoff = harder to get in (amber); falling = easier (green). */
function CutoffTrend({
  series,
  viewedYear,
}: {
  series?: Record<string, number>;
  viewedYear: number;
}) {
  if (!series) return null;
  const years = Object.keys(series)
    .map(Number)
    .sort((a, b) => b - a);
  if (years.length < 2) return null;
  const current = series[String(viewedYear)];
  const prevYear = years.find((y) => y < viewedYear);
  const delta =
    current != null && prevYear != null ? current - series[String(prevYear)] : null;

  let chip: { text: string; color: string; bg: string } | null = null;
  if (delta != null && prevYear != null) {
    if (Math.abs(delta) < 0.005) {
      chip = { text: `≈ same as ${prevYear}`, color: "var(--dg-muted)", bg: "var(--dg-surface2)" };
    } else if (delta > 0) {
      chip = { text: `↑ +${delta.toFixed(4)} vs ${prevYear}`, color: "var(--dg-amb-fg)", bg: "var(--dg-amb-bg)" };
    } else {
      chip = { text: `↓ ${delta.toFixed(4)} vs ${prevYear}`, color: "var(--dg-safe-fg)", bg: "var(--dg-safe-bg)" };
    }
  }

  return (
    <details className="relative inline-block">
      <summary
        className="inline-flex cursor-pointer list-none items-center gap-1 rounded-full px-[10px] py-[3px] text-[11.5px] font-bold [&::-webkit-details-marker]:hidden"
        style={chip ? { color: chip.color, background: chip.bg } : { color: "var(--dg-muted)", background: "var(--dg-surface2)" }}
        title="Cutoff history for your district and stream"
      >
        {chip ? chip.text : "History"}
      </summary>
      <div
        className="absolute right-0 z-20 mt-2 w-[210px] rounded-xl p-3"
        style={{ border: "1px solid var(--dg-border)", background: "var(--dg-surface)", boxShadow: "var(--dg-shadow)" }}
      >
        <div className="mb-2 text-[11px] font-bold uppercase tracking-[.5px]" style={{ color: "var(--dg-muted)" }}>
          Cutoff by year
        </div>
        {years.map((y) => (
          <div
            key={y}
            className="flex items-center justify-between py-[3px] text-[13px] tabular-nums"
            style={{ fontWeight: y === viewedYear ? 700 : 500 }}
          >
            <span style={{ color: "var(--dg-muted)" }}>
              {y}
              {y === viewedYear ? " (viewing)" : ""}
            </span>
            <span style={{ color: "var(--dg-ink)" }}>{series[String(y)].toFixed(4)}</span>
          </div>
        ))}
        <div
          className="mt-2 border-t pt-2 text-[11px] leading-[1.4]"
          style={{ borderColor: "var(--dg-track)", color: "var(--dg-muted)" }}
        >
          Z-scores are standardised per year — treat older years as trend context.
        </div>
      </div>
    </details>
  );
}

function CourseCard({
  d,
  accent,
  series,
  viewedYear,
}: {
  d: ScoredRecommendation;
  accent: string;
  series?: Record<string, number>;
  viewedYear: number;
}) {
  const matchPct = Math.round(d.total_score * 100);
  const youColor = d.student_margin >= 0 ? "#16a06b" : "var(--dg-amb-bar)";
  const youPos = Math.min(96, Math.max(4, ((d.student_margin + 0.4) / 0.8) * 100));

  return (
    <article
      className="rounded-[20px] p-6 sm:p-7"
      style={{ border: "1px solid var(--dg-border)", background: "var(--dg-surface)", boxShadow: "var(--dg-shadow)" }}
    >
      <div className="flex flex-wrap items-start justify-between gap-5">
        <div className="min-w-[220px] flex-1">
          {d.status === "conditional" ? (
            <div
              className="mb-[11px] inline-flex items-center rounded-md px-[11px] py-1 text-[11.5px] font-bold uppercase tracking-[.4px]"
              style={{ background: "var(--dg-amb-bg)", color: "var(--dg-amb-fg)" }}
            >
              Aptitude / practical test required
            </div>
          ) : null}
          <h3
            className="mb-1 text-2xl font-semibold leading-[1.15] tracking-[-.3px] sm:text-[26px]"
            style={{ fontFamily: "var(--font-spectral), Georgia, serif", color: "var(--dg-ink)" }}
          >
            {d.course_name}
          </h3>
          <div className="text-[15px] font-medium" style={{ color: "var(--dg-muted)" }}>{d.university_name}</div>
          {d.eligible_stream_codes.length > 1 ? (
            <div className="mt-[9px] flex flex-wrap gap-[6px]">
              {d.eligible_stream_codes.map((code) => (
                <span
                  key={code}
                  className="inline-block rounded-full px-[10px] py-[3px] text-[11.5px] font-semibold"
                  style={{ border: "1px solid var(--dg-border)", color: "var(--dg-muted)" }}
                >
                  {STREAM_SHORT[code] ?? code}
                </span>
              ))}
            </div>
          ) : null}
        </div>
        <div className="flex-shrink-0 text-right">
          <div
            className="text-4xl font-semibold leading-none tracking-[-1px] sm:text-[46px]"
            style={{ color: accent, fontFamily: "var(--font-spectral), Georgia, serif" }}
          >
            {matchPct}
            <span className="text-xl sm:text-[22px]" style={{ color: "var(--dg-muted)" }}>%</span>
          </div>
          <div className="mt-[2px] text-xs font-semibold uppercase tracking-[.5px]" style={{ color: "var(--dg-muted)" }}>
            Match
          </div>
        </div>
      </div>

      <div
        className="mt-[22px] flex flex-wrap gap-[30px] border-t pt-[22px]"
        style={{ borderColor: "var(--dg-track)" }}
      >
        <div className="min-w-[260px] flex-1">
          <div className="mb-[14px] flex items-center justify-between">
            <div className="text-xs font-bold uppercase tracking-[.5px]" style={{ color: "var(--dg-muted)" }}>
              Score breakdown
            </div>
            {(() => {
              const why = whyRankedHere(d.breakdown);
              return why ? (
                <div className="text-[11.5px] font-semibold" style={{ color: "var(--dg-muted)" }}>{why}</div>
              ) : null;
            })()}
          </div>
          <div className="flex flex-col gap-[14px]">
            {d.breakdown.map((bar) => {
              const isMismatch = MISMATCH_DIMS.has(bar.name) && bar.raw_score === 0;
              const color = DIMENSION_COLOR[bar.name] ?? accent;
              return (
                <div key={bar.name}>
                  <div className="mb-[4px] flex items-baseline justify-between text-[13px]">
                    <span className="font-semibold" style={{ color: "var(--dg-ink)" }}>
                      {DIMENSION_LABEL[bar.name] ?? bar.name}
                    </span>
                    {isMismatch ? (
                      <span className="text-[12px] font-semibold" style={{ color: "var(--dg-con-fg)" }}>Not matched</span>
                    ) : (
                      <span className="font-bold tabular-nums" style={{ color }}>
                        {Math.round(bar.raw_score * 100)}%
                      </span>
                    )}
                  </div>
                  {DIMENSION_DESC[bar.name] ? (
                    <div className="mb-[6px] text-[11.5px]" style={{ color: "var(--dg-muted)" }}>
                      {DIMENSION_DESC[bar.name]}
                    </div>
                  ) : null}
                  {isMismatch ? (
                    <div className="h-[6px] overflow-hidden rounded-full" style={{ background: "var(--dg-track)" }}>
                      <div className="h-full w-0 rounded-full" />
                    </div>
                  ) : (
                    <div className="h-[6px] overflow-hidden rounded-full" style={{ background: "var(--dg-track)" }}>
                      <div
                        className="h-full rounded-full transition-[width] duration-500"
                        style={{
                          width: `${Math.round(bar.raw_score * 100)}%`,
                          background: color,
                        }}
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <div className="min-w-[240px] flex-1">
          <div className="mb-[14px] flex items-center justify-between gap-2">
            <div className="text-xs font-bold uppercase tracking-[.5px]" style={{ color: "var(--dg-muted)" }}>
              Cutoff vs. you
            </div>
            <CutoffTrend series={series} viewedYear={viewedYear} />
          </div>
          <div className="relative mb-2 h-2 rounded-full" style={{ background: "var(--dg-track)" }}>
            <div
              className="absolute -top-1 bottom-[-4px] w-[2px]"
              style={{ left: "50%", background: "var(--dg-muted)" }}
            />
            <div
              className="absolute top-1/2 h-[13px] w-[13px] -translate-x-1/2 -translate-y-1/2 rounded-full"
              style={{ left: `${youPos}%`, background: youColor, border: "2.5px solid var(--dg-surface)", boxShadow: "var(--dg-shadow)" }}
            />
          </div>
          <div className="mb-[18px] flex justify-between text-[13px]">
            <span style={{ color: "var(--dg-muted)" }}>
              Cutoff{" "}
              <strong className="tabular-nums" style={{ color: "var(--dg-ink)" }}>
                {d.cutoff_z_score.toFixed(4)}
              </strong>
            </span>
            <span className="font-bold tabular-nums" style={{ color: youColor }}>
              You {(d.student_margin >= 0 ? "+" : "") + d.student_margin.toFixed(2)}
            </span>
          </div>
          {d.is_marginal ? (
            <p className="text-[12.5px] leading-[1.4]" style={{ color: "var(--dg-con-fg)" }}>
              Close to the cutoff — next year&apos;s could shift and change this result.
            </p>
          ) : null}
        </div>
      </div>

      <div
        className="mt-5 border-t pt-[18px] text-[13px]"
        style={{ borderColor: "var(--dg-track)", color: "var(--dg-muted)" }}
      >
        {d.selection_basis === "all_island_merit" ? "All-island merit selection" : "District quota selection"}
      </div>
    </article>
  );
}
