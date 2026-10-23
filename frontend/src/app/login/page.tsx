"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signInWithGoogle } from "@/lib/supabase";
import { setToken } from "@/lib/api";
import { Shield, Sparkles, Building2, UserCheck, ArrowRight, GraduationCap, Lock, ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Handle Google OAuth sign-in
  const handleGoogleSignIn = async () => {
    try {
      setLoading(true);
      setError(null);
      await signInWithGoogle();
    } catch (err: any) {
      setError(err?.message || "Failed to initialize Google Sign-In");
      setLoading(false);
    }
  };

  // Quick Demo Persona Switcher (For local evaluation, marker tests, and DEMO_MODE)
  const handleQuickDemoLogin = async (email: string, role: string, tenantId: string, name: string) => {
    try {
      setLoading(true);
      setError(null);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const isRemoteHost =
        typeof window !== "undefined" &&
        window.location.hostname !== "localhost" &&
        window.location.hostname !== "127.0.0.1";

      // If a real remote backend is configured or running locally, attempt real API login
      if (!isRemoteHost || !apiUrl.includes("localhost")) {
        try {
          const res = await fetch(`${apiUrl}/auth/demo-login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, role, tenant_id: tenantId, name }),
          });

          if (res.ok) {
            const data = await res.json();
            setToken(data.access_token);
            localStorage.setItem("mtis_user", JSON.stringify(data.user));
            localStorage.setItem("mtis_tenant", JSON.stringify(data.tenant));
            router.push("/dashboard");
            return;
          }
        } catch (netErr) {
          console.warn("Backend API not reachable, falling back to client-side demo mode:", netErr);
        }
      }

      // 100% Client-Side Demo Persona Fallback for Netlify / Cloud Preview
      const demoUser = {
        id: `usr-${email.split("@")[0]}`,
        tenant_id: tenantId,
        name: name,
        email: email,
        role: role,
        plan: role === "student" ? "free" : "enterprise",
        quota_remaining: role === "student" ? 3 : 999,
        quota_reset_at: new Date(Date.now() + 86400000).toISOString(),
        created_at: new Date().toISOString(),
      };
      const demoTenant = {
        id: tenantId,
        name: tenantId === "tenant-utm-001" ? "Universiti Teknologi Malaysia (UTM)" : "Demo University Campus",
      };

      setToken(`demo-token-${role}-${Date.now()}`);
      localStorage.setItem("mtis_user", JSON.stringify(demoUser));
      localStorage.setItem("mtis_tenant", JSON.stringify(demoTenant));

      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.message || "Demo login request failed");
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", backgroundColor: "var(--surface-canvas)" }}>
      {/* Top Navbar */}
      <header className="navbar">
        <div className="container nav-container">
          <Link href="/" className="logo">
            <span className="logo-dot"></span>
            ScholarPulse <span style={{ color: "var(--primary)", fontWeight: 800 }}>MTIS</span>
            <span className="logo-badge">Academic Coach v2.4</span>
          </Link>
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <Link href="/pricing" style={{ color: "var(--on-surface-variant)", fontSize: "0.9rem", fontWeight: 500 }}>
              Pricing (RM15/mo)
            </Link>
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.8rem", color: "var(--secondary)", background: "var(--secondary-container)", padding: "0.25rem 0.65rem", borderRadius: "9999px" }}>
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--secondary)" }}></span>
              Zero-Key Demo Active
            </div>
          </div>
        </div>
      </header>

      {/* Main Login Canvas */}
      <main className="container" style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "3rem 1.5rem" }}>
        <div className="card" style={{ width: "100%", maxWidth: "500px", padding: "2.5rem 2rem" }}>
          <div style={{ textAlign: "center", marginBottom: "1.75rem" }}>
            <div style={{ width: "52px", height: "52px", borderRadius: "14px", background: "var(--surface-low)", color: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1rem auto", border: "1px solid var(--surface-container)" }}>
              <GraduationCap size={28} />
            </div>
            <h1 style={{ fontSize: "1.75rem", fontWeight: 700, color: "var(--on-surface)", marginBottom: "0.4rem" }}>
              Sign in to MTIS
            </h1>
            <p style={{ color: "var(--on-surface-variant)", fontSize: "0.92rem" }}>
              Institutional Thesis Structuring &amp; Research Gap Discovery
            </p>
          </div>

          {error && (
            <div style={{ background: "var(--error-container)", border: "1px solid rgba(186, 26, 26, 0.2)", color: "var(--on-error-container)", padding: "0.75rem 1rem", borderRadius: "8px", fontSize: "0.88rem", marginBottom: "1.25rem" }}>
              {error}
            </div>
          )}

          {/* Primary Action: Google Auth (Coming Soon — Supabase not configured) */}
          <button
            disabled={true}
            className="btn-secondary"
            style={{ width: "100%", padding: "0.75rem", fontSize: "0.95rem", marginBottom: "0.5rem", opacity: 0.5 }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" style={{ marginRight: "0.25rem" }}>
              <path fill="#4285F4" d="M21.35 11.1h-9.17v2.98h5.27c-.23 1.25-.94 2.3-2 3.01v2.5h3.24c1.89-1.74 2.98-4.3 2.98-7.39 0-.71-.06-1.4-.32-1.1z"/>
              <path fill="#34A853" d="M12.18 21c2.7 0 4.96-.89 6.62-2.42l-3.24-2.5c-.9.6-2.04.96-3.38.96-2.6 0-4.8-1.75-5.59-4.11H3.24v2.58A9.99 9.99 0 0 0 12.18 21z"/>
              <path fill="#FBBC05" d="M6.59 12.93c-.2-.6-.32-1.25-.32-1.93s.12-1.33.32-1.93V6.49H3.24A9.99 9.99 0 0 0 2 11c0 1.61.39 3.14 1.24 4.51l3.35-2.58z"/>
              <path fill="#EA4335" d="M12.18 4.96c1.47 0 2.78.51 3.82 1.5l2.86-2.86C17.13 1.99 14.88 1 12.18 1 7.68 1 3.84 3.58 2.01 7.49l3.35 2.58c.79-2.36 2.99-4.11 5.82-4.11z"/>
            </svg>
            Continue with Google (Coming Soon)
          </button>
          <p style={{ textAlign: "center", fontSize: "0.75rem", color: "var(--outline)", marginBottom: "1.25rem" }}>
            Google Sign-In will be available after deployment. Use demo personas below.
          </p>

          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", margin: "1.25rem 0", color: "var(--outline)", fontSize: "0.78rem", textTransform: "uppercase", letterSpacing: "0.05em", fontWeight: 600 }}>
            <div style={{ flex: 1, height: "1px", background: "var(--border-subtle)" }} />
            <span>OR TEST PERSONAS (DEMO MODE)</span>
            <div style={{ flex: 1, height: "1px", background: "var(--border-subtle)" }} />
          </div>

          {/* Quick Persona Selectors */}
          <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", margin: "0.2rem 0", color: "var(--outline)", fontSize: "0.72rem", textTransform: "uppercase", letterSpacing: "0.05em", fontWeight: 600 }}>
              <div style={{ flex: 1, height: "1px", background: "var(--border-subtle)" }} />
              <span>RESEARCHER / STUDENT ACCESS</span>
              <div style={{ flex: 1, height: "1px", background: "var(--border-subtle)" }} />
            </div>

            <button
              onClick={() => handleQuickDemoLogin("student@demo.test", "student", "tenant-demo-002", "Demo Student Researcher")}
              className="btn-secondary"
              style={{ width: "100%", justifyContent: "space-between", padding: "0.65rem 0.85rem", fontSize: "0.88rem" }}
            >
              <span style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Building2 size={16} color="var(--primary)" /> Demo University Researcher
              </span>
              <span className="badge badge-student">student@demo.test</span>
            </button>

            <button
              onClick={() => handleQuickDemoLogin("ahmad@utm.my", "student", "tenant-utm-001", "Ahmad (UTM Researcher)")}
              className="btn-secondary"
              style={{ width: "100%", justifyContent: "space-between", padding: "0.65rem 0.85rem", fontSize: "0.88rem" }}
            >
              <span style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Building2 size={16} color="var(--secondary)" /> UTM Researcher (Ahmad)
              </span>
              <span className="badge badge-tenant">ahmad@utm.my</span>
            </button>

            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", margin: "0.5rem 0 0.2rem 0", color: "var(--outline)", fontSize: "0.72rem", textTransform: "uppercase", letterSpacing: "0.05em", fontWeight: 600 }}>
              <div style={{ flex: 1, height: "1px", background: "var(--border-subtle)" }} />
              <span>SYSTEM OWNER / ADMIN ACCESS</span>
              <div style={{ flex: 1, height: "1px", background: "var(--border-subtle)" }} />
            </div>

            <button
              onClick={() => handleQuickDemoLogin("admin@demo.test", "admin", "tenant-demo-002", "System Owner / Admin")}
              className="btn-secondary"
              style={{ width: "100%", justifyContent: "space-between", padding: "0.65rem 0.85rem", fontSize: "0.88rem", borderColor: "#fecaca" }}
            >
              <span style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <ShieldCheck size={16} color="#dc2626" /> System Admin (Owner)
              </span>
              <span className="badge badge-admin">admin@demo.test</span>
            </button>
          </div>

          {/* Coach Guidance Note */}
          <div className="coach-card" style={{ marginTop: "1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontWeight: 600, marginBottom: "0.25rem" }}>
              <Sparkles size={14} color="var(--tertiary)" />
              Coach Guidance
            </div>
            MTIS isolates research workspaces by institutional tenant. Selecting any demo persona simulates verified campus credentials with zero external setup required.
          </div>
        </div>
      </main>
    </div>
  );
}
