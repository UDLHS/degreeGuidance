"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Check, ChevronDown, MinusCircle, PlusCircle, TrendingUp, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

type ChangeType = "course_added" | "course_removed" | "cutoff_changed";
type ChangeStatus = "pending" | "approved" | "rejected" | "applied";

type CutoffDelta = { district: string; old: number | null; new: number | null };

type Change = {
  change_id: number;
  change_type: ChangeType;
  course_code: string;
  summary: string | null;
  before_value: Record<string, unknown> | null;
  after_value: Record<string, unknown> | null;
  status: ChangeStatus;
  // D6: the course number already has a curated baseline rule (e.g. re-added)
  subject_rule_exists?: boolean | null;
};

type ChangesResponse = { total: number; counts: Record<string, number>; items: Change[] };
type University = { university_id: number; university_code: string | null };
type Stream = { code: string; name_en: string };
type AddForm = {
  university_id: string;
  name_en: string;
  stream_codes: string[];
  // D6 — the JSON rule text the admin authors from the book's wording
  subject_rule: string;
};

// Deliberate one-click starters, not silent pre-fills: the admin still chooses.
const RULE_TEMPLATES: { label: string; json: string }[] = [
  {
    label: "Any 3 passes",
    json: '{"type": "any_n_subjects", "count": 3, "min_grade": "S"}',
  },
  {
    label: "One named subject + any 2",
    json:
      '{\n  "type": "and",\n  "conditions": [\n    {"type": "subject_min_grade", "subject": "Economics", "min_grade": "B"},\n    {"type": "any_n_subjects", "count": 3, "min_grade": "S"}\n  ]\n}',
  },
  {
    label: "3 from a list",
    json:
      '{\n  "type": "count_from_list",\n  "subjects": ["Biology", "Chemistry", "Physics"],\n  "count": 3,\n  "min_grade": "S"\n}',
  },
];

function parseRule(text: string): Record<string, unknown> | null {
  try {
    const v = JSON.parse(text);
    return v && typeof v === "object" && !Array.isArray(v) ? v : null;
  } catch {
    return null;
  }
}

// ICT is a subject, not an A/L stream — the student side never offers it as
// one, so it isn't offered here either. Same list the student picker uses.
const NOT_A_STREAM = "ICT";

const STATUS_STYLES: Record<ChangeStatus, string> = {
  pending: "bg-amber-100 text-amber-800",
  approved: "bg-blue-100 text-blue-800",
  rejected: "bg-zinc-200 text-zinc-600",
  applied: "bg-green-100 text-green-800",
};

const GROUPS: { type: ChangeType; label: string; icon: typeof PlusCircle; accent: string }[] = [
  { type: "course_added", label: "New courses", icon: PlusCircle, accent: "text-green-700" },
  { type: "course_removed", label: "Removed courses", icon: MinusCircle, accent: "text-red-700" },
  { type: "cutoff_changed", label: "Cutoff changes", icon: TrendingUp, accent: "text-amber-700" },
];

function Badge({ status }: { status: ChangeStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium capitalize",
        STATUS_STYLES[status],
      )}
    >
      {status}
    </span>
  );
}

export function ChangeSetReview({ runId }: { runId: string }) {
  const [data, setData] = useState<ChangesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [universities, setUniversities] = useState<University[]>([]);
  const [streams, setStreams] = useState<Stream[]>([]);
  const [forms, setForms] = useState<Record<number, AddForm>>({});
  const [busyId, setBusyId] = useState<number | null>(null);
  const [applying, setApplying] = useState(false);
  const [open, setOpen] = useState<Record<number, boolean>>({});
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const load = useCallback(async () => {
    const res = await fetch(`/api/bff/admin/ingestions/${runId}/changes`, { cache: "no-store" });
    if (res.ok) {
      const d: ChangesResponse = await res.json();
      setData(d);
      // Seed the inline add-course forms from what the book already told us
      // (Phase 9.2): name/university come from the book's own Uni-Codes
      // section, streams from its cutoff-column tag — a suggestion only, so
      // the admin still confirms. Anything already saved on the change wins.
      setForms((prev) => {
        const next = { ...prev };
        for (const c of d.items) {
          if (c.change_type === "course_added" && !next[c.change_id]) {
            const saved = c.after_value?.stream_codes as string[] | undefined;
            const suggested = c.after_value?.suggested_stream_codes as string[] | undefined;
            const savedRule = c.after_value?.subject_rule as Record<string, unknown> | undefined;
            // 9.6b — a rule READ from the book's own sentence (only when the
            // whole sentence parsed; validated against catalog subject names).
            // Pre-filled for review, marked as book-derived in the UI.
            const suggestedRule = c.after_value?.suggested_subject_rule as
              | Record<string, unknown>
              | undefined;
            const rule = savedRule ?? suggestedRule;
            next[c.change_id] = {
              university_id: String((c.after_value?.university_id as number) ?? ""),
              name_en: String((c.after_value?.name_en as string) ?? ""),
              stream_codes: (saved ?? suggested ?? []).filter((s) => s !== NOT_A_STREAM),
              subject_rule: rule ? JSON.stringify(rule, null, 2) : "",
            };
          }
        }
        return next;
      });
    }
    setLoading(false);
  }, [runId]);

  useEffect(() => {
    load();
  }, [load]);

  // university dropdown — deduped from the courses list (no dedicated endpoint)
  useEffect(() => {
    (async () => {
      const res = await fetch("/api/bff/admin/courses?limit=200", { cache: "no-store" });
      if (!res.ok) return;
      const d = await res.json();
      const seen = new Map<number, University>();
      for (const c of d.items ?? []) {
        if (!seen.has(c.university_id))
          seen.set(c.university_id, { university_id: c.university_id, university_code: c.university_code });
      }
      setUniversities(
        Array.from(seen.values()).sort((a, b) =>
          (a.university_code ?? "").localeCompare(b.university_code ?? ""),
        ),
      );
    })();
  }, []);

  // Stream catalog for the eligibility ticks — public reference data, the same
  // source the Courses page uses. ICT is dropped: see NOT_A_STREAM.
  useEffect(() => {
    (async () => {
      const res = await fetch("/api/public/reference", { cache: "no-store" });
      if (!res.ok) return;
      const d = await res.json();
      setStreams(
        (d.streams ?? [])
          .map((s: { code: string; name_en: string }) => ({ code: s.code, name_en: s.name_en }))
          .filter((s: Stream) => s.code !== NOT_A_STREAM),
      );
    })();
  }, []);

  function toggleStream(changeId: number, code: string) {
    setForms((p) => {
      const f = p[changeId] ?? { university_id: "", name_en: "", stream_codes: [], subject_rule: "" };
      return {
        ...p,
        [changeId]: {
          ...f,
          stream_codes: f.stream_codes.includes(code)
            ? f.stream_codes.filter((s) => s !== code)
            : [...f.stream_codes, code],
        },
      };
    });
  }

  async function review(change: Change, status: "approved" | "rejected") {
    setBusyId(change.change_id);
    setMsg(null);
    const body: Record<string, unknown> = { status };
    if (change.change_type === "course_added" && status === "approved") {
      const f = forms[change.change_id];
      body.university_id = f?.university_id ? Number(f.university_id) : null;
      body.name_en = f?.name_en?.trim() || null;
      body.stream_codes = f?.stream_codes ?? [];
      // D6 — the rule rides with the approval unless the number already has one
      if (!change.subject_rule_exists && f?.subject_rule?.trim()) {
        const parsed = parseRule(f.subject_rule);
        if (!parsed) {
          setBusyId(null);
          setMsg({
            ok: false,
            text: `${change.course_code}: the subject rule is not valid JSON — fix it before approving.`,
          });
          return;
        }
        body.subject_rule = parsed;
      }
    }
    const res = await fetch(`/api/bff/admin/ingestions/${runId}/changes/${change.change_id}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
    setBusyId(null);
    if (!res.ok) {
      const e = await res.json().catch(() => null);
      // detail is a string for our own gates, but FastAPI's validation errors
      // are a list — never hand a non-string to the renderer.
      setMsg({
        ok: false,
        text: typeof e?.detail === "string" ? e.detail : `Update failed (${res.status}).`,
      });
      return;
    }
    await load();
  }

  // 9.6b — one course of study across several universities is ONE review:
  // shared streams + subject rule (the book documents the course once), each
  // member keeping its own university and name. All members approve together
  // so no university's Uni-Code can be silently forgotten (the promote gate
  // would still catch it, but the admin shouldn't meet that wall at all).
  async function approveGroup(members: Change[]) {
    setMsg(null);
    const lead = members[0];
    const shared = forms[lead.change_id];
    let rule: Record<string, unknown> | null = null;
    if (!lead.subject_rule_exists && shared?.subject_rule?.trim()) {
      rule = parseRule(shared.subject_rule);
      if (!rule) {
        setMsg({
          ok: false,
          text: `${lead.course_code.slice(0, 3)}: the subject rule is not valid JSON — fix it before approving.`,
        });
        return;
      }
    }
    for (const m of members) {
      if (m.status === "applied" || m.status === "rejected") continue;
      const f = forms[m.change_id];
      const body: Record<string, unknown> = {
        status: "approved",
        university_id: f?.university_id ? Number(f.university_id) : null,
        name_en: f?.name_en?.trim() || null,
        stream_codes: shared?.stream_codes ?? [],
      };
      if (rule) body.subject_rule = rule;
      setBusyId(m.change_id);
      const res = await fetch(`/api/bff/admin/ingestions/${runId}/changes/${m.change_id}`, {
        method: "PATCH",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        setBusyId(null);
        const e = await res.json().catch(() => null);
        setMsg({
          ok: false,
          text: `${m.course_code}: ${typeof e?.detail === "string" ? e.detail : `update failed (${res.status})`}`,
        });
        await load();
        return;
      }
    }
    setBusyId(null);
    await load();
  }

  async function apply() {
    if (
      !confirm(
        "Apply all approved changes? Removed courses will be hidden from students. " +
          "New courses will be created and visible to students, with the streams you ticked.",
      )
    )
      return;
    setApplying(true);
    setMsg(null);
    const res = await fetch(`/api/bff/admin/ingestions/${runId}/changes/apply`, { method: "POST" });
    const d = await res.json().catch(() => null);
    setApplying(false);
    if (!res.ok) {
      setMsg({ ok: false, text: d?.detail ?? `Apply failed (${res.status}).` });
      return;
    }
    const skipped = (d.skipped ?? []) as { course_code: string; reason: string }[];
    setMsg({
      ok: true,
      text:
        `Applied: ${d.applied_removed} removed, ${d.applied_added} added.` +
        (skipped.length ? ` Skipped ${skipped.length}: ${skipped.map((s) => `${s.course_code} (${s.reason})`).join(", ")}` : ""),
    });
    await load();
  }

  const approvedApplyable = useMemo(
    () =>
      (data?.items ?? []).filter(
        (c) => c.status === "approved" && (c.change_type === "course_added" || c.change_type === "course_removed"),
      ).length,
    [data],
  );

  if (loading) return <p className="text-sm text-muted-foreground">Loading change-set…</p>;
  if (!data || data.total === 0)
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Handbook changes</CardTitle>
          <CardDescription>No differences from the current data were detected in this handbook.</CardDescription>
        </CardHeader>
      </Card>
    );

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <CardTitle className="text-base">Handbook changes</CardTitle>
            <CardDescription>
              Review what changed vs the live data, then apply. Nothing changes for students until you apply.
            </CardDescription>
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            {(Object.entries(data.counts) as [ChangeStatus, number][]).map(([s, n]) => (
              <span key={s} className={cn("rounded-md px-2 py-0.5 text-xs font-medium capitalize", STATUS_STYLES[s])}>
                {n} {s}
              </span>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {GROUPS.map(({ type, label, icon: Icon, accent }) => {
          const items = data.items.filter((c) => c.change_type === type);
          if (items.length === 0) return null;

          // 9.6b — one course of study across several universities is printed
          // once in the book, so it is reviewed once here: members grouped by
          // course number share streams + subject rule, keep their own
          // university, and approve together.
          const addedGroups: [string, Change[]][] = [];
          if (type === "course_added") {
            const byNum = new Map<string, Change[]>();
            for (const c of items) {
              const key = /^\d{3}/.test(c.course_code) ? c.course_code.slice(0, 3) : c.course_code;
              const arr = byNum.get(key);
              if (arr) arr.push(c);
              else byNum.set(key, [c]);
            }
            byNum.forEach((members, key) => addedGroups.push([key, members]));
          }

          return (
            <div key={type}>
              <div className={cn("mb-2 flex items-center gap-2 text-sm font-semibold", accent)}>
                <Icon className="h-4 w-4" aria-hidden /> {label}
                <span className="text-muted-foreground">({items.length})</span>
              </div>
              <div className="space-y-2">
                {type === "course_added"
                  ? addedGroups.map(([num, members]) => {
                      const lead = members[0];
                      const leadForm =
                        forms[lead.change_id] ??
                        { university_id: "", name_en: "", stream_codes: [], subject_rule: "" };
                      const allApplied = members.every((m) => m.status === "applied");
                      const active = members.filter(
                        (m) => m.status !== "applied" && m.status !== "rejected",
                      );
                      // Phase 9 D1+D6: streams and a subject rule are required
                      // to approve; every active member needs its university+name
                      const needsRule = !lead.subject_rule_exists;
                      const ruleOk = !needsRule || parseRule(leadForm.subject_rule) !== null;
                      const groupReady =
                        leadForm.stream_codes.length > 0 &&
                        ruleOk &&
                        active.length > 0 &&
                        active.every((m) => {
                          const f = forms[m.change_id];
                          return Boolean(f?.university_id && f?.name_en.trim());
                        });
                      const av = lead.after_value ?? {};
                      const bookReq = av.book_requirements_text as string | undefined;
                      const bookIntake = av.book_intake as number | undefined;
                      const detailsPage = av.book_details_page as number | undefined;
                      const mayBeIncomplete = av.streams_may_be_incomplete === true;
                      const bookDuration = av.book_duration_years as number | undefined;
                      const bookMediumText = av.book_medium_text as string | undefined;
                      const mediumNeedsReview = av.book_medium_needs_review === true;
                      const busy = members.some((m) => busyId === m.change_id);
                      return (
                        <div key={num} className="rounded-lg border p-3">
                          <div className="flex flex-wrap items-start justify-between gap-3">
                            <div className="min-w-0 flex-1">
                              <div className="flex flex-wrap items-center gap-2">
                                <span className="font-mono text-xs font-semibold">{num}</span>
                                <span className="text-sm font-medium">
                                  {leadForm.name_en || "New course of study"}
                                </span>
                                {members.length > 1 ? (
                                  <span className="rounded-md bg-muted px-2 py-0.5 text-xs">
                                    one course of study · {members.length} universities — reviewed
                                    together
                                  </span>
                                ) : null}
                              </div>

                              {/* one row per Uni-Code: its own university + name */}
                              <div className="mt-2 space-y-1.5">
                                {members.map((m) => {
                                  const f =
                                    forms[m.change_id] ??
                                    { university_id: "", name_en: "", stream_codes: [], subject_rule: "" };
                                  const rename = m.after_value?.possible_rename_of as
                                    | { course_code: string; name_en?: string; similarity?: number }
                                    | undefined;
                                  const mAptitude = m.after_value?.book_requires_aptitude === true;
                                  const mBookUni = m.after_value?.book_university as string | undefined;
                                  const editable = m.status !== "applied" && m.status !== "rejected";
                                  return (
                                    <div key={m.change_id} className="rounded-md border px-2 py-1.5">
                                      <div className="flex flex-wrap items-center gap-2">
                                        <span className="font-mono text-xs font-semibold">{m.course_code}</span>
                                        <Badge status={m.status} />
                                        {editable ? (
                                          <>
                                            <Select
                                              value={f.university_id}
                                              onValueChange={(v) =>
                                                setForms((p) => ({
                                                  ...p,
                                                  [m.change_id]: { ...f, university_id: v },
                                                }))
                                              }
                                            >
                                              <SelectTrigger className="h-8 w-[140px] text-xs">
                                                <SelectValue placeholder="University…" />
                                              </SelectTrigger>
                                              <SelectContent>
                                                {universities.map((u) => (
                                                  <SelectItem
                                                    key={u.university_id}
                                                    value={String(u.university_id)}
                                                  >
                                                    {u.university_code ?? `#${u.university_id}`}
                                                  </SelectItem>
                                                ))}
                                              </SelectContent>
                                            </Select>
                                            <Input
                                              value={f.name_en}
                                              onChange={(e) =>
                                                setForms((p) => ({
                                                  ...p,
                                                  [m.change_id]: { ...f, name_en: e.target.value },
                                                }))
                                              }
                                              placeholder="Course name"
                                              className="h-8 w-[220px] text-xs"
                                            />
                                          </>
                                        ) : null}
                                        {mAptitude ? (
                                          <span className="text-xs text-muted-foreground">
                                            aptitude test (book)
                                          </span>
                                        ) : null}
                                        {editable && m.status !== "rejected" ? (
                                          <Button
                                            size="sm"
                                            variant="ghost"
                                            className="ml-auto h-7"
                                            disabled={busy}
                                            onClick={() => review(m, "rejected")}
                                          >
                                            <X className="mr-1 h-3 w-3" aria-hidden /> Reject
                                          </Button>
                                        ) : null}
                                      </div>
                                      {mBookUni && !f.university_id && editable ? (
                                        <p className="mt-1 text-xs text-muted-foreground">
                                          the book says “{mBookUni}” — pick the matching university
                                        </p>
                                      ) : null}
                                      {rename ? (
                                        <p className="mt-1 rounded-md border border-amber-300 bg-amber-100 px-2 py-1 text-xs text-amber-900">
                                          ⚠ Possibly a <strong>rename</strong> of {rename.course_code}
                                          {rename.name_en ? ` “${rename.name_en}”` : ""}
                                          {typeof rename.similarity === "number"
                                            ? ` (${Math.round(rename.similarity * 100)}% name match)`
                                            : ""}{" "}
                                          — see the removed-courses list below. If it is, approving
                                          here and letting the old code deactivate is correct; its
                                          history stays under the old code.
                                        </p>
                                      ) : null}
                                    </div>
                                  );
                                })}
                              </div>

                              {!allApplied ? (
                                <div className="mt-2 space-y-2">
                                  <div
                                    className={cn(
                                      "space-y-1.5 rounded-md border p-3",
                                      leadForm.stream_codes.length === 0 && "border-amber-300 bg-amber-50",
                                    )}
                                  >
                                    <div className="text-xs font-medium">
                                      Eligible streams (required
                                      {members.length > 1 ? ", shared by all universities" : ""})
                                      {detailsPage ? (
                                        <span className="ml-1 font-normal text-muted-foreground">
                                          — read from the book, p.{detailsPage}
                                        </span>
                                      ) : null}
                                    </div>
                                    <p className="text-xs text-muted-foreground">
                                      Students only see this course from a ticked stream. No ticks =
                                      invisible to everyone, so it can&apos;t be approved without one.
                                    </p>
                                    {mayBeIncomplete && (
                                      <p className="rounded-md border border-amber-300 bg-amber-100 px-2 py-1.5 text-xs text-amber-900">
                                        ⚠ <strong>These may not be all of them.</strong> The book also
                                        lets students in through a subject list without naming a
                                        stream, so what we could read is a <em>minimum</em>. Read the
                                        book&apos;s wording below and add any stream that qualifies — a
                                        missing tick means those students never see this course.
                                      </p>
                                    )}
                                    <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 pt-1 sm:grid-cols-3">
                                      {streams.map((s) => (
                                        <label key={s.code} className="flex items-center gap-2 text-xs">
                                          <input
                                            type="checkbox"
                                            checked={leadForm.stream_codes.includes(s.code)}
                                            onChange={() => toggleStream(lead.change_id, s.code)}
                                          />
                                          {s.name_en}
                                        </label>
                                      ))}
                                    </div>
                                  </div>

                                  {bookReq && (
                                    <details
                                      className="rounded-md border p-3"
                                      open={mayBeIncomplete || needsRule}
                                    >
                                      <summary className="cursor-pointer text-xs font-medium">
                                        What the book says about this course
                                        {detailsPage ? ` (p.${detailsPage})` : ""}
                                        {bookIntake ? ` · proposed intake ${bookIntake}` : ""}
                                        {bookDuration ? ` · ${bookDuration} years` : ""}
                                        {bookMediumText && !mediumNeedsReview
                                          ? ` · medium: ${bookMediumText}`
                                          : ""}
                                      </summary>
                                      {mediumNeedsReview ? (
                                        <p className="mt-2 rounded-md border border-amber-300 bg-amber-100 px-2 py-1.5 text-xs text-amber-900">
                                          ⚠ <strong>The medium differs per institution</strong> — the
                                          book prints: &ldquo;{bookMediumText}&rdquo;. No medium is set
                                          automatically; assign it per Uni-Code after applying.
                                        </p>
                                      ) : null}
                                      {/* the book's own words, verbatim — the admin
                                          confirms against this, and reviews the
                                          subject rule below against it (D6) */}
                                      <p className="mt-2 whitespace-pre-wrap text-xs leading-relaxed text-muted-foreground">
                                        {bookReq}
                                      </p>
                                    </details>
                                  )}

                                  {/* D6 — the subject rule slot, shared by every
                                      university offering this course of study. */}
                                  {!needsRule ? (
                                    <p className="rounded-md border border-green-300 bg-green-50 px-2 py-1.5 text-xs text-green-900">
                                      ✓ This course number already has a curated subject rule (see{" "}
                                      <span className="font-medium">Subject Rules</span>) — it applies
                                      as-is.
                                    </p>
                                  ) : (
                                    <div
                                      className={cn(
                                        "space-y-1.5 rounded-md border p-3",
                                        !leadForm.subject_rule.trim() && "border-amber-300 bg-amber-50",
                                      )}
                                    >
                                      <div className="text-xs font-medium">
                                        Subject rule (required
                                        {members.length > 1 ? ", shared by all universities" : ""})
                                      </div>
                                      <p className="text-xs text-muted-foreground">
                                        Streams decide who <em>sees</em> this course; this rule decides
                                        who <em>qualifies</em>. Write it from the book&apos;s wording
                                        above — the engine evaluates it on every student&apos;s three
                                        subjects. Subject names must match the catalog exactly (the
                                        server checks).
                                      </p>
                                      {av.suggested_subject_rule ? (
                                        <p className="rounded-md border border-sky-300 bg-sky-50 px-2 py-1.5 text-xs text-sky-900 dark:bg-sky-950/20 dark:text-sky-200">
                                          ✓ Pre-filled by reading the book&apos;s own sentence above —
                                          check it says the same thing, edit if not, then approve.
                                        </p>
                                      ) : null}
                                      <div className="flex flex-wrap gap-1.5">
                                        {RULE_TEMPLATES.map((t) => (
                                          <button
                                            key={t.label}
                                            type="button"
                                            className="rounded-md border px-2 py-0.5 text-[11px] hover:bg-accent"
                                            onClick={() =>
                                              setForms((p) => ({
                                                ...p,
                                                [lead.change_id]: { ...leadForm, subject_rule: t.json },
                                              }))
                                            }
                                          >
                                            {t.label}
                                          </button>
                                        ))}
                                      </div>
                                      <textarea
                                        value={leadForm.subject_rule}
                                        onChange={(e) =>
                                          setForms((p) => ({
                                            ...p,
                                            [lead.change_id]: {
                                              ...leadForm,
                                              subject_rule: e.target.value,
                                            },
                                          }))
                                        }
                                        rows={5}
                                        spellCheck={false}
                                        placeholder='e.g. {"type": "count_from_list", "subjects": ["Biology", "Chemistry", "Physics"], "count": 3, "min_grade": "S"}'
                                        className="w-full rounded-md border bg-background p-2 font-mono text-[11px] leading-relaxed"
                                      />
                                      {leadForm.subject_rule.trim() && !ruleOk ? (
                                        <p className="text-xs text-destructive">Not valid JSON yet.</p>
                                      ) : null}
                                    </div>
                                  )}
                                </div>
                              ) : null}
                            </div>

                            {!allApplied && active.length > 0 ? (
                              <div className="flex shrink-0 items-center gap-1.5">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  disabled={busy || !groupReady}
                                  onClick={() => approveGroup(members)}
                                  title={
                                    !groupReady
                                      ? "Every university needs a name picked, plus shared streams and a subject rule"
                                      : undefined
                                  }
                                >
                                  <Check className="mr-1 h-3.5 w-3.5" aria-hidden />
                                  {members.length > 1
                                    ? `Approve all ${members.length}`
                                    : "Approve"}
                                </Button>
                              </div>
                            ) : null}
                          </div>
                        </div>
                      );
                    })
                  : items.map((c) => {
                      const isCutoff = c.change_type === "cutoff_changed";
                      const actionable =
                        c.status === "pending" || c.status === "approved" || c.status === "rejected";
                      const details = (c.after_value?.details as CutoffDelta[] | undefined) ?? [];
                      const renameTo = c.after_value?.possible_rename_to as
                        | { course_code: string; name_en?: string; similarity?: number }[]
                        | undefined;
                      return (
                        <div key={c.change_id} className="rounded-lg border p-3">
                          <div className="flex flex-wrap items-start justify-between gap-3">
                            <div className="min-w-0 flex-1">
                              <div className="flex items-center gap-2">
                                <span className="font-mono text-xs font-semibold">{c.course_code}</span>
                                <Badge status={c.status} />
                              </div>
                              <p className="mt-0.5 text-sm text-muted-foreground">{c.summary}</p>

                              {renameTo && renameTo.length > 0 ? (
                                <p className="mt-1 rounded-md border border-amber-300 bg-amber-100 px-2 py-1.5 text-xs text-amber-900">
                                  ⚠ Possibly <strong>renamed</strong> to{" "}
                                  {renameTo
                                    .map(
                                      (r) =>
                                        `${r.course_code}${r.name_en ? ` “${r.name_en}”` : ""}${
                                          typeof r.similarity === "number"
                                            ? ` (${Math.round(r.similarity * 100)}%)`
                                            : ""
                                        }`,
                                    )
                                    .join(", ")}{" "}
                                  in the new-courses list above. If so, approve both sides: the new
                                  code takes over, this one deactivates but keeps its history.
                                </p>
                              ) : null}

                              {isCutoff && details.length > 0 && (
                                <button
                                  type="button"
                                  onClick={() =>
                                    setOpen((o) => ({ ...o, [c.change_id]: !o[c.change_id] }))
                                  }
                                  className="mt-1 inline-flex items-center gap-1 text-xs text-primary"
                                >
                                  <ChevronDown
                                    className={cn(
                                      "h-3 w-3 transition-transform",
                                      open[c.change_id] && "rotate-180",
                                    )}
                                    aria-hidden
                                  />
                                  {open[c.change_id] ? "Hide" : "Show"} {details.length} district changes
                                </button>
                              )}
                              {isCutoff && open[c.change_id] && (
                                <div className="mt-2 grid grid-cols-2 gap-x-6 gap-y-0.5 text-xs sm:grid-cols-3">
                                  {details.map((d) => (
                                    <div key={d.district} className="flex justify-between gap-2">
                                      <span className="text-muted-foreground">{d.district}</span>
                                      <span className="font-mono">
                                        {d.old ?? "—"} → {d.new ?? "—"}
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>

                            {actionable && c.status !== "applied" && (
                              <div className="flex shrink-0 items-center gap-1.5">
                                {c.status !== "approved" && (
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    disabled={busyId === c.change_id}
                                    onClick={() => review(c, "approved")}
                                  >
                                    <Check className="mr-1 h-3.5 w-3.5" aria-hidden /> Approve
                                  </Button>
                                )}
                                {c.status !== "rejected" && (
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    disabled={busyId === c.change_id}
                                    onClick={() => review(c, "rejected")}
                                  >
                                    <X className="mr-1 h-3.5 w-3.5" aria-hidden /> Reject
                                  </Button>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
              </div>
            </div>
          );
        })}

        <div className="flex flex-wrap items-center gap-3 border-t pt-4">
          <Button onClick={apply} disabled={applying || approvedApplyable === 0}>
            {applying ? "Applying…" : `Apply ${approvedApplyable} approved change${approvedApplyable === 1 ? "" : "s"}`}
          </Button>
          <span className="text-xs text-muted-foreground">
            Removed → hidden from students (kept for the AI). Added → created live and visible to
            students with the streams you ticked. Promote is blocked until every new course is done.
          </span>
        </div>
        {msg && <p className={cn("text-sm", msg.ok ? "text-green-700" : "text-destructive")}>{msg.text}</p>}
      </CardContent>
    </Card>
  );
}
