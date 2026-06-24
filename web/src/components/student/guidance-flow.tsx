"use client";

import { useEffect, useMemo, useState } from "react";

import { ChatPanel } from "@/components/student/chat-panel";
import { ResultsView } from "@/components/student/results-view";
import type {
  ReferenceData,
  RecommendationRequest,
  RecommendationResponse,
  SubjectInput,
} from "@/lib/guidance-types";

const ACCENT = "#2b5fd0";
const STEP_LABELS = ["Z-score", "District", "Stream", "Subjects", "Preferences"];
const TOTAL_STEPS = STEP_LABELS.length;
const GRADES: SubjectInput["grade"][] = ["A", "B", "C", "S"];

// The 6 real A/L exam streams a student actually sits. ICT is a navigation
// category on the courses side (masterplan §3), not something a student
// "was in" -- so it is deliberately excluded from this picker even though
// the reference endpoint returns it.
const STREAM_ICONS: Record<string, React.ReactNode> = {
  PHYSICAL_SCIENCE: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.6" />
      <ellipse cx="12" cy="12" rx="10" ry="4.5" stroke="currentColor" strokeWidth="1.6" />
      <ellipse cx="12" cy="12" rx="10" ry="4.5" stroke="currentColor" strokeWidth="1.6" transform="rotate(60 12 12)" />
      <ellipse cx="12" cy="12" rx="10" ry="4.5" stroke="currentColor" strokeWidth="1.6" transform="rotate(120 12 12)" />
    </svg>
  ),
  BIO_SCIENCE: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
      <path d="M7 3c0 5 10 5 10 9s-10 4-10 9M17 3c0 5-10 5-10 9s10 4 10 9" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  ),
  COMMERCE: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
      <path d="M4 20V10M9.5 20V5M15 20v-7M20.5 20V8" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  ),
  ARTS: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
      <path d="M4 19.5h16M6 19.5V8l6-4 6 4v11.5M10 19.5V13h4v6.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  ENGINEERING_TECH: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
      <path d="M9 18l-5-6 5-6M15 6l5 6-5 6" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  BIOSYSTEMS_TECH: (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
      <path d="M12 3v6M12 15v6M5 12h6M13 12h6" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.4" />
    </svg>
  ),
};

type View = "flow" | "results";

export function GuidanceFlow() {
  const [reference, setReference] = useState<ReferenceData | null>(null);
  const [refError, setRefError] = useState(false);

  const [view, setView] = useState<View>("flow");
  const [step, setStep] = useState(0);
  const [zScore, setZScore] = useState(1.5);
  const [districtCode, setDistrictCode] = useState<string | null>(null);
  const [streamCode, setStreamCode] = useState<string | null>(null);
  const [subjects, setSubjects] = useState<(SubjectInput | null)[]>([null, null, null]);
  const [preferredUnis, setPreferredUnis] = useState<string[]>([]);
  const [interests, setInterests] = useState("");

  const [results, setResults] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/public/reference")
      .then((r) => (r.ok ? r.json() : Promise.reject(r)))
      .then((d: ReferenceData) => setReference(d))
      .catch(() => setRefError(true));
  }, []);

  const examStreams = useMemo(
    () => (reference?.streams ?? []).filter((s) => s.code !== "ICT"),
    [reference],
  );

  function toggleUni(code: string) {
    setPreferredUnis((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code],
    );
  }

  async function submit() {
    const filledSubjects = subjects.filter((s): s is SubjectInput => s !== null);
    if (!districtCode || !streamCode || filledSubjects.length !== 3) return;
    setLoading(true);
    setSubmitError(null);
    const payload: RecommendationRequest = {
      z_score: Math.round(zScore * 100) / 100,
      district_code: districtCode,
      stream_code: streamCode,
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
      setView("results");
      window.scrollTo(0, 0);
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
  }

  const stepValid = !(
    (step === 1 && !districtCode) ||
    (step === 2 && !streamCode) ||
    (step === 3 && subjects.filter(Boolean).length !== 3)
  );
  const isResults = view === "results";
  const progressPct = isResults ? 100 : ((step + 1) / TOTAL_STEPS) * 100;
  const districtName = reference?.districts.find((d) => d.code === districtCode)?.name_en ?? "";
  const streamName = examStreams.find((s) => s.code === streamCode)?.name_en ?? "";

  if (refError) {
    return (
      <div className="flex min-h-screen items-center justify-center p-6 text-center">
        <p className="text-[#5b6b85]">
          Couldn&apos;t reach the guidance service. Please refresh, or try again shortly.
        </p>
      </div>
    );
  }

  return (
    <div className="relative flex min-h-screen flex-col text-[#16243b]">
      <header className="sticky top-0 z-40 border-b border-[#e3e9f2] bg-white/86 backdrop-blur">
        <div className="mx-auto flex h-[66px] max-w-[1120px] items-center justify-between gap-4 px-6">
          <button
            onClick={() => {
              window.scrollTo(0, 0);
              setView("flow");
              setStep(0);
            }}
            className="flex flex-shrink-0 items-center gap-[11px]"
          >
            <div
              className="flex h-9 w-9 items-center justify-center rounded-[10px] shadow-[0_3px_10px_rgba(43,95,208,.3)]"
              style={{ background: ACCENT }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L3 7l9 5 9-5-9-5z" fill="#fff" />
                <path d="M3 12l9 5 9-5M3 17l9 5 9-5" stroke="#fff" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <div className="text-left leading-[1.05]">
              <div className="text-[17px] font-bold tracking-[-.2px]">Degree Guidance</div>
              <div className="text-[11px] font-medium text-[#7c89a0]">Sri Lankan A/L admissions</div>
            </div>
          </button>

          {!isResults ? (
            <nav className="hidden items-center gap-[18px] sm:flex">
              {STEP_LABELS.map((label, i) => {
                const done = i < step;
                const active = i === step;
                return (
                  <div key={label} className="flex items-center gap-[9px]">
                    <span
                      className="flex h-[25px] w-[25px] items-center justify-center rounded-full border-[1.5px] text-[12.5px] font-bold transition-colors"
                      style={{
                        background: done || active ? ACCENT : "#fff",
                        color: done || active ? "#fff" : "#9aa7be",
                        borderColor: done || active ? ACCENT : "#d4dce8",
                      }}
                    >
                      {done ? "✓" : i + 1}
                    </span>
                    <span
                      className="text-[13.5px] font-semibold"
                      style={{ color: done || active ? "#16243b" : "#9aa7be" }}
                    >
                      {label}
                    </span>
                  </div>
                );
              })}
            </nav>
          ) : null}
          <div className="w-9 flex-shrink-0 sm:hidden" />
        </div>
        <div className="h-[3px] bg-[#e9eef6]">
          <div
            className="h-full rounded-r-[3px] transition-[width] duration-500"
            style={{ background: ACCENT, width: `${progressPct}%` }}
          />
        </div>
      </header>

      {!isResults ? (
        <main className="mx-auto w-full max-w-[1120px] flex-1 px-6">
          <div className="mx-auto max-w-[780px] py-[54px] pb-[100px]">
            {!reference ? (
              <p className="text-[#7c89a0]">Loading…</p>
            ) : (
              <>
                {step === 0 && (
                  <ZScoreStep value={zScore} onChange={setZScore} accent={ACCENT} />
                )}
                {step === 1 && (
                  <DistrictStep
                    districts={reference.districts}
                    selected={districtCode}
                    onPick={setDistrictCode}
                    accent={ACCENT}
                  />
                )}
                {step === 2 && (
                  <StreamStep
                    streams={examStreams}
                    selected={streamCode}
                    onPick={setStreamCode}
                    accent={ACCENT}
                  />
                )}
                {step === 3 && (
                  <SubjectsStep
                    stream={examStreams.find((s) => s.code === streamCode) ?? null}
                    subjects={subjects}
                    onChange={setSubjects}
                    accent={ACCENT}
                  />
                )}
                {step === 4 && (
                  <PreferencesStep
                    universities={reference.universities}
                    selectedUnis={preferredUnis}
                    onToggleUni={toggleUni}
                    interests={interests}
                    onInterests={setInterests}
                    accent={ACCENT}
                  />
                )}

                {submitError ? (
                  <p className="mt-6 text-sm text-[#b4485f]">{submitError}</p>
                ) : null}

                <div className="mt-12 flex items-center justify-between">
                  <button
                    onClick={back}
                    className="rounded-xl px-[22px] py-[13px] text-[15px] font-semibold text-[#7c89a0]"
                    style={{ visibility: step > 0 ? "visible" : "hidden" }}
                  >
                    ← Back
                  </button>
                  <button
                    onClick={next}
                    disabled={!stepValid || loading}
                    className="rounded-[13px] px-[34px] py-[15px] text-[16px] font-bold text-white shadow-[0_6px_18px_rgba(43,95,208,.28)] transition-opacity disabled:cursor-not-allowed"
                    style={{
                      background: stepValid ? ACCENT : "#aebbd2",
                      opacity: loading ? 0.7 : 1,
                    }}
                  >
                    {loading ? "Finding matches…" : step === TOTAL_STEPS - 1 ? "See my matches →" : "Continue"}
                  </button>
                </div>
              </>
            )}
          </div>
        </main>
      ) : results ? (
        <>
          <ResultsView
            results={results}
            zScore={zScore}
            districtName={districtName}
            streamName={streamName}
            onEdit={edit}
            accent={ACCENT}
          />
          <ChatPanel
            context={{
              z_score: zScore,
              district_code: districtCode ?? undefined,
              stream_code: streamCode ?? undefined,
              subjects: subjects.filter((s): s is SubjectInput => s !== null),
            }}
          />
        </>
      ) : null}
    </div>
  );
}

function StepKicker({ step, accent }: { step: number; accent: string }) {
  return (
    <div
      className="mb-[14px] text-[13px] font-bold uppercase tracking-[1.5px]"
      style={{ color: accent }}
    >
      Step {step} of {TOTAL_STEPS}
    </div>
  );
}

function ZScoreStep({
  value,
  onChange,
  accent,
}: {
  value: number;
  onChange: (v: number) => void;
  accent: string;
}) {
  const pct = ((value + 1) / 4) * 100;
  return (
    <section>
      <StepKicker step={1} accent={accent} />
      <h1 className="mb-3 font-[family-name:var(--font-newsreader)] text-5xl font-medium leading-[1.08] tracking-[-.5px]">
        What is your Z-score?
      </h1>
      <p className="mb-11 max-w-[520px] text-[17px] leading-[1.55] text-[#5b6b85]">
        Enter the Z-score from your G.C.E. A/L results. It determines which university programmes
        you&apos;re eligible for.
      </p>
      <div className="rounded-[22px] border border-[#e3e9f2] bg-white p-10 shadow-[0_1px_3px_rgba(20,36,59,.04)]">
        <div className="flex items-center justify-center gap-7">
          <button
            onClick={() => onChange(Math.max(-1, Math.round((value - 0.01) * 100) / 100))}
            className="h-12 w-12 flex-shrink-0 rounded-full border-[1.5px] border-[#e3e9f2] text-2xl font-semibold text-[#44546f]"
          >
            −
          </button>
          <div
            className="min-w-[200px] text-center font-[family-name:var(--font-newsreader)] text-7xl font-medium tracking-[-2px] tabular-nums sm:text-8xl"
            style={{ color: accent }}
          >
            {value.toFixed(2)}
          </div>
          <button
            onClick={() => onChange(Math.min(3, Math.round((value + 0.01) * 100) / 100))}
            className="h-12 w-12 flex-shrink-0 rounded-full border-[1.5px] border-[#e3e9f2] text-2xl font-semibold text-[#44546f]"
          >
            +
          </button>
        </div>
        <input
          type="range"
          min={-1}
          max={3}
          step={0.01}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="my-[34px] w-full"
          style={{
            background: `linear-gradient(90deg,${accent} ${pct}%,#e3e9f2 ${pct}%)`,
            height: 6,
            borderRadius: 999,
            appearance: "none",
          }}
        />
        <div className="flex justify-between text-[13px] font-medium text-[#9aa7be]">
          <span>−1.00</span>
          <span>1.00</span>
          <span>3.00</span>
        </div>
        <div className="mt-[26px] border-t border-dashed border-[#e3e9f2] pt-[22px] text-center text-[14.5px] leading-[1.5] text-[#7c89a0]">
          Eligibility is checked against the real, verified 2023 cutoffs for every course in your
          stream and district.
        </div>
      </div>
    </section>
  );
}

function DistrictStep({
  districts,
  selected,
  onPick,
  accent,
}: {
  districts: ReferenceData["districts"];
  selected: string | null;
  onPick: (code: string) => void;
  accent: string;
}) {
  return (
    <section>
      <StepKicker step={2} accent={accent} />
      <h1 className="mb-3 font-[family-name:var(--font-newsreader)] text-5xl font-medium leading-[1.08] tracking-[-.5px]">
        Which district did you apply from?
      </h1>
      <p className="mb-9 max-w-[560px] text-[17px] leading-[1.55] text-[#5b6b85]">
        University selection uses a district quota, so the same Z-score can mean different things
        depending on where you applied.
      </p>
      <div className="flex flex-wrap gap-[10px]">
        {districts.map((d) => {
          const sel = selected === d.code;
          return (
            <button
              key={d.code}
              onClick={() => onPick(d.code)}
              className="rounded-xl border-[1.5px] px-4 py-[11px] text-[14.5px] font-semibold transition-colors"
              style={{
                borderColor: sel ? accent : "#e3e9f2",
                background: sel ? `color-mix(in srgb, ${accent} 9%, #fff)` : "#fff",
                color: sel ? `color-mix(in srgb, ${accent} 78%, #000)` : "#44546f",
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

function StreamStep({
  streams,
  selected,
  onPick,
  accent,
}: {
  streams: ReferenceData["streams"];
  selected: string | null;
  onPick: (code: string) => void;
  accent: string;
}) {
  return (
    <section>
      <StepKicker step={3} accent={accent} />
      <h1 className="mb-3 font-[family-name:var(--font-newsreader)] text-5xl font-medium leading-[1.08] tracking-[-.5px]">
        What was your A/L stream?
      </h1>
      <p className="mb-9 max-w-[520px] text-[17px] leading-[1.55] text-[#5b6b85]">
        This sets the pool of degree programmes you can be considered for.
      </p>
      <div className="grid grid-cols-1 gap-[14px] sm:grid-cols-2">
        {streams.map((s) => {
          const sel = selected === s.code;
          return (
            <button
              key={s.code}
              onClick={() => onPick(s.code)}
              className="rounded-[18px] border-[1.5px] p-6 text-left transition-colors"
              style={{
                borderColor: sel ? accent : "#e3e9f2",
                background: sel ? `color-mix(in srgb, ${accent} 9%, #fff)` : "#fff",
              }}
            >
              <div className="mb-3" style={{ color: sel ? accent : "#7c89a0" }}>
                {STREAM_ICONS[s.code] ?? null}
              </div>
              <div className="mb-1 text-lg font-bold">{s.name_en}</div>
              <div className="text-[13.5px] leading-[1.45] text-[#7c89a0]">
                {s.subjects.length ? s.subjects.join(" · ") : "Subject combination varies"}
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function SubjectsStep({
  stream,
  subjects,
  onChange,
  accent,
}: {
  stream: ReferenceData["streams"][number] | null;
  subjects: (SubjectInput | null)[];
  onChange: (next: (SubjectInput | null)[]) => void;
  accent: string;
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
      <StepKicker step={4} accent={accent} />
      <h1 className="mb-3 font-[family-name:var(--font-newsreader)] text-5xl font-medium leading-[1.08] tracking-[-.5px]">
        What were your 3 A/L subjects?
      </h1>
      <p className="mb-9 max-w-[560px] text-[17px] leading-[1.55] text-[#5b6b85]">
        Many degrees require specific subjects beyond your stream — for example, Engineering
        requires Chemistry specifically, while a Physics+Maths+ICT combination doesn&apos;t
        qualify. This lets us check exactly, not just by stream.
      </p>
      {!options.length ? (
        <p className="text-sm text-[#b4485f]">Pick a stream first to see its subject list.</p>
      ) : (
        <div className="flex flex-col gap-[14px]">
          {[0, 1, 2].map((i) => {
            const current = subjects[i];
            const available = options.filter(
              (o) => o === current?.subject || !pickedNames.has(o),
            );
            return (
              <div
                key={i}
                className="flex flex-wrap items-center gap-3 rounded-2xl border-[1.5px] border-[#e3e9f2] bg-white p-4"
              >
                <span className="w-6 text-sm font-bold text-[#9aa7be]">{i + 1}.</span>
                <select
                  value={current?.subject ?? ""}
                  onChange={(e) => setSlotSubject(i, e.target.value)}
                  className="min-w-[220px] flex-1 rounded-xl border-[1.5px] border-[#e3e9f2] bg-white px-3 py-[10px] text-[15px]"
                >
                  <option value="">Select subject…</option>
                  {available.map((o) => (
                    <option key={o} value={o}>
                      {o}
                    </option>
                  ))}
                </select>
                <div className="flex gap-[6px]">
                  {GRADES.map((g) => {
                    const sel = current?.grade === g;
                    return (
                      <button
                        key={g}
                        type="button"
                        disabled={!current}
                        onClick={() => setSlotGrade(i, g)}
                        className="h-9 w-9 rounded-lg border-[1.5px] text-[14px] font-bold disabled:opacity-40"
                        style={{
                          borderColor: sel ? accent : "#e3e9f2",
                          background: sel ? accent : "#fff",
                          color: sel ? "#fff" : "#44546f",
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
      <p className="mt-4 text-[13px] text-[#9aa7be]">Grades: A (highest) · B · C · S (ordinary pass)</p>
    </section>
  );
}

function PreferencesStep({
  universities,
  selectedUnis,
  onToggleUni,
  interests,
  onInterests,
  accent,
}: {
  universities: ReferenceData["universities"];
  selectedUnis: string[];
  onToggleUni: (code: string) => void;
  interests: string;
  onInterests: (v: string) => void;
  accent: string;
}) {
  return (
    <section>
      <div className="mb-[14px] flex items-baseline gap-3">
        <div className="text-[13px] font-bold uppercase tracking-[1.5px]" style={{ color: accent }}>
          Step {TOTAL_STEPS} of {TOTAL_STEPS}
        </div>
        <div className="text-[13px] font-semibold text-[#9aa7be]">Optional</div>
      </div>
      <h1 className="mb-3 font-[family-name:var(--font-newsreader)] text-5xl font-medium leading-[1.08] tracking-[-.5px]">
        Any universities you&apos;d prefer?
      </h1>
      <p className="mb-9 max-w-[560px] text-[17px] leading-[1.55] text-[#5b6b85]">
        We&apos;ll rank matches at your chosen universities higher. Skip this and we&apos;ll rank
        purely by how safely you clear the cutoff.
      </p>

      <div className="mb-3 text-sm font-bold text-[#44546f]">Preferred universities</div>
      <div className="mb-9 flex flex-wrap gap-[10px]">
        {universities.map((u) => {
          const sel = selectedUnis.includes(u.code);
          return (
            <button
              key={u.code}
              onClick={() => onToggleUni(u.code)}
              className="rounded-full border-[1.5px] px-[18px] py-[11px] text-[14.5px] font-semibold"
              style={{
                borderColor: sel ? accent : "#e3e9f2",
                background: sel ? `color-mix(in srgb, ${accent} 9%, #fff)` : "#fff",
                color: sel ? `color-mix(in srgb, ${accent} 78%, #000)` : "#44546f",
              }}
            >
              {u.short_name || u.code}
            </button>
          );
        })}
      </div>

      <div className="mb-[14px] text-sm font-bold text-[#44546f]">
        Anything you&apos;re leaning toward? (in your own words)
      </div>
      <textarea
        value={interests}
        onChange={(e) => onInterests(e.target.value)}
        rows={4}
        placeholder="e.g. I love problem-solving and coding, and want a degree with strong job prospects."
        className="w-full resize-y rounded-2xl border-[1.5px] border-[#e3e9f2] bg-white px-[18px] py-4 text-[15px] leading-[1.6] text-[#16243b] outline-none"
        style={{ minHeight: 110 }}
      />
      <div className="mt-[9px] flex items-start gap-2 text-[13px] leading-[1.5] text-[#9aa7be]">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" className="mt-[2px] flex-shrink-0">
          <path d="M12 2L3 7l9 5 9-5-9-5z" fill="#aab5c8" />
        </svg>
        We save this with your results. It doesn&apos;t affect ranking yet — interest-based
        matching is coming soon.
      </div>
    </section>
  );
}
