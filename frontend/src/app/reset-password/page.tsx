"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { KeyRound, Lock } from "lucide-react";
import { useLanguage } from "@/lib/LanguageContext";
import { TranslationKey } from "@/lib/translations";
import LanguageToggle from "@/components/LanguageToggle";
import { authErrorKey, isSupabaseConfigured, supabase, updatePassword } from "@/lib/supabase";

const MIN_PASSWORD = 8;

/** Opened from the "Reset password" email: the link carries a recovery session from Supabase. */
export default function ResetPasswordPage() {
  const router = useRouter();
  const { t } = useLanguage();
  const [status, setStatus] = useState<"checking" | "ready" | "invalid" | "done">("checking");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isSupabaseConfigured) {
      setStatus("invalid");
      return;
    }
    const { data } = supabase.auth.onAuthStateChange((event, session) => {
      if (session && (event === "PASSWORD_RECOVERY" || event === "SIGNED_IN" || event === "INITIAL_SESSION")) {
        setStatus("ready");
      }
    });
    // Give Supabase a moment to read the link; without a session the link is invalid or expired
    const timer = setTimeout(async () => {
      const { data: s } = await supabase.auth.getSession();
      setStatus((prev) => (prev === "checking" ? (s.session ? "ready" : "invalid") : prev));
    }, 1500);
    return () => {
      clearTimeout(timer);
      data.subscription.unsubscribe();
    };
  }, []);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password.length < MIN_PASSWORD) return setError(t("auth_err_weak"));
    if (password !== confirm) return setError(t("auth_err_mismatch"));
    setBusy(true);
    setError(null);
    try {
      await updatePassword(password);
      setStatus("done");
      // The session is still active: /login completes sign-in and opens the dashboard
      setTimeout(() => router.push("/login"), 1500);
    } catch (err) {
      setError(t(authErrorKey(err) as TranslationKey));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", backgroundColor: "var(--surface-canvas)" }}>
      <header className="navbar">
        <div className="container nav-container">
          <Link href="/" className="logo">
            <span className="logo-dot"></span>
            ScholarPulse <span style={{ color: "var(--primary)", fontWeight: 800 }}>MTIS</span>
          </Link>
          <LanguageToggle />
        </div>
      </header>

      <main className="container" style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "3rem 1rem" }}>
        <div className="card" style={{ width: "100%", maxWidth: "440px", padding: "2.25rem 1.75rem" }}>
          <div style={{ textAlign: "center", marginBottom: "1.25rem" }}>
            <div style={{ width: "48px", height: "48px", borderRadius: "14px", background: "var(--surface-low)", color: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 0.85rem" }}>
              <KeyRound size={24} />
            </div>
            <h1 style={{ fontSize: "1.4rem", fontWeight: 700 }}>{t("auth_reset_title")}</h1>
          </div>

          {status === "checking" && (
            <p style={{ textAlign: "center", color: "var(--on-surface-variant)" }}>{t("auth_please_wait")}</p>
          )}

          {status === "invalid" && (
            <div style={{ textAlign: "center" }}>
              <p style={{ color: "var(--on-surface-variant)", marginBottom: "1rem" }}>{t("auth_reset_invalid")}</p>
              <Link href="/login" className="btn-primary" style={{ width: "100%", justifyContent: "center" }}>
                {t("auth_back_to_signin")}
              </Link>
            </div>
          )}

          {status === "done" && (
            <p role="status" style={{ textAlign: "center", color: "var(--secondary)", fontWeight: 600 }}>{t("auth_reset_done")}</p>
          )}

          {status === "ready" && (
            <form onSubmit={onSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.7rem" }}>
              <p style={{ fontSize: "0.86rem", color: "var(--on-surface-variant)", margin: 0 }}>{t("auth_reset_desc")}</p>
              {[
                { value: password, set: setPassword, label: t("auth_password_new") },
                { value: confirm, set: setConfirm, label: t("auth_password_confirm") },
              ].map((f) => (
                <label key={f.label} style={{ position: "relative" }}>
                  <span className="sr-only">{f.label}</span>
                  <Lock size={15} style={{ position: "absolute", left: "0.7rem", top: "50%", transform: "translateY(-50%)", color: "var(--outline)" }} />
                  <input
                    className="input-control"
                    style={{ paddingLeft: "2.1rem" }}
                    type="password"
                    autoComplete="new-password"
                    required
                    placeholder={f.label}
                    value={f.value}
                    onChange={(e) => f.set(e.target.value)}
                  />
                </label>
              ))}
              {error && (
                <div role="alert" style={{ background: "var(--error-container)", color: "var(--on-error-container)", padding: "0.6rem 0.8rem", borderRadius: "8px", fontSize: "0.84rem" }}>
                  {error}
                </div>
              )}
              <button type="submit" className="btn-primary" disabled={busy} style={{ width: "100%", padding: "0.7rem", justifyContent: "center" }}>
                {busy ? t("auth_please_wait") : t("auth_btn_save_password")}
              </button>
            </form>
          )}
        </div>
      </main>
    </div>
  );
}
