"use client";

import { useEffect, useRef, useState } from "react";
import { useSession, signIn, signOut } from "next-auth/react";

interface Message {
  role: "user" | "assistant";
  content: string;
  tools?: string[];
}

interface EligibleCourse {
  course_code: string;
  course_name: string;
  university: string;
  cutoff: number;
  margin: number;
  bucket: "safe" | "ambitious" | "consider";
}

interface ChatContext {
  z_score?: number;
  district_code?: string;
  stream_code?: string;
  /** Exam year whose cutoffs the student is currently viewing (Phase 2 §1.3). */
  exam_year?: number;
  subjects?: Array<{ subject: string; grade: string }>;
  interests?: string;
  eligible_courses?: EligibleCourse[];
}

interface ChatPanelProps {
  context?: ChatContext;
  /** When true: renders as a full-height inline view instead of a floating overlay. */
  inline?: boolean;
  /** Called when the user clicks "New Chat" in inline mode. */
  onNewChat?: () => void;
}

interface ConversationSummary {
  conversation_id: string;
  preview: string;
  updated_at: string;
  message_count: number;
}

const WELCOME: Message = {
  role: "assistant",
  content:
    "Hi! I'm your AI degree guide. I can answer questions about specific courses, Z-score cutoffs, career paths, and universities. What would you like to know?",
};

function getSessionId(): string {
  const key = "dg_session_id";
  let id = localStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(key, id);
  }
  return id;
}

export function ChatPanel({ context, inline = false, onNewChat }: ChatPanelProps) {
  const { data: session } = useSession();
  const isStudent = session?.user?.role === "student";

  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([WELCOME]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [webSearch, setWebSearch] = useState(false);

  // History panel state
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<ConversationSummary[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (open) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
      inputRef.current?.focus();
    }
  }, [open, messages]);

  useEffect(() => {
    if (!open) return;
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [open]);

  async function fetchHistory() {
    if (!isStudent) return;
    setHistoryLoading(true);
    try {
      const res = await fetch("/api/student/conversations");
      if (res.ok) setHistory(await res.json());
    } catch {
      // silently ignore
    } finally {
      setHistoryLoading(false);
    }
  }

  function toggleHistory() {
    if (!showHistory && history.length === 0) fetchHistory();
    setShowHistory((v) => !v);
  }

  async function resumeConversation(cid: string) {
    setShowHistory(false);
    setLoading(true);
    try {
      const res = await fetch(`/api/student/conversations/${cid}`);
      if (res.ok) {
        const msgs: Array<{ role: string; content: string }> = await res.json();
        setMessages([
          WELCOME,
          ...msgs.map((m) => ({ role: m.role as "user" | "assistant", content: m.content })),
        ]);
        setConversationId(cid);
      }
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }

  async function send() {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/public/chat", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          session_id: getSessionId(),
          conversation_id: conversationId,
          student_id: isStudent ? session?.user?.id ?? null : null,
          message: text,
          context: context ?? null,
          web_search: webSearch,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(
          typeof body?.detail === "string" ? body.detail : `Error ${res.status}`
        );
      }

      const data = await res.json();
      if (data.conversation_id) setConversationId(data.conversation_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply, tools: data.tools_used },
      ]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
      setMessages((prev) => prev.slice(0, -1));
      setInput(text);
    } finally {
      setLoading(false);
    }
  }

  function handleKey(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  function handleNewChat() {
    setMessages([WELCOME]);
    setConversationId(null);
    setError(null);
    setShowHistory(false);
    setHistory([]);
    onNewChat?.();
  }

  // ── History panel ─────────────────────────────────────────────────────────

  const historyPanel = showHistory && isStudent && (
    <div style={{ borderBottom: "1px solid var(--dg-border)", background: "var(--dg-surface2)" }}>
      <div className="px-4 py-3">
        <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide" style={{ color: "var(--dg-muted)" }}>
          Previous chats
        </p>
        {historyLoading && (
          <p className="text-[13px]" style={{ color: "var(--dg-muted)" }}>Loading…</p>
        )}
        {!historyLoading && history.length === 0 && (
          <p className="text-[13px]" style={{ color: "var(--dg-muted)" }}>No previous chats yet.</p>
        )}
        {!historyLoading && history.map((h) => (
          <button
            key={h.conversation_id}
            onClick={() => resumeConversation(h.conversation_id)}
            className="mb-1 w-full rounded-[10px] px-3 py-2 text-left text-[13px] transition-colors hover:brightness-95"
            style={{ color: "var(--dg-ink)", background: "var(--dg-surface)" }}
          >
            <span className="line-clamp-1">{h.preview}</span>
            <span className="mt-[2px] block text-[11px]" style={{ color: "var(--dg-muted)" }}>
              {h.message_count} messages · {new Date(h.updated_at).toLocaleDateString()}
            </span>
          </button>
        ))}
      </div>
    </div>
  );

  // ── Shared sub-components ─────────────────────────────────────────────────

  const headerBtn =
    "flex items-center gap-[5px] rounded-lg px-3 py-[6px] text-[12px] font-semibold transition-colors";
  const headerBtnStyle: React.CSSProperties = {
    background: "var(--dg-surface2)",
    color: "var(--dg-ink)",
    border: "1px solid var(--dg-border)",
  };

  const chatHeader = (
    <div
      className="flex items-center gap-3 px-5 py-4"
      style={{ background: "var(--dg-surface)", borderBottom: "1px solid var(--dg-border)" }}
    >
      <div
        className="flex h-9 w-9 items-center justify-center rounded-full"
        style={{ background: "var(--dg-accent)", color: "var(--dg-accent-ink)" }}
      >
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 8V4H8" />
          <rect x="4" y="8" width="16" height="12" rx="2" />
          <path d="M2 14h2M20 14h2M15 13v2M9 13v2" />
        </svg>
      </div>
      <div className="flex-1">
        <div className="text-[14px] font-bold" style={{ color: "var(--dg-ink)" }}>Degree Guide AI</div>
        {isStudent
          ? <div className="text-[11px]" style={{ color: "var(--dg-muted)" }}>{session?.user?.name ?? session?.user?.email}</div>
          : <div className="text-[11px]" style={{ color: "var(--dg-muted)" }}>Powered by Gemini</div>
        }
      </div>
      <div className="flex items-center gap-2">
        {isStudent && inline && (
          <button onClick={toggleHistory} title="Chat history" className={headerBtn} style={headerBtnStyle}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 7v5l3 3" />
            </svg>
            History
          </button>
        )}
        {!isStudent ? (
          <button onClick={() => signIn("google", { callbackUrl: "/" })} className={headerBtn} style={headerBtnStyle}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            Sign in
          </button>
        ) : (
          <button onClick={() => signOut({ callbackUrl: "/" })} title="Sign out" className={headerBtn} style={headerBtnStyle}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" />
            </svg>
          </button>
        )}
        {inline && (
          <button
            onClick={handleNewChat}
            className="flex items-center gap-[6px] rounded-lg px-3 py-[6px] text-[12px] font-semibold transition-colors"
            style={{ background: "var(--dg-accent)", color: "var(--dg-accent-ink)" }}
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
              <path d="M12 5v14M5 12h14" />
            </svg>
            New Chat
          </button>
        )}
      </div>
    </div>
  );

  const messageList = (
    <div className="flex-1 overflow-y-auto px-4 py-4" style={{ gap: 12, display: "flex", flexDirection: "column" }}>
      {messages.map((msg, i) => (
        <div key={i} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
          <div
            className="max-w-[85%] rounded-[16px] px-4 py-[10px] text-[14px] leading-[1.55]"
            style={
              msg.role === "user"
                ? { background: "var(--dg-accent)", color: "var(--dg-accent-ink)", borderBottomRightRadius: 4 }
                : { background: "var(--dg-surface2)", color: "var(--dg-ink)", borderBottomLeftRadius: 4 }
            }
          >
            <MessageContent content={msg.content} />
          </div>
          {msg.tools && msg.tools.length > 0 && (
            <div className="mt-1 flex flex-wrap gap-1">
              {msg.tools.map((t) => (
                <span key={t} className="rounded-full px-2 py-[2px] text-[10px] font-semibold" style={{ background: "var(--dg-accent-soft)", color: "var(--dg-accent)" }}>
                  {t.replace(/_/g, " ")}
                </span>
              ))}
            </div>
          )}
        </div>
      ))}
      {loading && (
        <div className="flex items-start">
          <div className="rounded-[16px] px-4 py-[10px]" style={{ background: "var(--dg-surface2)", borderBottomLeftRadius: 4 }}>
            <Dots />
          </div>
        </div>
      )}
      {error && <p className="text-center text-[12px]" style={{ color: "var(--dg-amb-fg)" }}>{error}</p>}
      <div ref={bottomRef} />
    </div>
  );

  const inputBar = (
    <div style={{ borderTop: "1px solid var(--dg-border)" }} className="px-4 py-3">
      <div
        className="flex items-end gap-2 rounded-[14px] px-3 py-2"
        style={{ border: "1.5px solid var(--dg-border)", background: "var(--dg-surface2)" }}
      >
        <button
          type="button"
          onClick={() => setWebSearch((v) => !v)}
          title={webSearch ? "Web search on" : "Web search off"}
          className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full transition-colors"
          style={{ background: webSearch ? "var(--dg-accent)" : "var(--dg-track)", color: webSearch ? "var(--dg-accent-ink)" : "var(--dg-muted)" }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 2C12 2 8 7 8 12s4 10 4 10M12 2c0 0 4 5 4 10s-4 10-4 10M2 12h20" />
          </svg>
        </button>
        <textarea
          ref={inputRef}
          rows={1}
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            e.target.style.height = "auto";
            e.target.style.height = Math.min(e.target.scrollHeight, 96) + "px";
          }}
          onKeyDown={handleKey}
          placeholder="Ask about any degree, cutoff, or career…"
          disabled={loading}
          className="flex-1 resize-none bg-transparent text-[14px] leading-[1.5] outline-none disabled:opacity-50"
          style={{ maxHeight: 96, minHeight: 22, color: "var(--dg-ink)" }}
        />
        <button
          onClick={send}
          disabled={!input.trim() || loading}
          className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full transition-colors disabled:opacity-40"
          style={{ background: input.trim() && !loading ? "var(--dg-accent)" : "var(--dg-border)", color: "var(--dg-accent-ink)" }}
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 2L11 13M22 2L15 22 11 13 2 9l20-7z" />
          </svg>
        </button>
      </div>
      <p className="mt-[6px] text-center text-[11px]" style={{ color: "var(--dg-muted)" }}>
        {isStudent
          ? "Your chats are saved to your account."
          : <>Sign in to save history. · AI can make mistakes — verify at ugc.ac.lk.</>
        }
      </p>
    </div>
  );

  // ── Inline mode (full-height tab) ─────────────────────────────────────────

  if (inline) {
    return (
      <div className="mx-auto mt-4 flex w-full max-w-[820px] flex-col overflow-hidden rounded-[18px]" style={{ minHeight: "calc(100vh - 200px)", border: "1px solid var(--dg-border)", background: "var(--dg-surface)", boxShadow: "var(--dg-shadow)" }}>
        {chatHeader}
        {historyPanel}
        {messageList}
        {inputBar}
      </div>
    );
  }

  // ── Floating mode (original behaviour, unchanged) ─────────────────────────

  return (
    <>
      <button
        onClick={() => setOpen((o) => !o)}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full transition-transform hover:scale-105"
        style={{ background: "var(--dg-accent)", color: "var(--dg-accent-ink)", boxShadow: "var(--dg-shadow)" }}
        aria-label="Ask AI degree guide"
      >
        {open ? (
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
          </svg>
        )}
      </button>

      {open && (
        <div
          className="fixed bottom-24 right-6 z-50 flex w-[380px] max-w-[calc(100vw-24px)] flex-col overflow-hidden rounded-[22px]"
          style={{ height: "520px", border: "1px solid var(--dg-border)", background: "var(--dg-surface)", boxShadow: "0 16px 48px rgba(22,36,59,.18)" }}
        >
          {chatHeader}
          {messageList}
          {inputBar}
        </div>
      )}
    </>
  );
}

/** Render markdown-style bold (**text**) and newlines cleanly */
function MessageContent({ content }: { content: string }) {
  const parts = content.split(/(\*\*[^*]+\*\*)/g);
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return <strong key={i}>{part.slice(2, -2)}</strong>;
        }
        return (
          <span key={i}>
            {part.split("\n").map((line, j, arr) => (
              <span key={j}>
                {line}
                {j < arr.length - 1 && <br />}
              </span>
            ))}
          </span>
        );
      })}
    </>
  );
}

function Dots() {
  return (
    <div className="flex gap-[5px] py-[2px]">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="block h-[7px] w-[7px] rounded-full"
          style={{
            background: "var(--dg-muted)",
            animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite`,
          }}
        />
      ))}
      <style>{`@keyframes bounce { 0%,80%,100%{transform:translateY(0)} 40%{transform:translateY(-6px)} }`}</style>
    </div>
  );
}
