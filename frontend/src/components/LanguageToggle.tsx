"use client";

import React from "react";
import { useLanguage } from "@/lib/LanguageContext";
import { Globe } from "lucide-react";

export function LanguageToggle() {
  const { lang, setLang } = useLanguage();

  return (
    <div
      className="lang-toggle-container"
      title="Tukar Bahasa / Switch Language (Bahasa Malaysia & English)"
      style={{
        display: "inline-flex",
        alignItems: "center",
        background: "var(--surface-low)",
        border: "1px solid var(--border-subtle)",
        borderRadius: "9999px",
        padding: "2px",
        fontSize: "0.78rem",
        fontWeight: 600,
        userSelect: "none",
        boxShadow: "var(--shadow-sm)",
      }}
    >
      <button
        type="button"
        onClick={() => setLang("en")}
        style={{
          border: "none",
          cursor: "pointer",
          padding: "0.22rem 0.55rem",
          borderRadius: "9999px",
          background: lang === "en" ? "var(--primary)" : "transparent",
          color: lang === "en" ? "#ffffff" : "var(--on-surface-variant)",
          transition: "all 0.18s ease-in-out",
          display: "flex",
          alignItems: "center",
          gap: "0.25rem",
          fontWeight: lang === "en" ? 700 : 500,
          boxShadow: lang === "en" ? "0 1px 3px rgba(0, 97, 148, 0.25)" : "none",
        }}
      >
        <span>🇬🇧</span>
        <span>EN</span>
      </button>

      <button
        type="button"
        onClick={() => setLang("bm")}
        style={{
          border: "none",
          cursor: "pointer",
          padding: "0.22rem 0.55rem",
          borderRadius: "9999px",
          background: lang === "bm" ? "var(--primary)" : "transparent",
          color: lang === "bm" ? "#ffffff" : "var(--on-surface-variant)",
          transition: "all 0.18s ease-in-out",
          display: "flex",
          alignItems: "center",
          gap: "0.25rem",
          fontWeight: lang === "bm" ? 700 : 500,
          boxShadow: lang === "bm" ? "0 1px 3px rgba(0, 97, 148, 0.25)" : "none",
        }}
      >
        <span>🇲🇾</span>
        <span>BM</span>
      </button>
    </div>
  );
}

export default LanguageToggle;
