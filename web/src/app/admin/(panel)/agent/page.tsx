"use client";

import { useCallback, useEffect, useState } from "react";
import { Bot, Check, FlaskConical, RotateCcw, Save } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

type Config = {
  config_id: number;
  name: string;
  system_prompt_template: string;
  model_name: string;
  web_search_default: boolean;
  max_tool_turns: number;
  notes: string | null;
  is_active: boolean;
  created_at: string;
};
type ListResponse = { active_source: string; items: Config[] };
type DefaultResponse = {
  system_prompt_template: string;
  model_name: string;
  web_search_default: boolean;
  max_tool_turns: number;
  live_facts: Record<string, string>;
  placeholders: string[];
};

export default function AgentPage() {
  const [list, setList] = useState<ListResponse | null>(null);
  const [defaults, setDefaults] = useState<DefaultResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  // editor state
  const [name, setName] = useState("");
  const [template, setTemplate] = useState("");
  const [model, setModel] = useState("");
  const [webSearch, setWebSearch] = useState(true);
  const [maxTurns, setMaxTurns] = useState(6);
  const [activate, setActivate] = useState(true);
  const [saving, setSaving] = useState(false);
  const [busyId, setBusyId] = useState<number | null>(null);

  // sandbox
  const [testMsg, setTestMsg] = useState("What is the cutoff for medicine at Colombo?");
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ reply: string; tools_used: string[] } | null>(null);

  const load = useCallback(async () => {
    const [l, d] = await Promise.all([
      fetch("/api/bff/admin/agent-configs", { cache: "no-store" }),
      fetch("/api/bff/admin/agent-configs/default", { cache: "no-store" }),
    ]);
    if (l.ok) setList(await l.json());
    else setErr(`Failed to load configs (HTTP ${l.status})`);
    if (d.ok) {
      const dd: DefaultResponse = await d.json();
      setDefaults(dd);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  // Pre-fill the editor once data arrives: active config if any, else built-in.
  useEffect(() => {
    if (!list || !defaults || template) return;
    const active = list.items.find((c) => c.is_active);
    if (active) {
      setName(`${active.name} (edited)`);
      setTemplate(active.system_prompt_template);
      setModel(active.model_name);
      setWebSearch(active.web_search_default);
      setMaxTurns(active.max_tool_turns);
    } else {
      setName("Custom v1");
      setTemplate(defaults.system_prompt_template);
      setModel(defaults.model_name);
      setWebSearch(defaults.web_search_default);
      setMaxTurns(defaults.max_tool_turns);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [list, defaults]);

  async function save() {
    setSaving(true);
    setMsg(null);
    const res = await fetch("/api/bff/admin/agent-configs", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        name: name.trim(),
        system_prompt_template: template,
        model_name: model.trim(),
        web_search_default: webSearch,
        max_tool_turns: maxTurns,
        activate,
      }),
    });
    const d = await res.json().catch(() => null);
    setSaving(false);
    if (!res.ok) {
      setMsg({ ok: false, text: d?.detail ?? `Save failed (${res.status}).` });
      return;
    }
    setMsg({
      ok: true,
      text: `Saved v${d.config_id}${activate ? " and activated — live for the next student message." : "."}`,
    });
    await load();
  }

  async function activateVersion(id: number) {
    setBusyId(id);
    setMsg(null);
    const res = await fetch(`/api/bff/admin/agent-configs/${id}/activate`, { method: "POST" });
    setBusyId(null);
    if (res.ok) {
      setMsg({ ok: true, text: `Version ${id} is now active.` });
      await load();
    }
  }

  async function revertToBuiltin() {
    if (!confirm("Revert the agent to the built-in default prompt and model?")) return;
    const res = await fetch("/api/bff/admin/agent-configs/deactivate", { method: "POST" });
    if (res.ok) {
      setMsg({ ok: true, text: "Agent reverted to the built-in default." });
      await load();
    }
  }

  async function runTest() {
    setTesting(true);
    setTestResult(null);
    setMsg(null);
    const res = await fetch("/api/bff/admin/agent-configs/test", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        message: testMsg,
        system_prompt_template: template || null,
        model_name: model || null,
        max_tool_turns: maxTurns,
        web_search: false,
      }),
    });
    const d = await res.json().catch(() => null);
    setTesting(false);
    if (!res.ok) {
      setMsg({ ok: false, text: d?.detail ?? `Test failed (${res.status}).` });
      return;
    }
    setTestResult(d);
  }

  const activeSource = list?.active_source ?? "…";

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-medium">
            <Bot className="h-6 w-6" aria-hidden /> AI Advisor
          </h1>
          <p className="text-sm text-muted-foreground">
            The agent&apos;s prompt, model and limits — versioned, testable, instantly
            revertible. Live facts ({defaults?.placeholders.join(", ")}) are injected at
            runtime, so the prompt never goes stale when you promote a new handbook year.
          </p>
        </div>
        <span
          className={cn(
            "rounded-md px-2 py-1 text-xs font-medium",
            activeSource === "builtin" ? "bg-zinc-100 text-zinc-700" : "bg-green-100 text-green-800",
          )}
        >
          active: {activeSource === "builtin" ? "built-in default" : `custom ${activeSource}`}
        </span>
      </div>

      {defaults ? (
        <p className="rounded-md bg-muted/60 px-3 py-2 text-xs text-muted-foreground">
          Current live facts: years = {defaults.live_facts.available_years} · latest ={" "}
          {defaults.live_facts.latest_year} · active courses = {defaults.live_facts.course_count}
        </p>
      ) : null}
      {err ? <p className="text-sm text-destructive">{err}</p> : null}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Edit prompt & behavior</CardTitle>
          <CardDescription>
            Saving creates a new version (history below is your rollback path). Use the
            placeholders instead of typing years or counts — they fill themselves.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap gap-3">
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Version name"
              className="max-w-56"
            />
            <Input
              value={model}
              onChange={(e) => setModel(e.target.value)}
              placeholder="Model name"
              className="max-w-72 font-mono text-xs"
            />
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={webSearch}
                onChange={(e) => setWebSearch(e.target.checked)}
              />
              Web search on by default
            </label>
            <label className="flex items-center gap-2 text-sm">
              Max tool turns
              <Input
                type="number"
                min={1}
                max={12}
                value={maxTurns}
                onChange={(e) => setMaxTurns(Number(e.target.value))}
                className="w-20"
              />
            </label>
          </div>
          <textarea
            value={template}
            onChange={(e) => setTemplate(e.target.value)}
            rows={18}
            spellCheck={false}
            className="w-full rounded-md border bg-background p-3 font-mono text-xs leading-relaxed"
          />
          <div className="flex flex-wrap items-center gap-3">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={activate}
                onChange={(e) => setActivate(e.target.checked)}
              />
              Activate immediately
            </label>
            <Button size="sm" onClick={save} disabled={saving || !template.trim() || !name.trim()}>
              <Save className="mr-1 h-4 w-4" aria-hidden />
              {saving ? "Saving…" : "Save as new version"}
            </Button>
            <Button size="sm" variant="outline" onClick={revertToBuiltin}>
              <RotateCcw className="mr-1 h-4 w-4" aria-hidden /> Revert to built-in
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Test before you trust</CardTitle>
          <CardDescription>
            Runs the real agent loop with the prompt in the editor above (web search off,
            nothing saved). This makes a real Gemini call.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex flex-wrap gap-2">
            <Input
              value={testMsg}
              onChange={(e) => setTestMsg(e.target.value)}
              className="min-w-72 flex-1"
              placeholder="Ask as a student would…"
            />
            <Button size="sm" variant="outline" onClick={runTest} disabled={testing || !testMsg.trim()}>
              <FlaskConical className="mr-1 h-4 w-4" aria-hidden />
              {testing ? "Running…" : "Run test"}
            </Button>
          </div>
          {testResult ? (
            <div className="rounded-md border bg-muted/40 p-3">
              <div className="mb-2 flex flex-wrap gap-1.5">
                {testResult.tools_used.map((t, i) => (
                  <span key={i} className="rounded-md bg-purple-100 px-1.5 py-0.5 text-[10px] font-medium text-purple-800">
                    {t}
                  </span>
                ))}
              </div>
              <p className="whitespace-pre-wrap text-sm">{testResult.reply}</p>
            </div>
          ) : null}
        </CardContent>
      </Card>

      {msg ? (
        <p className={cn("text-sm", msg.ok ? "text-green-700" : "text-destructive")}>{msg.text}</p>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Version history</CardTitle>
          <CardDescription>Activate any previous version to roll back instantly.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          {list?.items.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No saved versions yet — the built-in default is running.
            </p>
          ) : (
            list?.items.map((c) => (
              <div
                key={c.config_id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-lg border px-3 py-2"
              >
                <div className="min-w-0">
                  <span className="text-sm font-medium">
                    v{c.config_id} — {c.name}
                  </span>
                  {c.is_active ? (
                    <span className="ml-2 rounded-md bg-green-100 px-1.5 py-0.5 text-[10px] font-medium text-green-800">
                      active
                    </span>
                  ) : null}
                  <p className="text-xs text-muted-foreground">
                    {c.model_name} · {c.max_tool_turns} turns · web search{" "}
                    {c.web_search_default ? "on" : "off"} ·{" "}
                    {new Date(c.created_at).toLocaleString()}
                  </p>
                </div>
                {!c.is_active ? (
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={busyId === c.config_id}
                    onClick={() => activateVersion(c.config_id)}
                  >
                    <Check className="mr-1 h-3.5 w-3.5" aria-hidden /> Activate
                  </Button>
                ) : null}
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
