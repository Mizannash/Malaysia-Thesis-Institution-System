"use client";

import { useEffect, useRef, useState } from "react";
import { Send, Search } from "lucide-react";
import { useLanguage } from "@/lib/LanguageContext";
import { TranslationKey } from "@/lib/translations";
import { CoachMessage, getApiErrorMessage, getCoachHistory, sendCoachMessage } from "@/lib/api";

export interface CoachAutoSend {
  id: number;
  text: string;
}

interface CoachChatProps {
  projectId: string | null;
  stage: string;
  active?: boolean;
  autoSend?: CoachAutoSend | null;
  isSearching?: boolean;
  onSearchTopic?: (query: string) => void;
  onSendingChange?: (sending: boolean) => void;
}

export const STAGE_SUGGESTION: Record<string, TranslationKey> = {
  search: "coach_suggest_search",
  gap: "coach_suggest_gap",
  title: "coach_suggest_title",
  "deep-dive": "coach_suggest_deepdive",
  deepdive: "coach_suggest_deepdive",
  plan: "coach_suggest_plan",
};

export default function CoachChat({ projectId, stage, active = true, autoSend, isSearching = false, onSearchTopic, onSendingChange }: CoachChatProps) {
  const { t, lang } = useLanguage();
  const [history, setHistory] = useState<CoachMessage[]>([]);
  const [remaining, setRemaining] = useState<number | null>(null);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const lastAutoSendId = useRef<number | null>(null);

  useEffect(() => {
    setHistory([]);
    setRemaining(null);
    setError(null);
    if (!projectId) return;
    let cancelled = false;
    getCoachHistory(projectId)
      .then((data) => {
        if (cancelled) return;
        setHistory(data.history || []);
        setRemaining(data.chat_remaining);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [projectId]);

  useEffect(() => {
    if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [history, sending, active]);

  useEffect(() => {
    if (active) inputRef.current?.focus();
  }, [active]);

  useEffect(() => {
    onSendingChange?.(sending);
  }, [sending, onSendingChange]);

  const send = async (text: string) => {
    const message = text.trim();
    if (!message || !projectId || sending) return;
    setError(null);
    setSending(true);
    setInput("");
    setHistory((prev) => [...prev, { role: "user", content: message }]);
    try {
      const data = await sendCoachMessage(projectId, message, lang);
      setHistory(data.history);
      setRemaining(data.chat_remaining);
    } catch (err) {
      setHistory((prev) => prev.slice(0, -1));
      setInput(message);
      setError(getApiErrorMessage(err, t("coach_error")));
    } finally {
      setSending(false);
    }
  };

  useEffect(() => {
    if (!autoSend || autoSend.id === lastAutoSendId.current) return;
    lastAutoSendId.current = autoSend.id;
    send(autoSend.text);
  }, [autoSend]);

  const suggestions: TranslationKey[] = [STAGE_SUGGESTION[stage] || "coach_suggest_search", "coach_suggest_viva"];

  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, minHeight: 0 }}>
      <div
        ref={listRef}
        style={{
          flex: 1,
          minHeight: 0,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          gap: "0.5rem",
          marginBottom: "0.6rem",
        }}
      >
        {history.length === 0 && !sending && (
          <p style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", margin: 0 }}>{t("coach_empty")}</p>
        )}
        {history.map((m, i) => (
          <div
            key={i}
            style={{
              alignSelf: m.role === "user" ? "flex-end" : "flex-start",
              maxWidth: "88%",
              background: m.role === "user" ? "var(--primary)" : "var(--surface-low)",
              color: m.role === "user" ? "var(--on-primary)" : "var(--on-surface)",
              border: m.role === "user" ? "none" : "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-md)",
              padding: "0.5rem 0.7rem",
              fontSize: "0.82rem",
              lineHeight: 1.5,
              whiteSpace: "pre-wrap",
              overflowWrap: "anywhere",
            }}
          >
            {m.content}
          </div>
        ))}
        {sending && (
          <div style={{ alignSelf: "flex-start", fontSize: "0.78rem", fontStyle: "italic", color: "var(--on-surface-variant)" }}>
            {t("coach_thinking")}
          </div>
        )}
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", marginBottom: "0.5rem" }}>
        {suggestions.map((key) => (
          <button
            key={key}
            type="button"
            disabled={!projectId || sending}
            onClick={() => send(t(key))}
            className="btn-secondary"
            style={{ fontSize: "0.72rem", padding: "0.25rem 0.55rem" }}
          >
            {t(key)}
          </button>
        ))}
      </div>

      {error && (
        <p style={{ fontSize: "0.76rem", color: "var(--error)", margin: "0 0 0.4rem" }}>{error}</p>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        style={{ display: "flex", gap: "0.4rem" }}
      >
        <input
          ref={inputRef}
          type="text"
          maxLength={1000}
          placeholder={t("dash_coach_input_ph")}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="input-control"
          style={{ fontSize: "0.82rem", padding: "0.45rem 0.65rem" }}
        />
        <button
          type="submit"
          disabled={!projectId || sending || !input.trim()}
          className="btn-primary"
          style={{ padding: "0.45rem 0.8rem", fontSize: "0.8rem" }}
          aria-label="Send"
        >
          <Send size={14} />
        </button>
      </form>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "0.4rem", fontSize: "0.72rem", minHeight: "1rem" }}>
        {onSearchTopic ? (
          <button
            type="button"
            disabled={isSearching || !input.trim()}
            onClick={() => {
              onSearchTopic(input.trim());
              setInput("");
            }}
            style={{
              background: "none",
              border: "none",
              padding: 0,
              color: "var(--primary)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.25rem",
              fontSize: "0.72rem",
            }}
          >
            <Search size={11} /> {t("coach_search_this")}
          </button>
        ) : (
          <span />
        )}
        {remaining !== null && (
          <span style={{ color: "var(--on-surface-variant)" }}>
            {remaining} {t("coach_left_today")}
          </span>
        )}
      </div>
    </div>
  );
}
