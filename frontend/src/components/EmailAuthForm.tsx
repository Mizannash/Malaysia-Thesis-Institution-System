"use client";

import { useState } from "react";
import { Mail, Lock, User, ArrowLeft } from "lucide-react";
import { useLanguage } from "@/lib/LanguageContext";
import { TranslationKey } from "@/lib/translations";
import {
  authErrorKey,
  resendConfirmation,
  sendPasswordReset,
  signInWithEmail,
  signUpWithEmail,
} from "@/lib/supabase";

type Mode = "signin" | "signup" | "forgot" | "check-email" | "reset-sent";

const MIN_PASSWORD = 8;

/**
 * MTIS account sign-in / sign-up / forgot-password (Supabase Auth).
 * On successful sign-in, Supabase fires SIGNED_IN and the login page completes the session.
 */
export default function EmailAuthForm({ initialMode = "signin" }: { initialMode?: Mode }) {
  const { t } = useLanguage();
  const [mode, setMode] = useState<Mode>(initialMode);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const switchMode = (next: Mode) => {
    setMode(next);
    setError(null);
    setNotice(null);
    setPassword("");
    setConfirm("");
  };

  const run = async (action: () => Promise<void>) => {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await action();
    } catch (err) {
      setError(t(authErrorKey(err) as TranslationKey));
    } finally {
      setBusy(false);
    }
  };

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cleanEmail = email.trim().toLowerCase();
    if (mode === "signin") {
      run(async () => {
        await signInWithEmail(cleanEmail, password);
      });
    } else if (mode === "signup") {
      if (password.length < MIN_PASSWORD) return setError(t("auth_err_weak"));
      if (password !== confirm) return setError(t("auth_err_mismatch"));
      run(async () => {
        await signUpWithEmail(name.trim(), cleanEmail, password);
        switchMode("check-email");
      });
    } else if (mode === "forgot") {
      run(async () => {
        try {
          await sendPasswordReset(cleanEmail);
        } catch (err) {
          // Only rate limits are shown; never reveal whether an email is registered
          if (authErrorKey(err) === "auth_err_rate") throw err;
        }
        switchMode("reset-sent");
      });
    }
  };

  const inputStyle = { paddingLeft: "2.1rem" };
  const iconStyle = { position: "absolute" as const, left: "0.7rem", top: "50%", transform: "translateY(-50%)", color: "var(--outline)" };

  if (mode === "check-email" || mode === "reset-sent") {
    return (
      <div style={{ textAlign: "center" }}>
        <div style={{ width: "48px", height: "48px", borderRadius: "50%", background: "var(--secondary-container)", color: "var(--secondary)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 0.85rem" }}>
          <Mail size={22} />
        </div>
        <h2 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "0.4rem" }}>
          {t(mode === "check-email" ? "auth_check_email_title" : "auth_reset_sent_title")}
        </h2>
        <p style={{ fontSize: "0.88rem", color: "var(--on-surface-variant)", marginBottom: "1rem" }}>
          {t(mode === "check-email" ? "auth_check_email_desc" : "auth_reset_sent_desc")} <strong>{email.trim()}</strong>
        </p>
        {error && <p style={{ color: "var(--error)", fontSize: "0.82rem", marginBottom: "0.6rem" }}>{error}</p>}
        {notice && <p style={{ color: "var(--secondary)", fontSize: "0.82rem", marginBottom: "0.6rem" }}>{notice}</p>}
        {mode === "check-email" && (
          <button
            type="button"
            className="btn-secondary"
            disabled={busy}
            style={{ width: "100%", marginBottom: "0.5rem" }}
            onClick={() => run(async () => {
              await resendConfirmation(email.trim().toLowerCase());
              setNotice(t("auth_resent"));
            })}
          >
            {t("auth_resend")}
          </button>
        )}
        <button type="button" className="btn-primary" style={{ width: "100%" }} onClick={() => switchMode("signin")}>
          {t("auth_back_to_signin")}
        </button>
      </div>
    );
  }

  return (
    <div>
      {mode !== "forgot" ? (
        <div role="tablist" style={{ display: "flex", background: "var(--surface-low)", borderRadius: "10px", padding: "4px", marginBottom: "1.1rem" }}>
          {(["signin", "signup"] as const).map((m) => (
            <button
              key={m}
              type="button"
              role="tab"
              aria-selected={mode === m}
              onClick={() => switchMode(m)}
              style={{
                flex: 1,
                border: "none",
                borderRadius: "8px",
                padding: "0.5rem",
                fontWeight: 600,
                fontSize: "0.88rem",
                cursor: "pointer",
                background: mode === m ? "var(--surface-card)" : "transparent",
                color: mode === m ? "var(--primary)" : "var(--on-surface-variant)",
                boxShadow: mode === m ? "var(--shadow-sm)" : "none",
              }}
            >
              {t(m === "signin" ? "auth_tab_signin" : "auth_tab_signup")}
            </button>
          ))}
        </div>
      ) : (
        <div style={{ marginBottom: "1rem" }}>
          <button
            type="button"
            onClick={() => switchMode("signin")}
            style={{ background: "none", border: "none", padding: 0, color: "var(--primary)", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.3rem", fontSize: "0.85rem", marginBottom: "0.6rem" }}
          >
            <ArrowLeft size={14} /> {t("auth_back_to_signin")}
          </button>
          <h2 style={{ fontSize: "1.05rem", fontWeight: 700, marginBottom: "0.25rem" }}>{t("auth_forgot_title")}</h2>
          <p style={{ fontSize: "0.85rem", color: "var(--on-surface-variant)" }}>{t("auth_forgot_desc")}</p>
        </div>
      )}

      <form onSubmit={onSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.7rem" }}>
        {mode === "signup" && (
          <label style={{ position: "relative" }}>
            <span className="sr-only">{t("auth_name")}</span>
            <User size={15} style={iconStyle} />
            <input
              className="input-control"
              style={inputStyle}
              type="text"
              autoComplete="name"
              required
              maxLength={120}
              placeholder={t("auth_name")}
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </label>
        )}

        <label style={{ position: "relative" }}>
          <span className="sr-only">{t("auth_email")}</span>
          <Mail size={15} style={iconStyle} />
          <input
            className="input-control"
            style={inputStyle}
            type="email"
            autoComplete="email"
            required
            placeholder={t("auth_email")}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>

        {mode !== "forgot" && (
          <label style={{ position: "relative" }}>
            <span className="sr-only">{t("auth_password")}</span>
            <Lock size={15} style={iconStyle} />
            <input
              className="input-control"
              style={inputStyle}
              type="password"
              autoComplete={mode === "signup" ? "new-password" : "current-password"}
              required
              minLength={mode === "signup" ? MIN_PASSWORD : undefined}
              placeholder={t("auth_password")}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
        )}

        {mode === "signup" && (
          <>
            <label style={{ position: "relative" }}>
              <span className="sr-only">{t("auth_password_confirm")}</span>
              <Lock size={15} style={iconStyle} />
              <input
                className="input-control"
                style={inputStyle}
                type="password"
                autoComplete="new-password"
                required
                placeholder={t("auth_password_confirm")}
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
              />
            </label>
            <p style={{ fontSize: "0.76rem", color: "var(--on-surface-variant)", margin: 0 }}>{t("auth_signup_hint")}</p>
          </>
        )}

        {mode === "signin" && (
          <button
            type="button"
            onClick={() => switchMode("forgot")}
            style={{ alignSelf: "flex-end", background: "none", border: "none", padding: 0, color: "var(--primary)", cursor: "pointer", fontSize: "0.82rem" }}
          >
            {t("auth_forgot_link")}
          </button>
        )}

        {error && (
          <div role="alert" style={{ background: "var(--error-container)", color: "var(--on-error-container)", padding: "0.6rem 0.8rem", borderRadius: "8px", fontSize: "0.84rem" }}>
            {error}
          </div>
        )}

        <button type="submit" className="btn-primary" disabled={busy} style={{ width: "100%", padding: "0.7rem", justifyContent: "center" }}>
          {busy
            ? t("auth_please_wait")
            : t(mode === "signin" ? "auth_btn_signin" : mode === "signup" ? "auth_btn_signup" : "auth_btn_send_reset")}
        </button>
      </form>
    </div>
  );
}
