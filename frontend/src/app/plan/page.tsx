"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { clearToken, fetchWithAuth, getToken } from "@/lib/api";
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
  Calendar
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
          message: err.message || err.detail || "Failed to generate plan.",
        });
      }
    } catch (err: any) {
      setNotification({ type: "error", message: err.message || "Network error" });
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
          message: err.message || err.detail || "Failed to refine plan.",
        });
      }
    } catch (err: any) {
      setNotification({ type: "error", message: err.message || "Network error" });
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
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
        <p style={{ color: "var(--text-muted)", fontSize: "1.1rem" }}>Loading Research Plan View...</p>
      </div>
    );
  }

  const tenantName = user?.tenant_id === "tenant-utm-001" 
    ? "Universiti Teknologi Malaysia (UTM)" 
    : "Demo University";

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Top Navbar */}
      <header className="navbar">
        <div className="container nav-container">
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <Link href="/dashboard" className="btn-secondary" style={{ padding: "0.35rem 0.75rem", fontSize: "0.85rem" }}>
              <ArrowLeft size={14} /> Back to Dashboard
            </Link>
            <div className="logo" style={{ fontSize: "1.1rem" }}>
              <span className="logo-dot"></span>
              Thesis Plan Studio
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <span className="badge badge-tenant">
              <Building2 size={13} /> {tenantName}
            </span>
            <button onClick={handleLogout} className="btn-secondary" style={{ padding: "0.35rem 0.75rem", fontSize: "0.85rem" }}>
              <LogOut size={14} /> Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="container" style={{ flex: 1, padding: "2rem 1.5rem" }}>
        {/* Header Breadcrumb */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem", marginBottom: "1.5rem" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.4rem" }}>
              <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "1.85rem", fontWeight: 700 }}>
                {project ? project.title : "Research Execution Plan"}
              </h1>
              {plan && (
                <span className="badge" style={{ background: "rgba(16, 185, 129, 0.2)", color: "#10b981", border: "1px solid rgba(16, 185, 129, 0.4)", fontWeight: 700 }}>
                  Version {project?.plan_version || plan.version || 1}
                </span>
              )}
            </div>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem" }}>
              Project ID: <code>{project?.id || "N/A"}</code> • Stage 5 Objectives & Methodology
              {project?.last_refined_at && (
                <span style={{ marginLeft: "0.5rem", color: "#38bdf8" }}>
                  • Last Refined: {new Date(project.last_refined_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              )}
            </p>
          </div>

          {!plan && (
            <button
              onClick={handleGeneratePlan}
              disabled={generating}
              className="btn-primary"
              style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
            >
              <Sparkles size={16} />
              {generating ? "Synthesizing Plan..." : "Generate Structured Plan"}
            </button>
          )}
        </div>

        {/* Notification Banner */}
        {notification && (
          <div
            style={{
              background: notification.type === "success" ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)",
              border: `1px solid ${notification.type === "success" ? "rgba(16, 185, 129, 0.4)" : "rgba(239, 68, 68, 0.4)"}`,
              borderRadius: "10px",
              padding: "0.85rem 1.25rem",
              marginBottom: "1.5rem",
              color: notification.type === "success" ? "#a7f3d0" : "#fca5a5",
              display: "flex",
              alignItems: "center",
              gap: "0.75rem",
              fontSize: "0.9rem",
            }}
          >
            {notification.type === "success" ? <CheckCircle2 size={18} /> : <AlertTriangle size={18} />}
            {notification.message}
          </div>
        )}

        {!plan ? (
          <div className="glass-card" style={{ textAlign: "center", padding: "4rem 2rem" }}>
            <FileText size={48} color="var(--primary)" style={{ margin: "0 auto 1rem auto", opacity: 0.8 }} />
            <h2 style={{ fontSize: "1.4rem", fontWeight: 700, marginBottom: "0.5rem" }}>
              No Structured Plan Generated Yet
            </h2>
            <p style={{ color: "var(--text-muted)", maxWidth: "550px", margin: "0 auto 1.5rem auto" }}>
              Transform your literature search, identified research gap, and thesis title into a structured, defense-ready research execution plan.
            </p>
            <button
              onClick={handleGeneratePlan}
              disabled={generating}
              className="btn-primary"
              style={{ margin: "0 auto", display: "inline-flex", alignItems: "center", gap: "0.5rem" }}
            >
              <Sparkles size={16} />
              {generating ? "Consulting AI Research Agent..." : "Generate Plan Now"}
            </button>
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "2rem", alignItems: "start" }}>
            {/* Left: Structured Plan Document */}
            <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
              {/* Objectives Section */}
              <div className="glass-card">
                <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1rem" }}>
                  <Target size={20} color="var(--primary)" />
                  <h2 style={{ fontSize: "1.2rem", fontWeight: 700 }}>1. Research Objectives</h2>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                  {plan.objectives?.map((obj: any, idx: number) => (
                    <div
                      key={idx}
                      style={{
                        background: "rgba(255, 255, 255, 0.03)",
                        border: "1px solid var(--border-subtle)",
                        borderRadius: "8px",
                        padding: "0.85rem 1rem",
                        display: "flex",
                        alignItems: "flex-start",
                        gap: "0.75rem",
                      }}
                    >
                      <span className="badge" style={{ background: "rgba(16, 185, 129, 0.15)", color: "#10b981", fontSize: "0.7rem", marginTop: "0.1rem" }}>
                        {obj.objective_id || `RO-${idx + 1}`}
                      </span>
                      <p style={{ fontSize: "0.95rem", lineHeight: 1.5 }}>{obj.text}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Milestones Section */}
              <div className="glass-card">
                <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1rem" }}>
                  <Milestone size={20} color="#38bdf8" />
                  <h2 style={{ fontSize: "1.2rem", fontWeight: 700 }}>2. Key Deliverable Milestones</h2>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                  {plan.key_milestones?.map((m: any, idx: number) => (
                    <div
                      key={idx}
                      style={{
                        background: "rgba(255, 255, 255, 0.03)",
                        border: "1px solid var(--border-subtle)",
                        borderRadius: "8px",
                        padding: "1rem",
                        display: "flex",
                        flexDirection: "column",
                        justifyContent: "space-between",
                      }}
                    >
                      <div>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.4rem" }}>
                          <span style={{ fontSize: "0.75rem", color: "#38bdf8", fontWeight: 700 }}>
                            {m.milestone_id || `M-${idx + 1}`}
                          </span>
                          <span className="badge" style={{ fontSize: "0.65rem", background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8" }}>
                            {m.target_month || "Q1"}
                          </span>
                        </div>
                        <h4 style={{ fontSize: "0.95rem", fontWeight: 600, marginBottom: "0.3rem" }}>{m.title}</h4>
                        <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", lineHeight: 1.4 }}>{m.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Timeline Phases */}
              <div className="glass-card">
                <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1rem" }}>
                  <Calendar size={20} color="#f59e0b" />
                  <h2 style={{ fontSize: "1.2rem", fontWeight: 700 }}>3. High-Level Timeline & Phases</h2>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
                  {plan.timeline?.map((phase: any, idx: number) => (
                    <div
                      key={idx}
                      style={{
                        background: "rgba(255, 255, 255, 0.03)",
                        borderLeft: "3px solid #f59e0b",
                        borderTop: "1px solid var(--border-subtle)",
                        borderRight: "1px solid var(--border-subtle)",
                        borderBottom: "1px solid var(--border-subtle)",
                        borderRadius: "8px",
                        padding: "1rem",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                        <h4 style={{ fontSize: "1rem", fontWeight: 600 }}>{phase.phase_name}</h4>
                        <span className="badge" style={{ background: "rgba(245, 158, 11, 0.15)", color: "#f59e0b" }}>
                          {phase.months}
                        </span>
                      </div>
                      <ul style={{ paddingLeft: "1.25rem", color: "var(--text-muted)", fontSize: "0.85rem" }}>
                        {phase.tasks?.map((t: string, tidx: number) => (
                          <li key={tidx} style={{ marginBottom: "0.25rem" }}>{t}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              {/* Methodology & Resources */}
              <div className="glass-card">
                <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1rem" }}>
                  <Layers size={20} color="#c084fc" />
                  <h2 style={{ fontSize: "1.2rem", fontWeight: 700 }}>4. Methodology & Necessary Resources</h2>
                </div>

                <div style={{ marginBottom: "1.25rem" }}>
                  <h4 style={{ fontSize: "0.9rem", color: "var(--text-dim)", textTransform: "uppercase", marginBottom: "0.4rem" }}>
                    Methodology Strategy
                  </h4>
                  <p style={{ fontSize: "0.92rem", lineHeight: 1.6, background: "rgba(255, 255, 255, 0.02)", padding: "0.85rem", borderRadius: "8px", border: "1px solid var(--border-subtle)" }}>
                    {plan.methodology_summary || "Structured mixed-method approach tailored to Malaysian institutional guidelines."}
                  </p>
                </div>

                <div>
                  <h4 style={{ fontSize: "0.9rem", color: "var(--text-dim)", textTransform: "uppercase", marginBottom: "0.5rem" }}>
                    Resource Requirements
                  </h4>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
                    {plan.necessary_resources?.map((r: any, idx: number) => (
                      <div key={idx} style={{ background: "rgba(255, 255, 255, 0.03)", padding: "0.75rem", borderRadius: "8px", border: "1px solid var(--border-subtle)" }}>
                        <div style={{ fontSize: "0.75rem", color: "#c084fc", fontWeight: 600 }}>{r.category}</div>
                        <div style={{ fontSize: "0.9rem", fontWeight: 500, margin: "0.2rem 0" }}>{r.item}</div>
                        {r.justification && (
                          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>{r.justification}</div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Right: Iterative Refinement Panel (Requirement 2 & D1) */}
            <div style={{ position: "sticky", top: "1.5rem" }}>
              <div className="glass-card" style={{ border: "1px solid rgba(16, 185, 129, 0.3)", background: "rgba(16, 185, 129, 0.03)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                  <RefreshCw size={18} color="var(--primary)" />
                  <h3 style={{ fontSize: "1.1rem", fontWeight: 700 }}>Iterative Plan Refinement</h3>
                </div>

                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1rem", lineHeight: 1.5 }}>
                  Provide supervisor or student feedback to adapt the objectives, timeline, or resources (e.g. <em>&quot;Focus more on Malaysian SMEs&quot;</em> or <em>&quot;Reduce duration to 18 months&quot;</em>).
                </p>

                <form onSubmit={handleRefinePlan}>
                  <div style={{ marginBottom: "1rem" }}>
                    <label style={{ display: "block", fontSize: "0.8rem", color: "var(--text-dim)", marginBottom: "0.4rem", fontWeight: 600 }}>
                      SUPERVISOR / STUDENT FEEDBACK PROMPT
                    </label>
                    <textarea
                      value={refinePrompt}
                      onChange={(e) => setRefinePrompt(e.target.value)}
                      placeholder="e.g. Too ambitious: narrow down empirical sample to Johor SME manufacturers only, and add qualitative supervisor interview phase."
                      rows={4}
                      style={{
                        width: "100%",
                        background: "rgba(10, 14, 23, 0.8)",
                        border: "1px solid var(--border-subtle)",
                        borderRadius: "8px",
                        color: "var(--text-main)",
                        padding: "0.75rem",
                        fontSize: "0.85rem",
                        fontFamily: "inherit",
                        resize: "vertical",
                        outline: "none",
                      }}
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={refining || !refinePrompt.trim()}
                    className="btn-primary"
                    style={{ width: "100%", display: "flex", justifyContent: "center", alignItems: "center", gap: "0.5rem" }}
                  >
                    <Send size={15} />
                    {refining ? "Refining Plan (v" + ((project?.plan_version || plan?.version || 1) + 1) + ")..." : "Trigger Refinement Loop"}
                  </button>
                </form>

                <div style={{ marginTop: "1.25rem", paddingTop: "1rem", borderTop: "1px solid var(--border-subtle)", fontSize: "0.8rem", color: "var(--text-dim)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.3rem" }}>
                    <span>Active Version:</span>
                    <strong style={{ color: "var(--text-main)" }}>v{project?.plan_version || plan?.version || 1}</strong>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>State Persistence:</span>
                    <span style={{ color: "var(--primary)" }}>Immediate DB Commit (D3)</span>
                  </div>
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
        <p style={{ color: "var(--text-muted)", fontSize: "1.1rem" }}>Loading Research Plan View...</p>
      </div>
    }>
      <PlanViewContent />
    </Suspense>
  );
}
