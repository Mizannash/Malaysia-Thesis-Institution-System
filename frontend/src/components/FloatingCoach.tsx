"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { X } from "lucide-react";
import { useLanguage } from "@/lib/LanguageContext";
import { TranslationKey } from "@/lib/translations";
import CoachChat, { CoachAutoSend, STAGE_SUGGESTION } from "./CoachChat";
import BijakRobot, { BijakMood } from "./BijakRobot";

const OPEN_STORAGE_KEY = "mtis_coach_open";
const MUTE_STORAGE_KEY = "mtis_bijak_muted";
const NUDGE_SECONDS = 15;

// Random "need help?" lines: balanced frequency
const FIRST_LINE_AFTER_MS = 20_000;
const LINE_GAP_MS = 150_000;
const MAX_LINES_PER_VISIT = 4;
const LINE_VISIBLE_MS = 12_000;
const QUIET_AFTER_TYPING_MS = 10_000;
const LINE_CHECK_MS = 5_000;

const BIJAK_LINES: TranslationKey[] = [
  "bijak_line_1",
  "bijak_line_2",
  "bijak_line_3",
  "bijak_line_4",
  "bijak_line_5",
  "bijak_line_6",
  "bijak_line_7",
  "bijak_line_8",
];

const STAGE_TITLE: Record<string, TranslationKey> = {
  search: "dash_stage1_title",
  gap: "dash_stage2_title",
  title: "dash_stage3_title",
  "deep-dive": "dash_stage4_title",
  deepdive: "dash_stage4_title",
  plan: "dash_stage5_title",
};

const STAGE_NUDGE: Record<string, TranslationKey> = {
  gap: "coach_nudge_gap",
  title: "coach_nudge_title",
  "deep-dive": "coach_nudge_deepdive",
  deepdive: "coach_nudge_deepdive",
  plan: "coach_nudge_plan",
};

function readFlag(key: string): boolean {
  try {
    return localStorage.getItem(key) === "1";
  } catch {
    return false;
  }
}

function writeFlag(key: string, value: boolean) {
  try {
    localStorage.setItem(key, value ? "1" : "0");
  } catch {
    // storage blocked: the setting still applies for this visit
  }
}

/** Open/closed state for the floating coach, remembered per browser. */
export function useCoachOpen(): [boolean, (open: boolean) => void] {
  const [open, setOpenState] = useState(false);

  useEffect(() => {
    setOpenState(readFlag(OPEN_STORAGE_KEY));
  }, []);

  const setOpen = useCallback((next: boolean) => {
    setOpenState(next);
    writeFlag(OPEN_STORAGE_KEY, next);
  }, []);

  return [open, setOpen];
}

interface FloatingCoachProps {
  projectId: string | null;
  stage: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  busy?: boolean;
  isSearching?: boolean;
  onSearchTopic?: (query: string) => void;
}

export default function FloatingCoach({ projectId, stage, open, onOpenChange, busy = false, isSearching, onSearchTopic }: FloatingCoachProps) {
  const { t } = useLanguage();
  const [nudgeStage, setNudgeStage] = useState<string | null>(null);
  const [randomLine, setRandomLine] = useState<TranslationKey | null>(null);
  const [unread, setUnread] = useState(false);
  const [muted, setMuted] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [autoSend, setAutoSend] = useState<CoachAutoSend | null>(null);
  const prevStage = useRef<string | null>(null);
  const loadedAt = useRef(Date.now());
  const lastLineAt = useRef<number | null>(null);
  const lastLineKey = useRef<TranslationKey | null>(null);
  const linesShown = useRef(0);
  const lastKeyAt = useRef(0);

  useEffect(() => {
    setMuted(readFlag(MUTE_STORAGE_KEY));
    const onKey = () => {
      lastKeyAt.current = Date.now();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  // Stage nudge: when a stage finishes while the panel is closed (takes priority over random lines)
  useEffect(() => {
    const previous = prevStage.current;
    prevStage.current = stage;
    if (previous === null || previous === stage || open || !STAGE_NUDGE[stage]) return;
    setRandomLine(null);
    setNudgeStage(stage);
    setUnread(true);
  }, [stage, open]);

  useEffect(() => {
    if (!nudgeStage) return;
    const timer = setTimeout(() => setNudgeStage(null), NUDGE_SECONDS * 1000);
    return () => clearTimeout(timer);
  }, [nudgeStage]);

  // Random "need help?" lines, only when the student is not busy
  useEffect(() => {
    if (muted) return;
    const timer = setInterval(() => {
      const now = Date.now();
      const due = lastLineAt.current === null
        ? now - loadedAt.current >= FIRST_LINE_AFTER_MS
        : now - lastLineAt.current >= LINE_GAP_MS;
      const quiet =
        open ||
        busy ||
        nudgeStage !== null ||
        randomLine !== null ||
        linesShown.current >= MAX_LINES_PER_VISIT ||
        now - lastKeyAt.current < QUIET_AFTER_TYPING_MS ||
        document.visibilityState !== "visible";
      if (!due || quiet) return;

      const choices = BIJAK_LINES.filter((key) => key !== lastLineKey.current);
      const next = choices[Math.floor(Math.random() * choices.length)];
      lastLineKey.current = next;
      lastLineAt.current = now;
      linesShown.current += 1;
      setRandomLine(next);
    }, LINE_CHECK_MS);
    return () => clearInterval(timer);
  }, [muted, open, busy, nudgeStage, randomLine]);

  useEffect(() => {
    if (!randomLine) return;
    const timer = setTimeout(() => setRandomLine(null), LINE_VISIBLE_MS);
    return () => clearTimeout(timer);
  }, [randomLine]);

  useEffect(() => {
    if (!open) return;
    setUnread(false);
    setNudgeStage(null);
    setRandomLine(null);
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onOpenChange(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onOpenChange]);

  const askFromNudge = () => {
    if (!nudgeStage) return;
    const suggestion = STAGE_SUGGESTION[nudgeStage];
    if (suggestion) setAutoSend({ id: Date.now(), text: t(suggestion) });
    onOpenChange(true);
  };

  const muteLines = () => {
    setMuted(true);
    setRandomLine(null);
    writeFlag(MUTE_STORAGE_KEY, true);
  };

  const mood: BijakMood = thinking ? "thinking" : nudgeStage || randomLine ? "talking" : "idle";

  return (
    <>
      <section
        className="coach-panel"
        role="dialog"
        aria-label={`${t("bijak_name")} · ${t("coach_title")}`}
        hidden={!open}
      >
        <header className="coach-panel-header">
          <div style={{ display: "flex", alignItems: "center", gap: "0.55rem", minWidth: 0 }}>
            <span className="coach-avatar">
              <BijakRobot size={30} mood={thinking ? "thinking" : "idle"} animated={false} />
            </span>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontWeight: 700, fontSize: "0.92rem" }}>
                {t("bijak_name")} <span style={{ fontWeight: 500, opacity: 0.85 }}>· {t("coach_title")}</span>
              </div>
              <div style={{ fontSize: "0.72rem", opacity: 0.85, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {t(STAGE_TITLE[stage] || "dash_stage1_title")}
              </div>
            </div>
          </div>
          <button
            type="button"
            className="coach-icon-btn"
            onClick={() => onOpenChange(false)}
            aria-label={t("coach_minimise")}
            title={t("coach_minimise")}
          >
            <X size={16} />
          </button>
        </header>
        <div className="coach-panel-body">
          <CoachChat
            projectId={projectId}
            stage={stage}
            active={open}
            autoSend={autoSend}
            isSearching={isSearching}
            onSearchTopic={onSearchTopic}
            onSendingChange={setThinking}
          />
        </div>
      </section>

      {!open && nudgeStage && STAGE_NUDGE[nudgeStage] && (
        <div className="coach-nudge" role="status">
          <p style={{ margin: 0 }}>{t(STAGE_NUDGE[nudgeStage])}</p>
          <div style={{ display: "flex", gap: "0.4rem", justifyContent: "flex-end", marginTop: "0.5rem" }}>
            <button type="button" className="btn-secondary" style={{ fontSize: "0.72rem", padding: "0.25rem 0.6rem" }} onClick={() => setNudgeStage(null)}>
              {t("coach_nudge_dismiss")}
            </button>
            <button type="button" className="btn-primary" style={{ fontSize: "0.72rem", padding: "0.25rem 0.7rem" }} onClick={askFromNudge}>
              {t("coach_nudge_ask")}
            </button>
          </div>
        </div>
      )}

      {!open && !nudgeStage && randomLine && (
        <div className="coach-nudge coach-nudge--line" role="status">
          <button
            type="button"
            className="coach-icon-btn coach-nudge-close"
            onClick={() => setRandomLine(null)}
            aria-label={t("coach_nudge_dismiss")}
          >
            <X size={13} />
          </button>
          <button type="button" className="coach-nudge-text" onClick={() => onOpenChange(true)}>
            {t(randomLine)}
          </button>
          <button type="button" className="coach-nudge-mute" onClick={muteLines}>
            {t("bijak_mute")}
          </button>
        </div>
      )}

      {!open && (
        <button
          type="button"
          className="coach-launcher"
          onClick={() => onOpenChange(true)}
          aria-label={t("bijak_open")}
          title={t("bijak_open")}
        >
          <BijakRobot size={52} mood={mood} />
          {unread && <span className="coach-unread-dot" aria-hidden="true" />}
        </button>
      )}
    </>
  );
}
