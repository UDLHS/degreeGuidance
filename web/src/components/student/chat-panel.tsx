"use client";

import { useEffect, useRef, useState } from "react";

const ACCENT = "#2b5fd0";

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
  subjects?: Array<{ subject: string; grade: string }>;
  interests?: string;
  eligible_courses?: EligibleCourse[];
}

interface ChatPanelProps {
  context?: ChatContext;
}

function getSessionId(): string {
  const key = "dg_session_id";
  let id = localStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(key, id);
  }
  return id;
}

export function ChatPanel({ context }: ChatPanelProps) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm your AI degree guide. I can answer questions about specific courses, Z-score cutoffs, career paths, and universities. What would you like to know?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (open) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
      inputRef.current?.focus();
    }
  }, [open, messages]);

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
          message: text,
          context: context ?? null,
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
      // Remove the optimistic user message on error
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

  return (
    <>
      {/* Floating trigger button */}
      <button
        onClick={() => setOpen((o) => !o)}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full shadow-[0_6px_24px_rgba(43,95,208,.35)] transition-transform hover:scale-105"
        style={{ background: ACCENT }}
        aria-label="Ask AI degree guide"
      >
        {open ? (
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path d="M18 6L6 18M6 6l12 12" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" />
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path
              d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"
              stroke="#fff"
              strokeWidth="1.9"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </button>

      {/* Chat panel */}
      {open && (
        <div
          className="fixed bottom-24 right-6 z-50 flex w-[380px] max-w-[calc(100vw-24px)] flex-col overflow-hidden rounded-[22px] shadow-[0_16px_48px_rgba(22,36,59,.18)]"
          style={{ height: "520px", border: "1.5px solid #e3e9f2", background: "#fff" }}
        >
          {/* Header */}
          <div
            className="flex items-center gap-3 px-5 py-4"
            style={{ background: ACCENT }}
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/20">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L3 7l9 5 9-5-9-5z" fill="#fff" />
                <path d="M3 12l9 5 9-5M3 17l9 5 9-5" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <div>
              <div className="text-[14px] font-bold text-white">Degree Guide AI</div>
              <div className="text-[11px] text-white/70">Powered by Gemini</div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-4" style={{ gap: 12, display: "flex", flexDirection: "column" }}>
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
              >
                <div
                  className="max-w-[85%] rounded-[16px] px-4 py-[10px] text-[14px] leading-[1.55]"
                  style={
                    msg.role === "user"
                      ? { background: ACCENT, color: "#fff", borderBottomRightRadius: 4 }
                      : { background: "#f4f6fb", color: "#16243b", borderBottomLeftRadius: 4 }
                  }
                >
                  <MessageContent content={msg.content} />
                </div>
                {msg.tools && msg.tools.length > 0 && (
                  <div className="mt-1 flex gap-1 flex-wrap">
                    {msg.tools.map((t) => (
                      <span
                        key={t}
                        className="rounded-full px-2 py-[2px] text-[10px] font-semibold"
                        style={{ background: "#e8eef8", color: "#4a6fa5" }}
                      >
                        {t.replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex items-start">
                <div
                  className="rounded-[16px] px-4 py-[10px]"
                  style={{ background: "#f4f6fb", borderBottomLeftRadius: 4 }}
                >
                  <Dots />
                </div>
              </div>
            )}
            {error && (
              <p className="text-center text-[12px] text-[#b4485f]">{error}</p>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-[#e9eef6] px-4 py-3">
            <div className="flex items-end gap-2 rounded-[14px] border-[1.5px] border-[#e3e9f2] bg-[#f9fafc] px-3 py-2">
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
                className="flex-1 resize-none bg-transparent text-[14px] leading-[1.5] text-[#16243b] outline-none placeholder:text-[#9aa7be] disabled:opacity-50"
                style={{ maxHeight: 96, minHeight: 22 }}
              />
              <button
                onClick={send}
                disabled={!input.trim() || loading}
                className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full transition-colors disabled:opacity-40"
                style={{ background: input.trim() && !loading ? ACCENT : "#cdd6e8" }}
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
                  <path d="M22 2L11 13M22 2L15 22 11 13 2 9l20-7z" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            </div>
            <p className="mt-[6px] text-center text-[11px] text-[#b0baca]">
              AI can make mistakes. Verify cutoffs at ugc.ac.lk.
            </p>
          </div>
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
            background: "#9aa7be",
            animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite`,
          }}
        />
      ))}
      <style>{`@keyframes bounce { 0%,80%,100%{transform:translateY(0)} 40%{transform:translateY(-6px)} }`}</style>
    </div>
  );
}
