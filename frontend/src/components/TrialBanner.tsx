"use client";

import Link from "next/link";
import { Clock, Lock } from "lucide-react";
import { useLanguage } from "@/lib/LanguageContext";

interface TrialUser {
  access_status?: string | null;
  trial_ends_at?: string | null;
}

const DAY_MS = 24 * 60 * 60 * 1000;

/** Free-trial countdown, or the "trial ended" notice. Hidden for subscribed users and staff. */
export default function TrialBanner({ user }: { user: TrialUser | null }) {
  const { t } = useLanguage();
  const status = user?.access_status;
  if (status !== "trial" && status !== "expired") return null;

  if (status === "expired") {
    return (
      <div role="alert" className="container" style={{ marginTop: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap", background: "var(--error-container)", color: "var(--on-error-container)", borderRadius: "10px", padding: "0.75rem 1rem", fontSize: "0.88rem" }}>
          <Lock size={16} />
          <span style={{ flex: 1, minWidth: "200px" }}>
            <strong>{t("trial_ended_title")}</strong> {t("trial_ended_desc")}
          </span>
          <Link href="/pricing" className="btn-primary" style={{ padding: "0.4rem 0.9rem", fontSize: "0.82rem" }}>
            {t("trial_subscribe")}
          </Link>
        </div>
      </div>
    );
  }

  const ends = user?.trial_ends_at ? new Date(user.trial_ends_at).getTime() : NaN;
  const daysLeft = Number.isFinite(ends) ? Math.max(1, Math.ceil((ends - Date.now()) / DAY_MS)) : null;
  const urgent = daysLeft !== null && daysLeft <= 3;

  return (
    <div role="status" className="container" style={{ marginTop: "1rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap", background: urgent ? "#fef3c7" : "var(--surface-low)", color: urgent ? "#92400e" : "var(--on-surface)", border: "1px solid var(--border-subtle)", borderRadius: "10px", padding: "0.65rem 1rem", fontSize: "0.86rem" }}>
        <Clock size={16} />
        <span style={{ flex: 1, minWidth: "200px" }}>
          {daysLeft !== null ? t("trial_days_left").replace("{n}", String(daysLeft)) : t("trial_active")}
        </span>
        <Link href="/pricing" className="btn-secondary" style={{ padding: "0.35rem 0.85rem", fontSize: "0.8rem" }}>
          {t("trial_subscribe")}
        </Link>
      </div>
    </div>
  );
}
