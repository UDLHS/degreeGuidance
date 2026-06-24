"use client";

import type { RecommendationResponse, ScoredRecommendation } from "@/lib/guidance-types";

const BUCKET_META: Record<string, { label: string; color: string; bg: string; desc: string }> = {
  safe: {
    label: "Safe choice",
    color: "#0a7d54",
    bg: "#e4f5ec",
    desc: "You're comfortably above the cutoff.",
  },
  ambitious: {
    label: "Ambitious",
    color: "#b4485f",
    bg: "#fbe9ed",
    desc: "A strong fit, but right at the edge of the cutoff.",
  },
  consider: {
    label: "Worth considering",
    color: "#b07407",
    bg: "#fbf1da",
    desc: "Eligible, with more room between your score and the cutoff.",
  },
};
const BUCKET_ORDER = ["safe", "ambitious", "consider"];

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
  industry: "Industry fit",
};
const DIMENSION_COLOR: Record<string, string> = {
  z_margin: "#2b5fd0",
  university: "#0f9aa6",
  interest: "#7a5cd6",
  career: "#7a5cd6",
  industry: "#7a5cd6",
};

export function ResultsView({
  results,
  zScore,
  districtName,
  streamName,
  onEdit,
  accent,
}: {
  results: RecommendationResponse;
  zScore: number;
  districtName: string;
  streamName: string;
  onEdit: () => void;
  accent: string;
}) {
  const byBucket: Record<string, ScoredRecommendation[]> = {};
  for (const r of results.recommendations) {
    (byBucket[r.bucket] ??= []).push(r);
  }

  return (
    <main className="mx-auto w-full max-w-[1120px] flex-1 px-6">
      <div className="py-11 pb-[120px]">
        <div className="mb-4 flex flex-wrap items-start justify-between gap-6">
          <div>
            <h1 className="mb-[14px] font-[family-name:var(--font-newsreader)] text-4xl font-medium leading-[1.12] tracking-[-.5px] sm:text-[42px]">
              Your degree matches
            </h1>
            <div className="flex flex-wrap gap-[9px]">
              <Pill label="Z-score" value={zScore.toFixed(2)} />
              <Pill label="District" value={districtName} />
              <Pill label="Stream" value={streamName} />
              <button
                onClick={onEdit}
                className="rounded-full border border-dashed border-[#c4cee0] px-[15px] py-2 text-sm font-semibold"
                style={{ color: accent }}
              >
                Edit answers
              </button>
            </div>
          </div>
        </div>

        {results.confidence_message ? (
          <p className="mb-4 max-w-[640px] rounded-xl bg-[#fbf1da] px-4 py-3 text-sm text-[#7a5500]">
            {results.confidence_message}
          </p>
        ) : null}

        <p className="mb-3 max-w-[640px] text-base leading-[1.55] text-[#5b6b85]">
          We found {results.recommendations.length} programme
          {results.recommendations.length === 1 ? "" : "s"} you&apos;re eligible for in{" "}
          {streamName} from {districtName}, based on the verified {results.exam_year_used}{" "}
          cutoffs.
          {results.mode === "normal"
            ? " Ranked by how safely your Z-score clears each cutoff."
            : " Ranked by your preferences and Z-score margin."}
        </p>

        {results.conditional_count > 0 ? (
          <p className="mb-8 max-w-[640px] text-sm text-[#7c89a0]">
            {results.conditional_count} of these also require an aptitude or practical test —
            marked below.
          </p>
        ) : (
          <div className="mb-8" />
        )}

        {BUCKET_ORDER.filter((k) => byBucket[k]?.length).map((key) => {
          const meta = BUCKET_META[key];
          const degrees = byBucket[key];
          return (
            <section key={key} className="mb-10">
              <div className="mb-[18px] flex flex-wrap items-center gap-[14px]">
                <span
                  className="inline-flex items-center gap-2 rounded-full px-[15px] py-[7px] text-sm font-bold"
                  style={{ color: meta.color, background: meta.bg }}
                >
                  <span className="h-[9px] w-[9px] rounded-full" style={{ background: meta.color }} />
                  {meta.label}
                </span>
                <span className="text-sm font-semibold text-[#9aa7be]">
                  {degrees.length} programme{degrees.length === 1 ? "" : "s"}
                </span>
                <span className="flex-1 text-sm text-[#9aa7be]">{meta.desc}</span>
              </div>
              <div className="flex flex-col gap-[14px]">
                {degrees.map((d) => (
                  <CourseCard key={d.course_code} d={d} accent={accent} />
                ))}
              </div>
            </section>
          );
        })}

        {results.also_offered_no_cutoff_count > 0 ? (
          <section className="mt-4">
            <div className="mb-3 text-sm font-bold text-[#44546f]">
              Also offered in your stream — no {results.exam_year_used} cutoff in your district
            </div>
            <p className="mb-4 max-w-[640px] text-sm leading-[1.5] text-[#7c89a0]">
              These programmes are part of the catalog but had no recorded intake for your
              district in {results.exam_year_used}, so we can&apos;t compute eligibility from a
              Z-score. Check directly with the university.
            </p>
            <div className="flex flex-col gap-2">
              {results.also_offered_no_cutoff.map((it) => (
                <div
                  key={it.course_code + it.university_code}
                  className="flex items-center justify-between rounded-xl border border-[#e3e9f2] bg-white px-5 py-3 text-sm"
                >
                  <span className="font-medium">{it.course_name}</span>
                  <span className="text-[#9aa7be]">{it.university_name}</span>
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
    <span className="inline-flex items-center gap-[7px] rounded-full border border-[#e3e9f2] bg-white px-[15px] py-2 text-sm font-semibold">
      <span className="font-medium text-[#9aa7be]">{label}</span> {value}
    </span>
  );
}

function CourseCard({ d, accent }: { d: ScoredRecommendation; accent: string }) {
  const matchPct = Math.round(d.total_score * 100);
  const youColor = d.student_margin >= 0 ? "#16a06b" : "#d76a82";
  const youPos = Math.min(96, Math.max(4, ((d.student_margin + 0.4) / 0.8) * 100));

  return (
    <article className="rounded-[20px] border border-[#e3e9f2] bg-white p-6 shadow-[0_1px_3px_rgba(20,36,59,.04)] sm:p-7">
      <div className="flex flex-wrap items-start justify-between gap-5">
        <div className="min-w-[220px] flex-1">
          {d.status === "conditional" ? (
            <div className="mb-[11px] inline-flex items-center rounded-md bg-[#fbe9ed] px-[11px] py-1 text-[11.5px] font-bold uppercase tracking-[.4px] text-[#b4485f]">
              Aptitude / practical test required
            </div>
          ) : null}
          <h3 className="mb-1 font-[family-name:var(--font-newsreader)] text-2xl font-medium leading-[1.15] tracking-[-.3px] sm:text-[26px]">
            {d.course_name}
          </h3>
          <div className="text-[15px] font-medium text-[#7c89a0]">{d.university_name}</div>
          {d.eligible_stream_codes.length > 1 ? (
            <div className="mt-[9px] flex flex-wrap gap-[6px]">
              {d.eligible_stream_codes.map((code) => (
                <span
                  key={code}
                  className="inline-block rounded-full border border-[#e3e9f2] px-[10px] py-[3px] text-[11.5px] font-semibold text-[#7c89a0]"
                >
                  {STREAM_SHORT[code] ?? code}
                </span>
              ))}
            </div>
          ) : null}
        </div>
        <div className="flex-shrink-0 text-right">
          <div
            className="font-[family-name:var(--font-newsreader)] text-4xl font-medium leading-none tracking-[-1px] sm:text-[46px]"
            style={{ color: accent }}
          >
            {matchPct}
            <span className="text-xl text-[#9aa7be] sm:text-[22px]">%</span>
          </div>
          <div className="mt-[2px] text-xs font-semibold uppercase tracking-[.5px] text-[#9aa7be]">
            Match
          </div>
        </div>
      </div>

      <div className="mt-[22px] flex flex-wrap gap-[30px] border-t border-[#eef2f8] pt-[22px]">
        <div className="min-w-[260px] flex-1">
          <div className="mb-[14px] text-xs font-bold uppercase tracking-[.5px] text-[#9aa7be]">
            Score breakdown
          </div>
          <div className="flex flex-col gap-[13px]">
            {d.breakdown.map((bar) => (
              <div key={bar.name}>
                <div className="mb-[5px] flex justify-between text-[13.5px]">
                  <span className="font-semibold text-[#44546f]">
                    {DIMENSION_LABEL[bar.name] ?? bar.name}
                  </span>
                  <span className="font-bold tabular-nums">{Math.round(bar.raw_score * 100)}%</span>
                </div>
                <div className="h-[7px] overflow-hidden rounded-full bg-[#eef2f8]">
                  <div
                    className="h-full rounded-full transition-[width] duration-500"
                    style={{
                      width: `${Math.round(bar.raw_score * 100)}%`,
                      background: DIMENSION_COLOR[bar.name] ?? accent,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="min-w-[240px] flex-1">
          <div className="mb-[14px] text-xs font-bold uppercase tracking-[.5px] text-[#9aa7be]">
            Cutoff vs. you
          </div>
          <div className="relative mb-2 h-2 rounded-full bg-[#eef2f8]">
            <div
              className="absolute -top-1 bottom-[-4px] w-[2px] bg-[#aab5c8]"
              style={{ left: "50%" }}
            />
            <div
              className="absolute top-1/2 h-[13px] w-[13px] -translate-x-1/2 -translate-y-1/2 rounded-full border-[2.5px] border-white shadow-[0_1px_4px_rgba(20,36,59,.25)]"
              style={{ left: `${youPos}%`, background: youColor }}
            />
          </div>
          <div className="mb-[18px] flex justify-between text-[13px]">
            <span className="text-[#7c89a0]">
              Cutoff{" "}
              <strong className="tabular-nums text-[#44546f]">
                {d.cutoff_z_score.toFixed(4)}
              </strong>
            </span>
            <span className="font-bold tabular-nums" style={{ color: youColor }}>
              You {(d.student_margin >= 0 ? "+" : "") + d.student_margin.toFixed(2)}
            </span>
          </div>
          {d.is_marginal ? (
            <p className="text-[12.5px] leading-[1.4] text-[#b07407]">
              Close to the cutoff — next year&apos;s could shift and change this result.
            </p>
          ) : null}
        </div>
      </div>

      <div className="mt-5 border-t border-[#eef2f8] pt-[18px] text-[13px] text-[#9aa7be]">
        {d.selection_basis === "all_island_merit" ? "All-island merit selection" : "District quota selection"}
      </div>
    </article>
  );
}
