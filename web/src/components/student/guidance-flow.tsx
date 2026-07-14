"use client";

import { useEffect, useMemo, useState } from "react";

import { ChatPanel } from "@/components/student/chat-panel";
import { ResultsView } from "@/components/student/results-view";
import type {
  ExamYear,
  ReferenceData,
  RecommendationRequest,
  RecommendationResponse,
  SubjectInput,
  YearsResponse,
} from "@/lib/guidance-types";

const LAST_RUN_KEY = "dg_last_run";
const THEME_KEY = "dg-theme";
const STEP_LABELS = ["Z-score", "District", "Stream", "Subjects", "Preferences"];
const TOTAL_STEPS = STEP_LABELS.length;
const GRADES: SubjectInput["grade"][] = ["A", "B", "C", "S"];

// Short one-line descriptors shown under each stream card. Keyed by our real
// stream codes. ICT is intentionally absent — it is filtered from the picker.
const STREAM_DESC: Record<string, string> = {
  PHYSICAL_SCIENCE: "Maths, Physics, Chemistry — engineering, computing & physical sciences.",
  BIO_SCIENCE: "Biology-based — medicine, life sciences & agriculture.",
  COMMERCE: "Accounting, Economics & Business — management & finance.",
  ARTS: "Languages, humanities & social sciences.",
  ENGINEERING_TECH: "Applied engineering & technology degrees.",
  BIOSYSTEMS_TECH: "Agri & bio-based applied technology.",
};

type View = "flow" | "results";
type Tab = "results" | "chat";

export function GuidanceFlow() {
  const [reference, setReference] = useState<ReferenceData | null>(null);
  const [refError, setRefError] = useState(false);

  const [dark, setDark] = useState(false);
  const [view, setView] = useState<View>("flow");
  const [activeTab, setActiveTab] = useState<Tab>("results");
  const [chatKey, setChatKey] = useState(0);
  const [step, setStep] = useState(0);
  const [zScore, setZScore] = useState(1.5);
  const [districtCode, setDistrictCode] = useState<string | null>(null);
  const [streamCode, setStreamCode] = useState<string | null>(null);
  const [subjects, setSubjects] = useState<(SubjectInput | null)[]>([null, null, null]);
  const [preferredUnis, setPreferredUnis] = useState<string[]>([]);
  const [interests, setInterests] = useState("");

  // Exam years with promoted cutoff data (newest first). examYear is what the
  // student is viewing; null = "use the engine's default (latest)".
  const [years, setYears] = useState<ExamYear[]>([]);
  const [examYear, setExamYear] = useState<number | null>(null);

  const [results, setResults] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Self-contained light/dark for the student shell (drives the --dg-* tokens).
  // Independent of the admin theme. Read the saved choice once on mount…
  useEffect(() => {
    try {
      setDark(localStorage.getItem(THEME_KEY) === "dark");
    } catch {
      /* storage blocked — stay light */
    }
  }, []);
  // …then reflect it onto <html> so the whole student route (including the
  // layout wrapper behind this shell) themes together, not just this subtree.
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", dark ? "dark" : "light");
  }, [dark]);
  function toggleTheme() {
    setDark((d) => {
      const next = !d;
      try {
        localStorage.setItem(THEME_KEY, next ? "dark" : "light");
      } catch {
        /* ignore */
      }
      return next;
    });
  }

  useEffect(() => {
    fetch("/api/public/reference")
      .then((r) => (r.ok ? r.json() : Promise.reject(r)))
      .then((d: ReferenceData) => setReference(d))
      .catch(() => setRefError(true));
    // Years are progressive enhancement: if this fails, the flow still works —
    // requests just omit exam_year and the engine serves its default (latest).
    fetch("/api/public/years")
      .then((r) => (r.ok ? r.json() : Promise.reject(r)))
      .then((d: YearsResponse) => setYears(d.years))
      .catch(() => {});
  }, []);

  // Restore the last completed run so a returning visitor lands straight on
  // their results instead of re-entering Z-score / district / subjects.
  useEffect(() => {
    try {
      const raw = localStorage.getItem(LAST_RUN_KEY);
      if (!raw) return;
      const saved = JSON.parse(raw);
      // Version gate: a run saved by an OLDER build may lack fields the
      // current results view renders (a mid-deploy student crashed exactly
      // this way on the later-rounds fields). Discard stale shapes — the
      // student just re-runs the 5 steps once.
      if (!saved?.results || saved.v !== 2) return;
      if (typeof saved.zScore === "number") setZScore(saved.zScore);
      setDistrictCode(saved.districtCode ?? null);
      setStreamCode(saved.streamCode ?? null);
      if (Array.isArray(saved.subjects)) setSubjects(saved.subjects);
      setPreferredUnis(saved.preferredUnis ?? []);
      setInterests(saved.interests ?? "");
      if (typeof saved.examYear === "number") setExamYear(saved.examYear);
      setResults(saved.results);
      setView("results");
      setActiveTab("results");
    } catch {
      // Corrupt/blocked storage — start fresh, no harm done.
    }
  }, []);

  // A remembered year must still exist on the server: if an admin re-labels
  // or removes a dataset, a browser that saved that year would otherwise keep
  // requesting it forever and stare at a ghost-empty "verified YYYY" view.
  // Drop it to the engine default (latest) and, if stale results are on
  // screen, re-run against the default so the view self-heals.
  useEffect(() => {
    if (examYear === null || years.length === 0) return;
    if (years.some((y) => y.year === examYear)) return;
    setExamYear(null);
    if (results !== null) void submit(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps -- one-shot heal on years arrival
  }, [years, examYear]);

  const examStreams = useMemo(
    () => (reference?.streams ?? []).filter((s) => s.code !== "ICT"),
    [reference],
  );

  function toggleUni(code: string) {
    setPreferredUnis((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code],
    );
  }

  async function submit(yearOverride?: number | null) {
    const filledSubjects = subjects.filter((s): s is SubjectInput => s !== null);
    if (!districtCode || !streamCode || filledSubjects.length !== 3) return;
    setLoading(true);
    setSubmitError(null);
    // undefined = keep the current selection; null = force the engine default
    const year = yearOverride === undefined ? examYear : yearOverride;
    const payload: RecommendationRequest = {
      z_score: zScore,
      district_code: districtCode,
      stream_code: streamCode,
      // Omitted when unknown — the engine then serves the latest promoted year.
      ...(year != null ? { exam_year: year } : {}),
      subjects: filledSubjects,
      preferred_university_codes: preferredUnis,
      interests: interests.trim() || null,
    };
    try {
      const res = await fetch("/api/public/recommendations", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(
          typeof body?.detail === "string" ? body.detail : `Request failed (${res.status})`,
        );
      }
      const data: RecommendationResponse = await res.json();
      setResults(data);
      setExamYear(data.exam_year_used); // server truth wins
      setView("results");
      setActiveTab("results");
      window.scrollTo(0, 0);
      // Persist the run so it survives a page reload / return visit.
      try {
        localStorage.setItem(
          LAST_RUN_KEY,
          JSON.stringify({
            v: 2, // bump when the results shape changes (see restore gate)
            zScore,
            districtCode,
            streamCode,
            subjects,
            preferredUnis,
            interests,
            examYear: data.exam_year_used,
            results: data,
            savedAt: Date.now(),
          }),
        );
      } catch {
        // Storage full/blocked — non-fatal, the run still shows this session.
      }
    } catch (e) {
      setSubmitError(e instanceof Error ? e.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function next() {
    if (step === 1 && !districtCode) return;
    if (step === 2 && !streamCode) return;
    if (step === 3 && subjects.filter(Boolean).length !== 3) return;
    if (step < TOTAL_STEPS - 1) {
      window.scrollTo(0, 0);
      setStep(step + 1);
    } else {
      submit();
    }
  }
  function back() {
    if (step > 0) {
      window.scrollTo(0, 0);
      setStep(step - 1);
    }
  }
  function edit() {
    window.scrollTo(0, 0);
    setView("flow");
    setStep(0);
    setActiveTab("results");
  }

  const stepValid = !(
    (step === 1 && !districtCode) ||
    (step === 2 && !streamCode) ||
    (step === 3 && subjects.filter(Boolean).length !== 3)
  );
  const isResults = view === "results";
  const progressPct = ((step + 1) / TOTAL_STEPS) * 100;
  const districtName = reference?.districts.find((d) => d.code === districtCode)?.name_en ?? "";
  const streamName = examStreams.find((s) => s.code === streamCode)?.name_en ?? "";

  const shellStyle: React.CSSProperties = {
    background: "var(--dg-bg)",
    color: "var(--dg-ink)",
    fontFamily: "var(--font-public-sans), system-ui, sans-serif",
  };

  if (refError) {
    return (
      <div
        data-theme={dark ? "dark" : "light"}
        style={shellStyle}
        className="flex min-h-screen items-center justify-center p-6 text-center"
      >
        <p style={{ color: "var(--dg-muted)" }}>
          Couldn&apos;t reach the guidance service. Please refresh, or try again shortly.
        </p>
      </div>
    );
  }

  return (
    <div
      data-theme={dark ? "dark" : "light"}
      style={shellStyle}
      className="dg-scroll relative flex min-h-screen flex-col"
    >
      {/* ── Header ─────────────────────────────────────────────────────── */}
      <header
        className="sticky top-0 z-40 flex items-center justify-between gap-3 px-[18px] py-[14px] backdrop-blur"
        style={{
          background: "color-mix(in srgb, var(--dg-bg) 82%, transparent)",
          borderBottom: "1px solid var(--dg-border)",
        }}
      >
        <button
          onClick={() => {
            window.scrollTo(0, 0);
            setView("flow");
            setStep(0);
          }}
          className="flex items-center gap-[10px]"
        >
          <span
            className="grid h-[34px] w-[34px] place-items-center rounded-[9px]"
            style={{ background: "var(--dg-accent)", color: "var(--dg-accent-ink)", boxShadow: "var(--dg-shadow)" }}
          >
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 10 12 5 2 10l10 5 10-5Z" />
              <path d="M6 12v5c0 1 2.7 3 6 3s6-2 6-3v-5" />
            </svg>
          </span>
          <span
            className="text-[19px] font-bold tracking-[-.01em]"
            style={{ fontFamily: "var(--font-spectral), Georgia, serif" }}
          >
            Degree Guidance
          </span>
        </button>
        <div className="flex items-center gap-2">
          <span className="hidden text-[12.5px] sm:inline" style={{ color: "var(--dg-muted)" }}>
            Official UGC Z-score cutoffs
          </span>
          <button
            onClick={toggleTheme}
            aria-label="Toggle theme"
            className="grid h-[38px] w-[38px] place-items-center rounded-[10px]"
            style={{ background: "var(--dg-surface)", border: "1px solid var(--dg-border)", color: "var(--dg-muted)", boxShadow: "var(--dg-shadow)" }}
          >
            {dark ? (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
              </svg>
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
              </svg>
            )}
          </button>
        </div>
      </header>

      {!isResults ? (
        <main className="mx-auto w-full max-w-[600px] flex-1 px-5 pb-[120px] pt-[26px]">
          {!reference ? (
            <p style={{ color: "var(--dg-muted)" }}>Loading…</p>
          ) : (
            <>
              {/* progress */}
              <div className="mb-[26px] flex items-center gap-[14px]">
                <button
                  onClick={back}
                  className="grid h-10 w-10 flex-none place-items-center rounded-[10px]"
                  style={{
                    background: "var(--dg-surface)",
                    border: "1px solid var(--dg-border)",
                    color: "var(--dg-muted)",
                    visibility: step > 0 ? "visible" : "hidden",
                  }}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M19 12H5M11 18l-6-6 6-6" />
                  </svg>
                </button>
                <div className="flex-1">
                  <div className="mb-[7px] flex justify-between gap-[10px] text-[12.5px] font-medium" style={{ color: "var(--dg-muted)" }}>
                    <span>Step {step + 1} of {TOTAL_STEPS} · {STEP_LABELS[step]}</span>
                    <span>{Math.round(progressPct)}%</span>
                  </div>
                  <div className="h-[6px] overflow-hidden rounded-full" style={{ background: "var(--dg-track)" }}>
                    <div
                      className="h-full rounded-full transition-[width] duration-[350ms]"
                      style={{ width: `${progressPct}%`, background: "var(--dg-accent)" }}
                    />
                  </div>
                </div>
              </div>

              <div style={{ animation: "dgUp .3s ease" }}>
                {step === 0 && <ZScoreStep value={zScore} onChange={setZScore} latestYear={years.find((y) => y.is_latest)?.year ?? null} />}
                {step === 1 && <DistrictStep districts={reference.districts} selected={districtCode} onPick={setDistrictCode} />}
                {step === 2 && <StreamStep streams={examStreams} selected={streamCode} onPick={setStreamCode} />}
                {step === 3 && (
                  <SubjectsStep
                    stream={examStreams.find((s) => s.code === streamCode) ?? null}
                    subjects={subjects}
                    onChange={setSubjects}
                  />
                )}
                {step === 4 && (
                  <PreferencesStep
                    universities={reference.universities}
                    selectedUnis={preferredUnis}
                    onToggleUni={toggleUni}
                    interests={interests}
                    onInterests={setInterests}
                  />
                )}
              </div>

              {submitError ? <p className="mt-6 text-sm" style={{ color: "var(--dg-amb-fg)" }}>{submitError}</p> : null}
            </>
          )}

          {/* fixed bottom CTA */}
          {reference ? (
            <div
              className="fixed inset-x-0 bottom-0 px-5 py-[14px] backdrop-blur"
              style={{ background: "color-mix(in srgb, var(--dg-bg) 88%, transparent)", borderTop: "1px solid var(--dg-border)" }}
            >
              <div className="mx-auto max-w-[600px]">
                <button
                  onClick={next}
                  disabled={!stepValid || loading}
                  className="flex w-full items-center justify-center gap-[9px] rounded-[13px] p-4 text-[16px] font-semibold transition-all disabled:cursor-not-allowed"
                  style={{
                    background: stepValid ? "var(--dg-accent)" : "var(--dg-track)",
                    color: stepValid ? "var(--dg-accent-ink)" : "var(--dg-muted)",
                    opacity: loading ? 0.7 : 1,
                  }}
                >
                  {loading ? "Finding matches…" : step === TOTAL_STEPS - 1 ? "See my matches" : "Continue"}
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14M13 6l6 6-6 6" />
                  </svg>
                </button>
              </div>
            </div>
          ) : null}
        </main>
      ) : results ? (
        <>
          {/* ── Segmented Courses / AI Advisor ──────────────────────────── */}
          <div className="mx-auto w-full max-w-[1000px] px-[18px] pt-[22px]">
            <div
              className="inline-flex rounded-[12px] p-[4px]"
              style={{ background: "var(--dg-surface2)", border: "1px solid var(--dg-border)" }}
            >
              {(["results", "chat"] as Tab[]).map((tab) => {
                const active = activeTab === tab;
                return (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className="inline-flex items-center gap-[7px] rounded-[9px] px-4 py-[9px] text-[14px] font-semibold transition-colors"
                    style={{
                      background: active ? "var(--dg-surface)" : "transparent",
                      color: active ? "var(--dg-ink)" : "var(--dg-muted)",
                      boxShadow: active ? "var(--dg-shadow)" : "none",
                    }}
                  >
                    {tab === "results" ? (
                      <>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
                          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z" />
                        </svg>
                        Courses
                      </>
                    ) : (
                      <>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M12 8V4H8" />
                          <rect x="4" y="8" width="16" height="12" rx="2" />
                          <path d="M2 14h2M20 14h2M15 13v2M9 13v2" />
                        </svg>
                        AI Advisor
                      </>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {activeTab === "results" && (
            <ResultsView
              results={results}
              zScore={zScore}
              districtName={districtName}
              streamName={streamName}
              districtCode={districtCode ?? ""}
              streamCode={streamCode ?? ""}
              availableYears={years.map((y) => y.year)}
              yearLoading={loading}
              onYearChange={(y) => {
                setExamYear(y);
                submit(y);
              }}
              onEdit={edit}
              accent="var(--dg-accent)"
            />
          )}
          {activeTab === "chat" && (
            <ChatPanel
              key={chatKey}
              inline
              onNewChat={() => setChatKey((k) => k + 1)}
              context={{
                z_score: zScore,
                district_code: districtCode ?? undefined,
                stream_code: streamCode ?? undefined,
                exam_year: results.exam_year_used,
                subjects: subjects.filter((s): s is SubjectInput => s !== null),
                interests: interests.trim() || undefined,
                eligible_courses: results.recommendations.map((r) => ({
                  course_code: r.course_code,
                  course_name: r.course_name,
                  university: r.university_name,
                  cutoff: r.cutoff_z_score,
                  margin: r.student_margin,
                  bucket: r.bucket,
                })),
              }}
            />
          )}
        </>
      ) : null}
    </div>
  );
}

/* ── Shared step chrome ─────────────────────────────────────────────────── */

function StepHeading({ title, sub }: { title: React.ReactNode; sub: React.ReactNode }) {
  return (
    <>
      <h2 className="mb-[6px] text-[27px] font-bold tracking-[-.01em]" style={{ fontFamily: "var(--font-spectral), Georgia, serif" }}>
        {title}
      </h2>
      <p className="mb-[22px] text-[15px]" style={{ color: "var(--dg-muted)" }}>{sub}</p>
    </>
  );
}

/* ── Step 1: Z-score ────────────────────────────────────────────────────── */

function ZScoreStep({
  value,
  onChange,
  latestYear,
}: {
  value: number;
  onChange: (v: number) => void;
  latestYear: number | null;
}) {
  const [inputStr, setInputStr] = useState(value.toFixed(4));
  const [inputError, setInputError] = useState<string | null>(null);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const str = e.target.value;
    setInputStr(str);
    const num = parseFloat(str);
    if (isNaN(num)) {
      setInputError("Enter a valid number");
      return;
    }
    // Official standardisation can exceed 3 — real maximum is 4.0.
    if (num < -1 || num > 4) {
      setInputError("Z-score must be between −1.0000 and 4.0000");
      return;
    }
    setInputError(null);
    onChange(num);
  }

  const pct = Math.max(0, Math.min(100, ((value + 1) / 5) * 100)); // -1..4 → 0..100

  return (
    <section>
      <StepHeading
        title="What is your Z-score?"
        sub="Enter it exactly as shown on your results sheet — four decimal places."
      />
      <div className="rounded-[16px] p-[22px]" style={{ background: "var(--dg-surface)", border: "1px solid var(--dg-border)", boxShadow: "var(--dg-shadow)" }}>
        <input
          type="text"
          inputMode="decimal"
          value={inputStr}
          onChange={handleChange}
          placeholder="1.6500"
          className="w-full rounded-[12px] px-[18px] py-4 text-center text-[34px] font-semibold tracking-[.02em] tabular-nums outline-none"
          style={{
            background: "var(--dg-bg)",
            border: `1.5px solid ${inputError ? "var(--dg-amb-bd)" : "var(--dg-border)"}`,
            color: inputError ? "var(--dg-amb-fg)" : "var(--dg-ink)",
            fontFamily: "var(--font-spectral), Georgia, serif",
          }}
        />
        <div className="mt-[14px] flex justify-between text-[12.5px]" style={{ color: "var(--dg-muted)" }}>
          <span>Valid range: <strong style={{ color: "var(--dg-ink)" }}>−1.0000</strong></span>
          <span>to <strong style={{ color: "var(--dg-ink)" }}>4.0000</strong></span>
        </div>
        <div className="relative mt-[8px] h-[6px] rounded-full" style={{ background: "var(--dg-track)" }}>
          <div
            className="absolute top-1/2 h-[14px] w-[14px] -translate-x-1/2 -translate-y-1/2 rounded-full"
            style={{ left: `${pct}%`, background: "var(--dg-accent)", border: "2px solid var(--dg-surface)", boxShadow: "var(--dg-shadow)" }}
          />
        </div>
        {inputError ? (
          <p className="mt-[14px] flex items-center gap-[7px] text-[13px]" style={{ color: "var(--dg-amb-fg)" }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" /><path d="M12 8v4M12 16h.01" />
            </svg>
            {inputError}
          </p>
        ) : (
          <p className="mt-[14px] text-[13px]" style={{ color: "var(--dg-muted)" }}>
            Checked against the real, verified{latestYear ? ` ${latestYear}` : ""} cutoffs for every course in your
            stream and district. A typical strong score is around <strong style={{ color: "var(--dg-ink)" }}>1.8–2.4</strong>.
          </p>
        )}
      </div>
    </section>
  );
}

/* ── Step 2: District ───────────────────────────────────────────────────── */

function DistrictStep({
  districts,
  selected,
  onPick,
}: {
  districts: ReferenceData["districts"];
  selected: string | null;
  onPick: (code: string) => void;
}) {
  return (
    <section>
      <StepHeading
        title="Which district did you apply from?"
        sub="Cutoffs differ by district under the UGC quota system, so this matters."
      />
      <div className="flex flex-wrap gap-[9px]">
        {districts.map((d) => {
          const sel = selected === d.code;
          return (
            <button
              key={d.code}
              onClick={() => onPick(d.code)}
              className="rounded-full px-[15px] py-[10px] text-[14px] font-medium transition-all"
              style={{
                background: sel ? "var(--dg-accent)" : "var(--dg-surface)",
                color: sel ? "var(--dg-accent-ink)" : "var(--dg-ink)",
                border: `1px solid ${sel ? "var(--dg-accent)" : "var(--dg-border)"}`,
              }}
            >
              {d.name_en}
            </button>
          );
        })}
      </div>
    </section>
  );
}

/* ── Step 3: Stream (hover reveals the stream's subjects) ───────────────── */

function StreamStep({
  streams,
  selected,
  onPick,
}: {
  streams: ReferenceData["streams"];
  selected: string | null;
  onPick: (code: string) => void;
}) {
  return (
    <section>
      <StepHeading title="What was your A/L stream?" sub="Pick the stream you sat the exam in." />
      <div className="grid gap-[11px]">
        {streams.map((s) => {
          const sel = selected === s.code;
          const subjectPreview = s.subjects?.length ? s.subjects.join(" · ") : STREAM_DESC[s.code] ?? "";
          return (
            <button
              key={s.code}
              onClick={() => onPick(s.code)}
              title={subjectPreview}
              className="flex items-center gap-[14px] rounded-[14px] p-[16px_18px] text-left transition-all"
              style={{
                background: sel ? "var(--dg-accent-soft)" : "var(--dg-surface)",
                border: `1px solid ${sel ? "var(--dg-accent)" : "var(--dg-border)"}`,
              }}
            >
              <span
                className="grid h-[22px] w-[22px] flex-none place-items-center rounded-full"
                style={{ border: `2px solid ${sel ? "var(--dg-accent)" : "var(--dg-muted)"}`, color: sel ? "var(--dg-accent)" : "var(--dg-muted)" }}
              >
                {sel ? <span className="h-[10px] w-[10px] rounded-full" style={{ background: "currentColor" }} /> : null}
              </span>
              <span className="flex-1">
                <span className="block text-[15.5px] font-semibold" style={{ color: "var(--dg-ink)" }}>{s.name_en}</span>
                <span className="mt-[2px] block text-[13px]" style={{ color: "var(--dg-muted)" }}>
                  {STREAM_DESC[s.code] ?? subjectPreview}
                </span>
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

/* ── Step 4: Subjects (per-stream dropdown — our existing logic) ─────────── */

function SubjectsStep({
  stream,
  subjects,
  onChange,
}: {
  stream: ReferenceData["streams"][number] | null;
  subjects: (SubjectInput | null)[];
  onChange: (next: (SubjectInput | null)[]) => void;
}) {
  const options = stream?.subjects ?? [];
  const pickedNames = new Set(subjects.filter((s): s is SubjectInput => s !== null).map((s) => s.subject));

  function setSlotSubject(i: number, subject: string) {
    const next = [...subjects];
    next[i] = subject ? { subject, grade: next[i]?.grade ?? "C" } : null;
    onChange(next);
  }
  function setSlotGrade(i: number, grade: SubjectInput["grade"]) {
    const next = [...subjects];
    if (next[i]) next[i] = { ...next[i]!, grade };
    onChange(next);
  }

  return (
    <section>
      <StepHeading
        title="Your three subjects & grades"
        sub="Pick each subject from your stream and the grade you got — this lets us flag aptitude-test courses and check exact requirements."
      />
      {!options.length ? (
        <p className="text-sm" style={{ color: "var(--dg-amb-fg)" }}>Pick a stream first to see its subject list.</p>
      ) : (
        <div className="grid gap-[14px]">
          {[0, 1, 2].map((i) => {
            const current = subjects[i];
            const available = options.filter((o) => o === current?.subject || !pickedNames.has(o));
            return (
              <div key={i} className="rounded-[14px] p-[15px_16px]" style={{ background: "var(--dg-surface)", border: "1px solid var(--dg-border)" }}>
                <label className="mb-[8px] block text-[12px] font-semibold uppercase tracking-[.04em]" style={{ color: "var(--dg-muted)" }}>
                  Subject {i + 1}
                </label>
                <select
                  value={current?.subject ?? ""}
                  onChange={(e) => setSlotSubject(i, e.target.value)}
                  className="mb-[12px] w-full rounded-[10px] px-[13px] py-[11px] text-[15px] outline-none"
                  style={{ background: "var(--dg-bg)", border: "1px solid var(--dg-border)", color: "var(--dg-ink)" }}
                >
                  <option value="">Select subject…</option>
                  {available.map((o) => (
                    <option key={o} value={o}>{o}</option>
                  ))}
                </select>
                <div className="flex gap-[8px]">
                  {GRADES.map((g) => {
                    const sel = current?.grade === g;
                    return (
                      <button
                        key={g}
                        type="button"
                        disabled={!current}
                        onClick={() => setSlotGrade(i, g)}
                        className="flex-1 rounded-[9px] p-[10px] text-[15px] font-bold transition-all disabled:opacity-40"
                        style={{
                          background: sel ? "var(--dg-accent)" : "var(--dg-bg)",
                          color: sel ? "var(--dg-accent-ink)" : "var(--dg-muted)",
                          border: `1px solid ${sel ? "var(--dg-accent)" : "var(--dg-border)"}`,
                        }}
                      >
                        {g}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}
      <p className="mt-4 text-[13px]" style={{ color: "var(--dg-muted)" }}>Grades: A (highest) · B · C · S (ordinary pass)</p>
    </section>
  );
}

/* ── Step 5: Preferences (optional) ─────────────────────────────────────── */

function PreferencesStep({
  universities,
  selectedUnis,
  onToggleUni,
  interests,
  onInterests,
}: {
  universities: ReferenceData["universities"];
  selectedUnis: string[];
  onToggleUni: (code: string) => void;
  interests: string;
  onInterests: (v: string) => void;
}) {
  return (
    <section>
      <StepHeading
        title={<>Anything you&apos;re hoping for? <span className="text-[20px] font-medium italic" style={{ color: "var(--dg-muted)" }}>(optional)</span></>}
        sub="Totally optional. Leave it blank and we'll show you everything you qualify for, ranked by how safely you clear the cutoff."
      />
      <div className="mb-[20px]">
        <label className="mb-[11px] block text-[13px] font-semibold" style={{ color: "var(--dg-ink)" }}>Preferred universities</label>
        <div className="flex flex-wrap gap-[8px]">
          {universities.map((u) => {
            const sel = selectedUnis.includes(u.code);
            return (
              <button
                key={u.code}
                onClick={() => onToggleUni(u.code)}
                className="rounded-full px-[14px] py-[9px] text-[13.5px] font-medium transition-all"
                style={{
                  background: sel ? "var(--dg-accent)" : "var(--dg-surface)",
                  color: sel ? "var(--dg-accent-ink)" : "var(--dg-ink)",
                  border: `1px solid ${sel ? "var(--dg-accent)" : "var(--dg-border)"}`,
                }}
              >
                {u.short_name || u.code}
              </button>
            );
          })}
        </div>
      </div>
      <div className="mb-[6px]">
        <label className="mb-[11px] block text-[13px] font-semibold" style={{ color: "var(--dg-ink)" }}>What are you interested in?</label>
        <textarea
          value={interests}
          onChange={(e) => onInterests(e.target.value)}
          rows={3}
          placeholder="e.g. I love problem-solving and coding, and want a degree with strong job prospects."
          className="w-full resize-y rounded-[12px] px-[15px] py-[13px] text-[15px] leading-[1.5] outline-none"
          style={{ background: "var(--dg-surface)", border: "1px solid var(--dg-border)", color: "var(--dg-ink)", minHeight: 92 }}
        />
      </div>
      <p className="mt-[9px] text-[13px] leading-[1.5]" style={{ color: "var(--dg-muted)" }}>
        Programmes whose content matches what you write here are ranked higher using semantic similarity.
      </p>
    </section>
  );
}
