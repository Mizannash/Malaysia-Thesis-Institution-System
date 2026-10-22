"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { clearToken, fetchWithAuth, getToken, getApiErrorMessage } from "@/lib/api";
import {
  FileText,
  Sparkles,
  ArrowLeft,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Target,
  Milestone,
  Package,
  Layers,
  Send,
  Building2,
  ShieldCheck,
  LogOut,
  Calendar,
  Lightbulb,
  Check,
  ChevronRight,
  User,
  GraduationCap
} from "lucide-react";

function PlanViewContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectIdParam = searchParams.get("projectId");

  const [user, setUser] = useState<any>(null);
  const [project, setProject] = useState<any>(null);
  const [plan, setPlan] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [refining, setRefining] = useState(false);
  const [refinePrompt, setRefinePrompt] = useState("");
  const [notification, setNotification] = useState<{ type: "success" | "error"; message: string } | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }

    const loadData = async () => {
      try {
        const userRes = await fetchWithAuth("/auth/me");
        if (!userRes.ok) {
          clearToken();
          router.push("/login");
          return;
        }
        const userData = await userRes.json();
        setUser(userData);

        // Fetch project
        if (projectIdParam) {
          const projRes = await fetchWithAuth(`/projects/${projectIdParam}`);
          if (projRes.ok) {
            const p = await projRes.json();
            setProject(p);
            if (p.current_plan_json) {
              setPlan(p.current_plan_json);
            } else if (p.state_json?.plan) {
              setPlan(p.state_json.plan);
            }
          }
        } else {
          // Fallback: list projects and pick first
          const projListRes = await fetchWithAuth("/projects");
          if (projListRes.ok) {
            const list = await projListRes.json();
            if (list.length > 0) {
              const p = list[0];
              setProject(p);
              if (p.current_plan_json) {
                setPlan(p.current_plan_json);
              } else if (p.state_json?.plan) {
                setPlan(p.state_json.plan);
              }
            }
          }
        }
      } catch (err: any) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [projectIdParam, router]);

  const handleGeneratePlan = async () => {
    if (!project) return;
    setGenerating(true);
    setNotification(null);

    try {
      const res = await fetchWithAuth(`/projects/${project.id}/stage/plan`, {
        method: "POST",
        body: JSON.stringify({ project_id: project.id }),
      });

      if (res.ok) {
        const updatedProject = await res.json();
        setProject(updatedProject);
        setPlan(updatedProject.current_plan_json);
        setNotification({
          type: "success",
          message: "Structured thesis plan generated successfully within contract parameters!",
        });
      } else {
        const err = await res.json();
        setNotification({
          type: "error",
          message: getApiErrorMessage(err, "Failed to generate plan."),
        });
      }
    } catch (err: any) {
      setNotification({ type: "error", message: getApiErrorMessage(err, "Network error") });
    } finally {
      setGenerating(false);
    }
  };

  const handleRefinePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!refinePrompt.trim() || !project || !plan) return;
    setRefining(true);
    setNotification(null);

    try {
      const res = await fetchWithAuth("/api/plan/refine", {
        method: "POST",
        body: JSON.stringify({
          plan_id: plan.plan_id || project.plan_id,
          project_id: project.id,
          user_prompt: refinePrompt.trim(),
        }),
      });

      if (res.ok) {
        const refineData = await res.json();
        setPlan(refineData.plan);
        setProject((prev: any) => ({
          ...prev,
          plan_version: refineData.plan_version,
          current_plan_json: refineData.plan,
          last_refined_at: new Date().toISOString(),
        }));
        setRefinePrompt("");
        setNotification({
          type: "success",
          message: `Plan updated to Version ${refineData.plan_version}: ${refineData.diff_summary || "Refinement applied successfully."}`,
        });
      } else {
        const err = await res.json();
        setNotification({
          type: "error",
          message: getApiErrorMessage(err, "Failed to refine plan."),
        });
      }
    } catch (err: any) {
      setNotification({ type: "error", message: getApiErrorMessage(err, "Network error") });
    } finally {
      setRefining(false);
    }
  };

  const handleLogout = () => {
    clearToken();
    router.push("/login");
  };

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh", backgroundColor: "var(--surface-canvas)" }}>
        <p style={{ color: "var(--on-surface-variant)", fontSize: "1.05rem" }}>Loading Research Plan Studio...</p>
      </div>
    );
  }

  const tenantName = user?.tenant_id === "tenant-utm-001" 
    ? "Universiti Teknologi Malaysia (UTM)" 
    : "Demo University";

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", backgroundColor: "var(--surface-canvas)" }}>
      {/* Top Navbar */}
      <header className="navbar">
        <div className="container nav-container">
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <Link href="/dashboard" className="btn-secondary" style={{ padding: "0.4rem 0.85rem", fontSize: "0.82rem" }}>
              <ArrowLeft size={14} /> Back to Dashboard
            </Link>
            <div className="logo" style={{ fontSize: "1.15rem" }}>
              <span className="logo-dot"></span>
              ScholarPulse <span style={{ color: "var(--primary)", fontWeight: 800 }}>MTIS</span>
              <span className="logo-badge">Research Plan Studio</span>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.85rem" }}>
            <span className="badge badge-tenant">
              <Building2 size={13} /> {tenantName}
            </span>
            <button onClick={handleLogout} className="btn-secondary" style={{ padding: "0.4rem 0.85rem", fontSize: "0.82rem" }}>
              <LogOut size={14} /> Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Interactive Top Sub-bar adhering to scholarpulse_research_plan */}
      <div style={{ background: "#ffffff", borderBottom: "1px solid var(--border-subtle)", padding: "0.85rem 0", boxShadow: "var(--shadow-sm)" }}>
        <div className="container" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.75rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
            <span style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--outline)", background: "var(--surface-low)", padding: "0.25rem 0.65rem", borderRadius: "6px", fontWeight: 700 }}>
              Stage 05
            </span>
            <span style={{ color: "var(--border-subtle)" }}>/</span>
            <span style={{ fontSize: "0.88rem", color: "var(--on-surface-variant)", fontWeight: 600 }}>
              Objectives, Methodology &amp; Computational Execution
            </span>
            <span style={{ color: "var(--border-subtle)" }}>•</span>
            <span className="badge badge-secondary">
              Plan v{project?.plan_version || plan?.version || 1} • Contract Hardened
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            {!plan && (
              <button
                onClick={handleGeneratePlan}
                disabled={generating}
                className="btn-primary"
                style={{ fontSize: "0.85rem", padding: "0.45rem 0.95rem" }}
              >
                <Sparkles size={14} />
                {generating ? "Synthesizing Plan..." : "Generate Structured Plan"}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Workspace Canvas */}
      <main className="container" style={{ flex: 1, padding: "2rem 1.5rem" }}>
        
        {notification && (
          <div
            style={{
              background: notification.type === "success" ? "var(--secondary-container)" : "var(--error-container)",
              border: `1px solid ${notification.type === "success" ? "#86efac" : "rgba(186, 26, 26, 0.2)"}`,
              borderRadius: "8px",
              padding: "0.85rem 1.25rem",
              marginBottom: "1.5rem",
              color: notification.type === "success" ? "var(--on-secondary-container)" : "var(--on-error-container)",
              display: "flex",
              alignItems: "center",
              gap: "0.6rem",
              fontSize: "0.88rem",
            }}
          >
            {notification.type === "success" ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
            {typeof notification.message === "string" ? notification.message : JSON.stringify(notification.message)}
          </div>
        )}

        {!plan ? (
          <div className="card" style={{ textAlign: "center", padding: "4rem 2rem", maxWidth: "650px", margin: "2rem auto" }}>
            <div style={{ width: "64px", height: "64px", borderRadius: "16px", background: "var(--surface-low)", color: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1.25rem auto" }}>
              <FileText size={32} />
            </div>
            <h2 style={{ fontSize: "1.45rem", fontWeight: 700, color: "var(--on-surface)", marginBottom: "0.5rem" }}>
              No Structured Plan Generated Yet
            </h2>
            <p style={{ color: "var(--on-surface-variant)", fontSize: "0.95rem", lineHeight: 1.6, marginBottom: "1.75rem" }}>
              Transform your literature search, identified research gap, and thesis title into a defensible, multi-objective research execution plan adhering to Malaysian thesis standards.
            </p>
            <button
              onClick={handleGeneratePlan}
              disabled={generating}
              className="btn-primary"
              style={{ margin: "0 auto", padding: "0.75rem 1.75rem", fontSize: "0.95rem" }}
            >
              <Sparkles size={16} />
              {generating ? "Consulting Planning Agent..." : "Generate Research Plan"}
            </button>
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "2.3fr 1fr", gap: "1.75rem", alignItems: "start" }}>
            
            {/* Left Column: Structured Plan Document */}
            <article className="card" style={{ padding: "2.25rem", display: "flex", flexDirection: "column", gap: "2rem" }}>
              
              {/* Document Header Hero */}
              <header style={{ borderBottom: "1px solid var(--border-subtle)", paddingBottom: "1.5rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.6rem", flexWrap: "wrap" }}>
                  <span className="badge badge-primary">Stage 5 Architecture</span>
                  <span className="badge badge-secondary">Plan v{project?.plan_version || plan.version || 1}</span>
                  <span style={{ fontSize: "0.8rem", color: "var(--outline)", fontFamily: "var(--font-code)" }}>ID: {project?.id}</span>
                </div>

                <h1 style={{ fontSize: "1.75rem", fontWeight: 700, color: "var(--on-surface)", lineHeight: 1.3, marginBottom: "0.75rem" }}>
                  {project?.title || "Research Proposal & Methodology Architecture"}
                </h1>

                <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap", fontSize: "0.85rem", color: "var(--on-surface-variant)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
                    <User size={15} color="var(--primary)" />
                    <span>Author: <strong style={{ color: "var(--on-surface)" }}>{user?.email}</strong></span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
                    <GraduationCap size={15} color="var(--secondary)" />
                    <span>Institution: <strong style={{ color: "var(--on-surface)" }}>{tenantName}</strong></span>
                  </div>
                </div>
              </header>

              {/* Research Hypothesis Callout */}
              <div className="coach-card">
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontWeight: 700, marginBottom: "0.4rem" }}>
                  <Lightbulb size={16} /> Central Research Hypothesis &amp; Target
                </div>
                <p style={{ fontSize: "0.88rem", lineHeight: 1.6 }}>
                  {plan.methodology_summary || "Structured investigation addressing candidate literature gaps with defensible empirical evaluations."}
                </p>
              </div>

              {/* Section 1: Research Objectives (§ 01) */}
              <section>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
                  <span style={{ fontFamily: "var(--font-code)", fontSize: "0.78rem", fontWeight: 700, background: "var(--surface-high)", color: "var(--primary)", padding: "0.2rem 0.5rem", borderRadius: "4px" }}>
                    § 01
                  </span>
                  <h2 style={{ fontSize: "1.2rem", fontWeight: 700, color: "var(--on-surface)" }}>
                    Primary Research Objectives
                  </h2>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "0.85rem" }}>
                  {plan.objectives?.map((obj: any, idx: number) => (
                    <div
                      key={idx}
                      style={{
                        background: "#ffffff",
                        border: "1px solid var(--border-subtle)",
                        borderRadius: "10px",
                        padding: "1rem",
                        display: "flex",
                        flexDirection: "column",
                        justifyContent: "space-between"
                      }}
                    >
                      <div>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                          <span className="badge badge-primary">{obj.objective_id || `RO-${idx + 1}`}</span>
                          <CheckCircle2 size={15} color="var(--secondary)" />
                        </div>
                        <p style={{ fontSize: "0.88rem", color: "var(--on-surface)", lineHeight: 1.5 }}>
                          {obj.text}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* Section 2: Key Milestones (§ 02) */}
              <section>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
                  <span style={{ fontFamily: "var(--font-code)", fontSize: "0.78rem", fontWeight: 700, background: "var(--surface-high)", color: "var(--primary)", padding: "0.2rem 0.5rem", borderRadius: "4px" }}>
                    § 02
                  </span>
                  <h2 style={{ fontSize: "1.2rem", fontWeight: 700, color: "var(--on-surface)" }}>
                    Key Deliverable Milestones
                  </h2>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.85rem" }}>
                  {plan.key_milestones?.map((m: any, idx: number) => (
                    <div
                      key={idx}
                      style={{
                        background: "#ffffff",
                        border: "1px solid var(--border-subtle)",
                        borderRadius: "10px",
                        padding: "1rem",
                        display: "flex",
                        flexDirection: "column",
                        justifyContent: "space-between"
                      }}
                    >
                      <div>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.4rem" }}>
                          <span style={{ fontSize: "0.75rem", color: "var(--primary)", fontWeight: 700 }}>
                            {m.milestone_id || `M-${idx + 1}`}
                          </span>
                          <span className="badge badge-primary" style={{ fontSize: "0.68rem" }}>
                            {m.target_month || "Q1"}
                          </span>
                        </div>
                        <h4 style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--on-surface)", marginBottom: "0.3rem" }}>
                          {m.title}
                        </h4>
                        <p style={{ color: "var(--on-surface-variant)", fontSize: "0.84rem", lineHeight: 1.4 }}>
                          {m.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* Section 3: Timeline & Phases (§ 03) */}
              <section>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
                  <span style={{ fontFamily: "var(--font-code)", fontSize: "0.78rem", fontWeight: 700, background: "var(--surface-high)", color: "var(--primary)", padding: "0.2rem 0.5rem", borderRadius: "4px" }}>
                    § 03
                  </span>
                  <h2 style={{ fontSize: "1.2rem", fontWeight: 700, color: "var(--on-surface)" }}>
                    High-Level Timeline &amp; Phases
                  </h2>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                  {plan.timeline?.map((phase: any, idx: number) => (
                    <div
                      key={idx}
                      style={{
                        background: "var(--surface-low)",
                        border: "1px solid var(--border-subtle)",
                        borderLeft: "3px solid var(--primary)",
                        borderRadius: "8px",
                        padding: "1rem",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
                        <h4 style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--on-surface)" }}>{phase.phase_name}</h4>
                        <span className="badge badge-primary">
                          {phase.months}
                        </span>
                      </div>
                      <ul style={{ paddingLeft: "1.25rem", color: "var(--on-surface-variant)", fontSize: "0.84rem" }}>
                        {phase.tasks?.map((t: string, tidx: number) => (
                          <li key={tidx} style={{ marginBottom: "0.2rem" }}>{t}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </section>

              {/* Section 4: Required Resources (§ 04) */}
              <section>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
                  <span style={{ fontFamily: "var(--font-code)", fontSize: "0.78rem", fontWeight: 700, background: "var(--surface-high)", color: "var(--primary)", padding: "0.2rem 0.5rem", borderRadius: "4px" }}>
                    § 04
                  </span>
                  <h2 style={{ fontSize: "1.2rem", fontWeight: 700, color: "var(--on-surface)" }}>
                    Resource Requirements &amp; Feasibility
                  </h2>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
                  {plan.necessary_resources?.map((r: any, idx: number) => (
                    <div key={idx} style={{ background: "#ffffff", padding: "0.85rem", borderRadius: "8px", border: "1px solid var(--border-subtle)" }}>
                      <div style={{ fontSize: "0.72rem", color: "var(--primary)", fontWeight: 700, textTransform: "uppercase" }}>{r.category}</div>
                      <div style={{ fontSize: "0.9rem", fontWeight: 600, color: "var(--on-surface)", margin: "0.2rem 0" }}>{r.item}</div>
                      {r.justification && (
                        <div style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)" }}>{r.justification}</div>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            </article>

            {/* Right Column: Iterative Plan Refinement Panel */}
            <div style={{ position: "sticky", top: "5.5rem" }}>
              <div className="card" style={{ padding: "1.5rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                  <RefreshCw size={18} color="var(--primary)" />
                  <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--on-surface)" }}>
                    Refine with Coach
                  </h3>
                </div>

                <p style={{ color: "var(--on-surface-variant)", fontSize: "0.85rem", marginBottom: "1rem", lineHeight: 1.5 }}>
                  Provide feedback to iterate on objectives, methodology, or resources (e.g. <em>&quot;Focus more on Malaysian SMEs&quot;</em> or <em>&quot;Shorten timeline to 18 months&quot;</em>).
                </p>

                <form onSubmit={handleRefinePlan}>
                  <div style={{ marginBottom: "1rem" }}>
                    <label style={{ display: "block", fontSize: "0.8rem", color: "var(--on-surface-variant)", marginBottom: "0.4rem", fontWeight: 600 }}>
                      FEEDBACK PROMPT
                    </label>
                    <textarea
                      value={refinePrompt}
                      onChange={(e) => setRefinePrompt(e.target.value)}
                      placeholder="e.g. Focus more on Malaysian SMEs and reduce target duration..."
                      rows={4}
                      className="input-control"
                      style={{ resize: "none", fontSize: "0.88rem" }}
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={refining || !refinePrompt.trim()}
                    className="btn-primary"
                    style={{ width: "100%", fontSize: "0.9rem", padding: "0.65rem" }}
                  >
                    <Send size={15} />
                    {refining ? "Applying Refinement..." : "Submit Refinement"}
                  </button>
                </form>

                <div className="coach-card" style={{ marginTop: "1.25rem", padding: "0.85rem" }}>
                  <div style={{ fontWeight: 600, fontSize: "0.82rem", marginBottom: "0.2rem" }}>
                    Version Control Note
                  </div>
                  Refinements generate a clean version increment (Plan v1 → v2) and update the database with zero partial corruption.
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default function PlanPage() {
  return (
    <Suspense fallback={
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
        Loading Plan Studio...
      </div>
    }>
      <PlanViewContent />
    </Suspense>
  );
}
