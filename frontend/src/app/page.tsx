import Link from "next/link";
import { ArrowRight, BookOpen, Layers, ShieldCheck, Sparkles } from "lucide-react";

export default function HomePage() {
  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      {/* Top Navbar */}
      <header className="navbar">
        <div className="container nav-container">
          <Link href="/" className="logo">
            <span className="logo-dot"></span>
            MTIS
          </Link>
          <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
            <Link href="/pricing" style={{ color: "var(--text-muted)", fontSize: "0.95rem", fontWeight: 500 }}>
              Pricing
            </Link>
            <Link href="/login" className="btn-secondary" style={{ padding: "0.5rem 1.15rem", fontSize: "0.9rem" }}>
              Sign In
            </Link>
            <Link href="/dashboard" className="btn-primary" style={{ padding: "0.5rem 1.25rem", fontSize: "0.9rem" }}>
              Launch App
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container" style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center", padding: "4rem 1.5rem" }}>
        <div style={{ maxWidth: "800px", margin: "0 auto", textAlign: "center" }}>
          <div className="badge badge-tenant" style={{ marginBottom: "1.5rem" }}>
            <Sparkles size={14} /> Higher Education Research Intelligence
          </div>
          
          <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "3.25rem", lineHeight: 1.15, fontWeight: 700, marginBottom: "1.5rem" }}>
            Find Novel Research Gaps for Your <span style={{ color: "var(--primary)" }}>Malaysian Thesis</span>
          </h1>
          
          <p style={{ color: "var(--text-muted)", fontSize: "1.2rem", marginBottom: "2.5rem" }}>
            Helps Malaysian diploma, degree, and postgraduate researchers identify defensible gaps,
            validate titles, and draft structured research objectives citing real institutional literature.
          </p>

          <div style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
            <Link href="/login" className="btn-primary" style={{ fontSize: "1.05rem", padding: "0.85rem 2rem" }}>
              Get Started with Google <ArrowRight size={18} />
            </Link>
            <Link href="/pricing" className="btn-secondary" style={{ fontSize: "1.05rem", padding: "0.85rem 1.75rem" }}>
              View Student Pricing (RM15/mo)
            </Link>
          </div>
        </div>

        {/* Feature Highlights */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.5rem", marginTop: "5rem" }}>
          <div className="glass-card">
            <BookOpen style={{ color: "var(--primary)", marginBottom: "1rem" }} size={28} />
            <h3 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "0.5rem" }}>Local Repository Indexing</h3>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem" }}>
              Queries OpenAlex and Malaysian institutional repositories (UTM, MyJurnal, MyThesis) for genuine local context.
            </p>
          </div>

          <div className="glass-card">
            <Layers style={{ color: "var(--secondary)", marginBottom: "1rem" }} size={28} />
            <h3 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "0.5rem" }}>5-Stage Workflow</h3>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem" }}>
              Structured pipeline: Search Papers → Gap Analysis → Title Suggestions → Deep-Dive → Objectives & Methodology.
            </p>
          </div>

          <div className="glass-card">
            <ShieldCheck style={{ color: "var(--accent)", marginBottom: "1rem" }} size={28} />
            <h3 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "0.5rem" }}>Institutional Tenant Isolation</h3>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem" }}>
              Database-level Row Level Security guarantees complete boundary isolation between universities and research teams.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer style={{ borderTop: "1px solid var(--border-subtle)", padding: "2rem 0", color: "var(--text-dim)", textAlign: "center", fontSize: "0.9rem" }}>
        <div className="container">
          Malaysian Thesis Institution System (MTIS) • Local Dev Prototype
        </div>
      </footer>
    </div>
  );
}
