import Link from "next/link";
import { ArrowRight, BookOpen, Layers, ShieldCheck, Sparkles, GraduationCap } from "lucide-react";

export default function HomePage() {
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
          <div style={{ display: "flex", gap: "0.85rem", alignItems: "center" }}>
            <Link href="/pricing" style={{ color: "var(--on-surface-variant)", fontSize: "0.9rem", fontWeight: 500 }}>
              Pricing (RM15/mo)
            </Link>
            <Link href="/login" className="btn-secondary" style={{ padding: "0.45rem 1rem", fontSize: "0.88rem" }}>
              Sign In
            </Link>
            <Link href="/dashboard" className="btn-primary" style={{ padding: "0.45rem 1.15rem", fontSize: "0.88rem" }}>
              Launch App
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container" style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", padding: "4rem 1.5rem" }}>
        <div style={{ maxWidth: "860px", margin: "0 auto", textAlign: "center" }}>
          <div className="badge badge-primary" style={{ marginBottom: "1.25rem", padding: "0.35rem 0.85rem" }}>
            <Sparkles size={14} /> Higher Education Research Intelligence
          </div>
          
          <h1 style={{ fontSize: "3.25rem", lineHeight: 1.2, fontWeight: 800, color: "var(--on-surface)", marginBottom: "1.25rem", letterSpacing: "-0.03em" }}>
            Find Novel Research Gaps for Your <span style={{ color: "var(--primary)" }}>Malaysian Thesis</span>
          </h1>
          
          <p style={{ color: "var(--on-surface-variant)", fontSize: "1.15rem", lineHeight: 1.6, maxWidth: "700px", margin: "0 auto 2.25rem auto" }}>
            Empowers Malaysian diploma, degree, and postgraduate researchers to identify defensible literature gaps, 
            formulate defended titles in English &amp; BM, and draft multi-objective research plans backed by institutional citations.
          </p>

          <div style={{ display: "flex", gap: "0.85rem", justifyContent: "center", flexWrap: "wrap" }}>
            <Link href="/login" className="btn-primary" style={{ fontSize: "1rem", padding: "0.75rem 1.75rem" }}>
              Get Started with Zero Keys <ArrowRight size={16} />
            </Link>
            <Link href="/pricing" className="btn-secondary" style={{ fontSize: "1rem", padding: "0.75rem 1.5rem" }}>
              View Student Pricing (RM15/mo)
            </Link>
          </div>
        </div>

        {/* Feature Highlights Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1.5rem", marginTop: "4.5rem" }}>
          <div className="card">
            <div style={{ width: "44px", height: "44px", borderRadius: "10px", background: "var(--surface-low)", color: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "1rem" }}>
              <BookOpen size={22} />
            </div>
            <h3 style={{ fontSize: "1.15rem", fontWeight: 700, marginBottom: "0.4rem", color: "var(--on-surface)" }}>
              Local Repository Indexing
            </h3>
            <p style={{ color: "var(--on-surface-variant)", fontSize: "0.9rem", lineHeight: 1.5 }}>
              Integrates genuine Malaysian repositories (UTM ePrints, MyJurnal) alongside OpenAlex global metadata for real academic context.
            </p>
          </div>

          <div className="card">
            <div style={{ width: "44px", height: "44px", borderRadius: "10px", background: "var(--surface-low)", color: "var(--secondary)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "1rem" }}>
              <Layers size={22} />
            </div>
            <h3 style={{ fontSize: "1.15rem", fontWeight: 700, marginBottom: "0.4rem", color: "var(--on-surface)" }}>
              5-Stage Academic Pipeline
            </h3>
            <p style={{ color: "var(--on-surface-variant)", fontSize: "0.9rem", lineHeight: 1.5 }}>
              Structured path: Topic Search → Gap Analysis → Title Suggestions (EN/BM) → Deep-Dive Citations → Research Plan &amp; Refinement.
            </p>
          </div>

          <div className="card">
            <div style={{ width: "44px", height: "44px", borderRadius: "10px", background: "var(--surface-low)", color: "var(--tertiary)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "1rem" }}>
              <ShieldCheck size={22} />
            </div>
            <h3 style={{ fontSize: "1.15rem", fontWeight: 700, marginBottom: "0.4rem", color: "var(--on-surface)" }}>
              Hardened Tenant Boundary
            </h3>
            <p style={{ color: "var(--on-surface-variant)", fontSize: "0.9rem", lineHeight: 1.5 }}>
              Row Level Security asserts complete boundary isolation between Malaysian universities and research teams.
            </p>
          </div>
        </div>

        {/* Coach Guidance Callout on Home */}
        <div className="coach-card" style={{ maxWidth: "800px", margin: "3rem auto 0 auto" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontWeight: 700, marginBottom: "0.3rem" }}>
            <Sparkles size={16} /> Ready for Academic Evaluation
          </div>
          MTIS runs 100% out-of-the-box in DEMO MODE with zero external API keys needed. You can also configure tenant-specific encrypted keys anytime in settings.
        </div>
      </main>

      {/* Footer */}
      <footer style={{ borderTop: "1px solid var(--border-subtle)", padding: "1.75rem 0", color: "var(--outline)", textAlign: "center", fontSize: "0.85rem", background: "#ffffff" }}>
        <div className="container">
          Malaysian Thesis Institution System (MTIS) • ScholarPulse Architecture • Designed for Malaysian Higher Education
        </div>
      </footer>
    </div>
  );
}
