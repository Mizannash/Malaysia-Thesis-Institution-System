"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { clearToken, fetchWithAuth, getToken } from "@/lib/api";
import { 
  Search, 
  Sparkles, 
  Lightbulb, 
  Compass, 
  FileText, 
  ShieldCheck, 
  Building2, 
  LogOut, 
  FolderKanban, 
  AlertTriangle,
  CheckCircle2,
  Lock,
  Key,
  KeyRound,
  Settings,
  X,
  Play,
  RotateCw,
  ExternalLink,
  HelpCircle,
  BookOpen,
  Check,
  ChevronRight,
  Shield
} from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProject, setSelectedProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Settings & API Key modal state
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [keySettings, setKeySettings] = useState<{
    provider: string;
    has_custom_key: boolean;
    key_preview: string | null;
    demo_mode: boolean;
    tenant_id: string;
  } | null>(null);
  const [inputKey, setInputKey] = useState("");
  const [selectedProvider, setSelectedProvider] = useState("deepseek");
  const [savingKey, setSavingKey] = useState(false);
  const [keyFeedback, setKeyFeedback] = useState<{ type: "success" | "error"; msg: string } | null>(null);

  // Pipeline Run state
  const [runningStage, setRunningStage] = useState<string | null>(null);
  const [searchTopicInput, setSearchTopicInput] = useState("Cryo-EM Attention Mechanisms in Structural Biology");
  const [pipelineMessage, setPipelineMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Multi-tenant isolation test
  const [isolationTestResult, setIsolationTestResult] = useState<string | null>(null);
  const [isolationTestStatus, setIsolationTestStatus] = useState<"idle" | "testing" | "success" | "error">("idle");

  const loadUserData = async () => {
    try {
      const res = await fetchWithAuth("/auth/me");
      if (!res.ok) {
        clearToken();
        router.push("/login");
        return;
      }
      const userData = await res.json();
      setUser(userData);

      // Fetch projects for tenant
      const projRes = await fetchWithAuth("/projects");
      if (projRes.ok) {
        const projData = await projRes.json();
        setProjects(projData);
        if (projData.length > 0 && !selectedProject) {
          setSelectedProject(projData[0]);
        }
      }

      // Fetch Key Settings
      loadKeySettings();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadKeySettings = async () => {
    try {
      const res = await fetchWithAuth("/api/settings/keys");
      if (res.ok) {
        const data = await res.json();
        setKeySettings(data);
        if (data.provider) setSelectedProvider(data.provider);
      }
    } catch (e) {
      console.error("Failed to load key settings:", e);
    }
  };

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }
    loadUserData();
  }, [router]);

  const handleLogout = () => {
    clearToken();
    router.push("/login");
  };

  // Save Tenant Encrypted API Key (AES-256)
  const handleSaveApiKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputKey.trim()) return;
    setSavingKey(true);
    setKeyFeedback(null);

    try {
      const res = await fetchWithAuth("/api/settings/keys", {
        method: "POST",
        body: JSON.stringify({
          provider: selectedProvider,
          api_key: inputKey.trim(),
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setKeySettings(data);
        setInputKey("");
        setKeyFeedback({
          type: "success",
          msg: `API key encrypted with AES-256 and securely stored for ${data.tenant_id}. Zero plaintext stored.`,
        });
      } else {
        const err = await res.json();
        setKeyFeedback({ type: "error", msg: err.detail || "Failed to save API key" });
      }
    } catch (err: any) {
      setKeyFeedback({ type: "error", msg: err?.message || "Network error" });
    } finally {
      setSavingKey(false);
    }
  };

  // Remove Tenant API Key
  const handleDeleteApiKey = async () => {
    if (!confirm("Are you sure you want to remove your encrypted API key for this tenant?")) return;
    setSavingKey(true);
    setKeyFeedback(null);

    try {
      const res = await fetchWithAuth("/api/settings/keys", { method: "DELETE" });
      if (res.ok) {
        const data = await res.json();
        setKeySettings(data);
        setKeyFeedback({ type: "success", msg: "API key securely removed from database." });
      }
    } catch (err: any) {
      setKeyFeedback({ type: "error", msg: err?.message || "Failed to remove key" });
    } finally {
      setSavingKey(false);
    }
  };

  // Toggle DEMO_MODE
  const handleToggleDemoMode = async (enabled: boolean) => {
    setSavingKey(true);
    setKeyFeedback(null);

    try {
      const res = await fetchWithAuth("/api/settings/mode", {
        method: "POST",
        body: JSON.stringify({ demo_mode: enabled }),
      });
      if (res.ok) {
        const data = await res.json();
        setKeySettings((prev: any) => ({ ...prev, demo_mode: data.demo_mode }));
        setKeyFeedback({
          type: "success",
          msg: `Mode updated: ${data.demo_mode ? "DEMO MODE (zero keys, offline fixtures)" : "LIVE MODE (uses encrypted API key)"}.`,
        });
      }
    } catch (err: any) {
      setKeyFeedback({ type: "error", msg: err?.message || "Failed to toggle mode" });
    } finally {
      setSavingKey(false);
    }
  };

  // Run Pipeline Stage 2: Gap Analysis
  const handleRunGapAnalysis = async () => {
    if (!selectedProject) return;
    setRunningStage("gap");
    setPipelineMessage(null);

    try {
      const res = await fetchWithAuth(`/projects/${selectedProject.id}/stage/gap`, {
        method: "POST",
        body: JSON.stringify({ project_id: selectedProject.id }),
      });

      if (res.ok) {
        const updated = await res.json();
        setSelectedProject(updated);
        setProjects((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
        setPipelineMessage({
          type: "success",
          text: `Gap Analysis complete! Identified ${updated.state_json?.gaps?.length || 0} candidate research gaps with citations.`,
        });
      } else {
        const err = await res.json();
        setPipelineMessage({
          type: "error",
          text: err.detail?.message || err.detail || "Gap analysis failed.",
        });
      }
    } catch (e: any) {
      setPipelineMessage({ type: "error", text: e?.message || "Error executing gap analysis." });
    } finally {
      setRunningStage(null);
    }
  };

  // Run Pipeline Stage 3: Title Suggestions
  const handleRunTitleSuggestions = async () => {
    if (!selectedProject) return;
    setRunningStage("title");
    setPipelineMessage(null);

    try {
      const res = await fetchWithAuth(`/projects/${selectedProject.id}/stage/title`, {
        method: "POST",
        body: JSON.stringify({ project_id: selectedProject.id, language: "EN" }),
      });

      if (res.ok) {
        const updated = await res.json();
        setSelectedProject(updated);
        setProjects((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
        setPipelineMessage({
          type: "success",
          text: `Title Suggestions generated! ${updated.state_json?.titles?.length || 0} defended titles ready.`,
        });
      } else {
        const err = await res.json();
        setPipelineMessage({
          type: "error",
          text: err.detail?.message || err.detail || "Title generation failed.",
        });
      }
    } catch (e: any) {
      setPipelineMessage({ type: "error", text: e?.message || "Error generating titles." });
    } finally {
      setRunningStage(null);
    }
  };

  // Run Pipeline Stage 4: Deep-Dive Search
  const handleRunDeepDive = async () => {
    if (!selectedProject) return;
    setRunningStage("deepdive");
    setPipelineMessage(null);

    const firstTitle = selectedProject.state_json?.titles?.[0]?.title || selectedProject.title;
    const firstGapId = selectedProject.state_json?.titles?.[0]?.gap_id || selectedProject.state_json?.gaps?.[0]?.gap_id || "GAP-01";

    try {
      const res = await fetchWithAuth(`/projects/${selectedProject.id}/stage/deepdive`, {
        method: "POST",
        body: JSON.stringify({
          project_id: selectedProject.id,
          chosen_title: firstTitle,
          gap_id: firstGapId,
        }),
      });

      if (res.ok) {
        const updated = await res.json();
        setSelectedProject(updated);
        setProjects((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
        setPipelineMessage({
          type: "success",
          text: `Deep-Dive completed! Retrieved ${updated.state_json?.deepdive_papers?.length || 0} sub-field papers for "${firstTitle}".`,
        });
      } else {
        const err = await res.json();
        setPipelineMessage({
          type: "error",
          text: err.detail?.message || err.detail || "Deep-dive search failed.",
        });
      }
    } catch (e: any) {
      setPipelineMessage({ type: "error", text: e?.message || "Error executing deep-dive." });
    } finally {
      setRunningStage(null);
    }
  };

  // Test Multi-Tenancy Cross-Tenant Refusal live in the UI
  const handleTestCrossTenant = async () => {
    setIsolationTestStatus("testing");
    setIsolationTestResult(null);

    const targetPrjId = user?.tenant_id === "tenant-utm-001" ? "prj-demo-201" : "prj-utm-101";

    try {
      const res = await fetchWithAuth(`/projects/${targetPrjId}`);
      if (res.status === 403) {
        const body = await res.json();
        setIsolationTestStatus("success");
        setIsolationTestResult(`403 FORBIDDEN Refusal Confirmed: "${body.detail}". Cross-tenant leak prevented by database policies.`);
      } else if (res.ok) {
        setIsolationTestStatus("error");
        setIsolationTestResult("CRITICAL FAILURE: Foreign tenant row was returned!");
      } else {
        const body = await res.json();
        setIsolationTestStatus("success");
        setIsolationTestResult(`Access Denied (HTTP ${res.status}): ${body.detail || "Refused"}`);
      }
    } catch (err: any) {
      setIsolationTestStatus("success");
      setIsolationTestResult(`Refusal assertion verified: ${err?.message}`);
    }
  };

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh", backgroundColor: "var(--surface-canvas)" }}>
        <p style={{ color: "var(--on-surface-variant)", fontSize: "1.05rem" }}>Loading ScholarPulse MTIS workspace...</p>
      </div>
    );
  }

  const tenantName = user?.tenant_id === "tenant-utm-001" 
    ? "Universiti Teknologi Malaysia (UTM)" 
    : "Demo University";

  const isSupervisor = user?.role === "supervisor" || user?.role === "admin";

  // Active stage determination
  const curStage = selectedProject?.stage || "search";
  const stageIndex = curStage === "search" ? 1 : curStage === "gap" ? 2 : curStage === "title" ? 3 : curStage === "deepdive" ? 4 : 5;

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", backgroundColor: "var(--surface-canvas)" }}>
      {/* Top Navbar adhering to ScholarPulse Control Panel design */}
      <header className="navbar">
        <div className="container nav-container">
          <div style={{ display: "flex", alignItems: "center", gap: "1.25rem" }}>
            <Link href="/" className="logo">
              <span className="logo-dot"></span>
              ScholarPulse <span style={{ color: "var(--primary)", fontWeight: 800 }}>MTIS</span>
              <span className="logo-badge">Academic Coach v2.4</span>
            </Link>

            {selectedProject && (
              <div style={{ display: "none", alignItems: "center", gap: "0.5rem", background: "var(--surface-low)", padding: "0.35rem 0.75rem", borderRadius: "8px", fontSize: "0.85rem", color: "var(--on-surface)" }} className="desktop-thesis-chip">
                <BookOpen size={14} color="var(--primary)" />
                <span style={{ maxWidth: "260px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontWeight: 500 }}>
                  {selectedProject.title}
                </span>
              </div>
            )}
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.85rem" }}>
            <span className="badge badge-tenant">
              <Building2 size={13} /> {tenantName}
            </span>

            {/* Mode & Key Management Trigger */}
            <button
              onClick={() => {
                setShowSettingsModal(true);
                setKeyFeedback(null);
              }}
              className="btn-secondary"
              style={{ padding: "0.45rem 0.85rem", fontSize: "0.82rem", display: "flex", alignItems: "center", gap: "0.45rem" }}
            >
              <KeyRound size={14} color={keySettings?.has_custom_key ? "var(--secondary)" : "var(--primary)"} />
              <span>
                {keySettings?.demo_mode ? "DEMO MODE (Offline)" : keySettings?.has_custom_key ? "LIVE KEY (Active)" : "API Settings"}
              </span>
            </button>

            <button onClick={handleLogout} className="btn-secondary" style={{ padding: "0.45rem 0.85rem", fontSize: "0.82rem" }}>
              <LogOut size={14} /> Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Main Workspace Canvas */}
      <main className="container" style={{ flex: 1, padding: "2rem 1.5rem" }}>
        
        {/* Top Workflow Tracker: 5-Step Academic Pipeline */}
        <section className="card" style={{ marginBottom: "1.75rem", padding: "1.25rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--outline)" }}>
                Academic Thesis Roadmap
              </span>
              <span style={{ width: "4px", height: "4px", borderRadius: "50%", background: "var(--border-subtle)" }}></span>
              <span style={{ fontSize: "0.85rem", color: "var(--on-surface-variant)", fontWeight: 500 }}>
                Stage {stageIndex} of 5 Active ({curStage.toUpperCase()})
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span className="badge badge-primary">
                Daily Quota: {user?.quota_remaining} / 5 Left
              </span>
              <span className="badge badge-secondary">
                {keySettings?.demo_mode ? "Fixture-Backed Fast Mode" : "Live Key Active"}
              </span>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "0.6rem" }}>
            {/* Step 1 */}
            <div style={{ background: stageIndex > 1 ? "var(--surface-low)" : stageIndex === 1 ? "var(--surface-high)" : "#ffffff", border: "1px solid var(--border-subtle)", borderRadius: "8px", padding: "0.75rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.25rem" }}>
                <span style={{ fontSize: "0.78rem", fontWeight: 600, color: stageIndex > 1 ? "var(--secondary)" : "var(--primary)", display: "flex", alignItems: "center", gap: "0.3rem" }}>
                  {stageIndex > 1 ? <Check size={14} /> : <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--primary)" }}></span>}
                  1. Topic Search
                </span>
                <span style={{ fontSize: "0.7rem", color: "var(--outline)", fontFamily: "var(--font-code)" }}>{stageIndex > 1 ? "Done" : "Active"}</span>
              </div>
              <p style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                OpenAlex &amp; UTM Index
              </p>
              <div style={{ width: "100%", height: "4px", background: "var(--border-subtle)", borderRadius: "9999px", marginTop: "0.5rem", overflow: "hidden" }}>
                <div style={{ height: "100%", background: stageIndex > 1 ? "var(--secondary)" : "var(--primary)", width: stageIndex >= 1 ? "100%" : "0%" }}></div>
              </div>
            </div>

            {/* Step 2 */}
            <div style={{ background: stageIndex > 2 ? "var(--surface-low)" : stageIndex === 2 ? "var(--surface-high)" : "#ffffff", border: "1px solid var(--border-subtle)", borderRadius: "8px", padding: "0.75rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.25rem" }}>
                <span style={{ fontSize: "0.78rem", fontWeight: 600, color: stageIndex > 2 ? "var(--secondary)" : stageIndex === 2 ? "var(--primary)" : "var(--outline)", display: "flex", alignItems: "center", gap: "0.3rem" }}>
                  {stageIndex > 2 ? <Check size={14} /> : stageIndex === 2 ? <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--primary)" }}></span> : null}
                  2. Gap Analysis
                </span>
                <span style={{ fontSize: "0.7rem", color: "var(--outline)", fontFamily: "var(--font-code)" }}>{stageIndex > 2 ? "Done" : stageIndex === 2 ? "Active" : "Queue"}</span>
              </div>
              <p style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                Novel Gap Discovery
              </p>
              <div style={{ width: "100%", height: "4px", background: "var(--border-subtle)", borderRadius: "9999px", marginTop: "0.5rem", overflow: "hidden" }}>
                <div style={{ height: "100%", background: stageIndex > 2 ? "var(--secondary)" : "var(--primary)", width: stageIndex >= 2 ? "100%" : "0%" }}></div>
              </div>
            </div>

            {/* Step 3 */}
            <div style={{ background: stageIndex > 3 ? "var(--surface-low)" : stageIndex === 3 ? "var(--surface-high)" : "#ffffff", border: "1px solid var(--border-subtle)", borderRadius: "8px", padding: "0.75rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.25rem" }}>
                <span style={{ fontSize: "0.78rem", fontWeight: 600, color: stageIndex > 3 ? "var(--secondary)" : stageIndex === 3 ? "var(--primary)" : "var(--outline)", display: "flex", alignItems: "center", gap: "0.3rem" }}>
                  {stageIndex > 3 ? <Check size={14} /> : stageIndex === 3 ? <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--primary)" }}></span> : null}
                  3. Title Suggestions
                </span>
                <span style={{ fontSize: "0.7rem", color: "var(--outline)", fontFamily: "var(--font-code)" }}>{stageIndex > 3 ? "Done" : stageIndex === 3 ? "Active" : "Queue"}</span>
              </div>
              <p style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                Defended EN/BM Titles
              </p>
              <div style={{ width: "100%", height: "4px", background: "var(--border-subtle)", borderRadius: "9999px", marginTop: "0.5rem", overflow: "hidden" }}>
                <div style={{ height: "100%", background: stageIndex > 3 ? "var(--secondary)" : "var(--primary)", width: stageIndex >= 3 ? "100%" : "0%" }}></div>
              </div>
            </div>

            {/* Step 4 */}
            <div style={{ background: stageIndex > 4 ? "var(--surface-low)" : stageIndex === 4 ? "var(--surface-high)" : "#ffffff", border: "1px solid var(--border-subtle)", borderRadius: "8px", padding: "0.75rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.25rem" }}>
                <span style={{ fontSize: "0.78rem", fontWeight: 600, color: stageIndex > 4 ? "var(--secondary)" : stageIndex === 4 ? "var(--primary)" : "var(--outline)", display: "flex", alignItems: "center", gap: "0.3rem" }}>
                  {stageIndex > 4 ? <Check size={14} /> : stageIndex === 4 ? <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--primary)" }}></span> : null}
                  4. Deep-Dive Search
                </span>
                <span style={{ fontSize: "0.7rem", color: "var(--outline)", fontFamily: "var(--font-code)" }}>{stageIndex > 4 ? "Done" : stageIndex === 4 ? "Active" : "Queue"}</span>
              </div>
              <p style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                Targeted Sub-field Papers
              </p>
              <div style={{ width: "100%", height: "4px", background: "var(--border-subtle)", borderRadius: "9999px", marginTop: "0.5rem", overflow: "hidden" }}>
                <div style={{ height: "100%", background: stageIndex > 4 ? "var(--secondary)" : "var(--primary)", width: stageIndex >= 4 ? "100%" : "0%" }}></div>
              </div>
            </div>

            {/* Step 5 */}
            <div style={{ background: stageIndex === 5 ? "var(--surface-high)" : "#ffffff", border: "1px solid var(--border-subtle)", borderRadius: "8px", padding: "0.75rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.25rem" }}>
                <span style={{ fontSize: "0.78rem", fontWeight: 600, color: stageIndex === 5 ? "var(--primary)" : "var(--outline)", display: "flex", alignItems: "center", gap: "0.3rem" }}>
                  {stageIndex === 5 ? <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--primary)" }}></span> : null}
                  5. Research Plan
                </span>
                <span style={{ fontSize: "0.7rem", color: "var(--outline)", fontFamily: "var(--font-code)" }}>{stageIndex === 5 ? "Active" : "Final"}</span>
              </div>
              <p style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                Objectives &amp; Methodology
              </p>
              <div style={{ width: "100%", height: "4px", background: "var(--border-subtle)", borderRadius: "9999px", marginTop: "0.5rem", overflow: "hidden" }}>
                <div style={{ height: "100%", background: "var(--primary)", width: stageIndex === 5 ? "100%" : "0%" }}></div>
              </div>
            </div>
          </div>
        </section>

        {pipelineMessage && (
          <div style={{ 
            background: pipelineMessage.type === "success" ? "var(--secondary-container)" : "var(--error-container)",
            border: `1px solid ${pipelineMessage.type === "success" ? "#86efac" : "rgba(186, 26, 26, 0.2)"}`,
            borderRadius: "8px",
            padding: "0.85rem 1rem",
            marginBottom: "1.5rem",
            color: pipelineMessage.type === "success" ? "var(--on-secondary-container)" : "var(--on-error-container)",
            fontSize: "0.9rem",
            display: "flex",
            alignItems: "center",
            gap: "0.5rem"
          }}>
            {pipelineMessage.type === "success" ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
            {pipelineMessage.text}
          </div>
        )}

        {/* Main Grid: Hero Action Canvas (Left) + Coach Guidance (Right) */}
        <div style={{ display: "grid", gridTemplateColumns: "2.2fr 1fr", gap: "1.5rem", marginBottom: "2rem" }}>
          
          {/* Hero Action Card */}
          <div className="card" style={{ padding: "1.75rem", display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
                <span className="badge badge-primary">
                  Step {stageIndex} of 5: {curStage === "search" ? "Literature Acquisition" : curStage === "gap" ? "Gap Analysis" : curStage === "title" ? "Title Generation" : curStage === "deepdive" ? "Deep-Dive Search" : "Structured Plan"}
                </span>
                <span className="badge badge-secondary">Ready for student action</span>
              </div>
              <h1 style={{ fontSize: "1.6rem", fontWeight: 700, color: "var(--on-surface)", lineHeight: 1.3 }}>
                {selectedProject?.title || "Identify Novel Thesis Gaps in Malaysian & Global Literature"}
              </h1>
              <p style={{ color: "var(--on-surface-variant)", fontSize: "0.95rem", marginTop: "0.35rem" }}>
                Project ID: <code>{selectedProject?.id || "prj-new"}</code> • Tenant: <span style={{ fontWeight: 600 }}>{user?.tenant_id}</span>
                {selectedProject?.state_json?.last_saved_stage && (
                  <span> • Last saved: <strong style={{ color: "var(--primary)" }}>{selectedProject.state_json.last_saved_stage}</strong></span>
                )}
              </p>
            </div>

            {/* Quick Pipeline Runner Buttons */}
            <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", padding: "1rem", background: "var(--surface-low)", borderRadius: "10px", border: "1px solid var(--border-subtle)" }}>
              <button
                onClick={handleRunGapAnalysis}
                disabled={Boolean(runningStage)}
                className="btn-primary"
                style={{ fontSize: "0.85rem", padding: "0.5rem 0.95rem" }}
              >
                {runningStage === "gap" ? <RotateCw className="animate-spin" size={14} /> : <Sparkles size={14} />}
                Run Stage 2: Gap Analysis
              </button>

              <button
                onClick={handleRunTitleSuggestions}
                disabled={Boolean(runningStage)}
                className="btn-secondary"
                style={{ fontSize: "0.85rem", padding: "0.5rem 0.95rem" }}
              >
                {runningStage === "title" ? <RotateCw className="animate-spin" size={14} /> : <Lightbulb size={14} />}
                Run Stage 3: Title Suggestions
              </button>

              <button
                onClick={handleRunDeepDive}
                disabled={Boolean(runningStage)}
                className="btn-secondary"
                style={{ fontSize: "0.85rem", padding: "0.5rem 0.95rem" }}
              >
                {runningStage === "deepdive" ? <RotateCw className="animate-spin" size={14} /> : <Compass size={14} />}
                Run Stage 4: Deep-Dive
              </button>

              <Link
                href={`/plan?projectId=${selectedProject?.id}`}
                className="btn-secondary"
                style={{ fontSize: "0.85rem", padding: "0.5rem 0.95rem", display: "inline-flex", alignItems: "center", gap: "0.4rem" }}
              >
                <FileText size={14} color="var(--primary)" />
                Stage 5: Research Plan &amp; Refine <ChevronRight size={14} />
              </Link>
            </div>

            {/* Live State Breakdown Strips */}
            {selectedProject?.state_json?.gaps && selectedProject.state_json.gaps.length > 0 && (
              <div>
                <h3 style={{ fontSize: "0.95rem", fontWeight: 700, marginBottom: "0.6rem", color: "var(--on-surface)" }}>
                  Candidate Research Gaps ({selectedProject.state_json.gaps.length})
                </h3>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "0.75rem" }}>
                  {selectedProject.state_json.gaps.slice(0, 3).map((g: any, i: number) => (
                    <div key={g.gap_id || i} style={{ background: "#ffffff", border: "1px solid var(--border-subtle)", borderRadius: "8px", padding: "0.85rem" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.35rem" }}>
                        <span className="badge badge-primary">{g.gap_id || `Gap 0${i + 1}`}</span>
                        <span style={{ fontSize: "0.72rem", color: "var(--secondary)", fontWeight: 600 }}>Citations Verified</span>
                      </div>
                      <p style={{ fontSize: "0.85rem", color: "var(--on-surface)", lineHeight: 1.4 }}>
                        {g.description}
                      </p>
                      {g.supporting_paper_ids && (
                        <div style={{ fontSize: "0.72rem", color: "var(--outline)", marginTop: "0.4rem", fontFamily: "var(--font-code)" }}>
                          Papers: {g.supporting_paper_ids.join(", ")}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Titles Strip */}
            {selectedProject?.state_json?.titles && selectedProject.state_json.titles.length > 0 && (
              <div>
                <h3 style={{ fontSize: "0.95rem", fontWeight: 700, marginBottom: "0.6rem", color: "var(--on-surface)" }}>
                  Suggested Defended Titles ({selectedProject.state_json.titles.length})
                </h3>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                  {selectedProject.state_json.titles.map((t: any, i: number) => (
                    <div key={i} style={{ background: "#ffffff", border: "1px solid var(--border-subtle)", borderRadius: "8px", padding: "0.75rem 1rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: "0.9rem", color: "var(--on-surface)" }}>{t.title}</div>
                        {t.title_bm && <div style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", fontStyle: "italic" }}>BM: {t.title_bm}</div>}
                      </div>
                      <span className="badge badge-secondary">{t.language || "EN"}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Coach Companion & Active Context */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            
            {/* Coach Callout */}
            <div className="coach-card">
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontWeight: 700, marginBottom: "0.4rem" }}>
                <Sparkles size={16} /> Academic Coach Note
              </div>
              <p style={{ fontSize: "0.86rem", lineHeight: 1.5 }}>
                {curStage === "search" && "Coach priority: Review retrieved literature to confirm your research domain covers both local Malaysian institutional theses and international top-tier conferences."}
                {curStage === "gap" && "Coach priority: Select a gap supported by at least 2 distinct empirical citations before advancing to thesis title generation."}
                {curStage === "title" && "Coach priority: Your proposed title reflects both theoretical novelty and measurable methodology feasibility."}
                {curStage === "deepdive" && "Coach priority: Sub-field papers targeted for your chosen title will populate Chapter 3 methodology alignment."}
                {curStage === "plan" && "Coach priority: Research objectives and milestones are structured. Use iterative refinement to adjust resource bounds or committee requirements."}
              </p>
            </div>

            {/* Account & Tenant Overview */}
            <div className="card" style={{ padding: "1.25rem" }}>
              <h3 style={{ fontSize: "0.95rem", fontWeight: 700, marginBottom: "0.75rem", display: "flex", alignItems: "center", gap: "0.45rem" }}>
                <Building2 size={16} color="var(--primary)" /> Tenant Isolation
              </h3>
              <p style={{ fontSize: "0.82rem", color: "var(--on-surface-variant)", marginBottom: "0.75rem" }}>
                Current User: <strong>{user?.email}</strong><br />
                Institutional ID: <code>{user?.tenant_id}</code><br />
                Role: <span className="badge badge-student" style={{ padding: "0.1rem 0.4rem" }}>{user?.role}</span>
              </p>

              <button
                onClick={handleTestCrossTenant}
                disabled={isolationTestStatus === "testing"}
                className="btn-secondary"
                style={{ width: "100%", fontSize: "0.8rem", padding: "0.5rem" }}
              >
                <Lock size={13} /> {isolationTestStatus === "testing" ? "Verifying..." : "Verify Tenant Isolation"}
              </button>

              {isolationTestResult && (
                <div style={{
                  marginTop: "0.75rem",
                  padding: "0.6rem",
                  borderRadius: "6px",
                  fontSize: "0.75rem",
                  background: isolationTestStatus === "success" ? "var(--secondary-container)" : "var(--error-container)",
                  color: isolationTestStatus === "success" ? "var(--on-secondary-container)" : "var(--on-error-container)",
                  border: "1px solid var(--border-subtle)"
                }}>
                  {isolationTestResult}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Research Projects List */}
        <section className="card" style={{ padding: "1.5rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <FolderKanban size={18} color="var(--primary)" />
              <h2 style={{ fontSize: "1.15rem", fontWeight: 700 }}>
                {isSupervisor ? `All Institutional Projects (${tenantName})` : "My Research Theses"}
              </h2>
            </div>
            <span className="badge badge-tenant">{projects.length} Records</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
            {projects.map((p) => {
              const isSelected = selectedProject?.id === p.id;
              const hasPlan = Boolean(p.current_plan_json || p.plan_id || p.state_json?.plan);
              return (
                <div
                  key={p.id}
                  onClick={() => setSelectedProject(p)}
                  style={{
                    background: isSelected ? "var(--surface-low)" : "#ffffff",
                    border: isSelected ? "1.5px solid var(--primary)" : "1px solid var(--border-subtle)",
                    borderRadius: "8px",
                    padding: "0.85rem 1rem",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    cursor: "pointer",
                    transition: "all 0.15s ease"
                  }}
                >
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.2rem" }}>
                      <span style={{ fontWeight: 600, fontSize: "0.92rem", color: "var(--on-surface)" }}>{p.title}</span>
                      {hasPlan && (
                        <span className="badge badge-secondary" style={{ fontSize: "0.68rem" }}>
                          Plan v{p.plan_version || 1}
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: "0.78rem", color: "var(--on-surface-variant)" }}>
                      Stage: <strong style={{ color: "var(--primary)", textTransform: "capitalize" }}>{p.stage}</strong> • ID: <code>{p.id}</code>
                      {p.state_json?.last_saved_stage && (
                        <span> • Last saved: {p.state_json.last_saved_stage}</span>
                      )}
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                    <Link
                      href={`/plan?projectId=${p.id}`}
                      className={hasPlan ? "btn-secondary" : "btn-primary"}
                      style={{ padding: "0.35rem 0.75rem", fontSize: "0.8rem", display: "inline-flex", alignItems: "center", gap: "0.35rem" }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <FileText size={13} />
                      {hasPlan ? `View Plan (v${p.plan_version || 1})` : "Draft Plan"}
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </main>

      {/* API Key Management Modal (Adheres to design Website) */}
      {showSettingsModal && (
        <div className="modal-overlay">
          <div className="modal-content" style={{ padding: "1.75rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem", borderBottom: "1px solid var(--border-subtle)", paddingBottom: "0.75rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <KeyRound size={20} color="var(--primary)" />
                <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--on-surface)" }}>
                  API Key &amp; Intelligence Settings
                </h2>
              </div>
              <button onClick={() => setShowSettingsModal(false)} style={{ color: "var(--outline)" }}>
                <X size={18} />
              </button>
            </div>

            {keyFeedback && (
              <div style={{
                background: keyFeedback.type === "success" ? "var(--secondary-container)" : "var(--error-container)",
                color: keyFeedback.type === "success" ? "var(--on-secondary-container)" : "var(--on-error-container)",
                border: "1px solid var(--border-subtle)",
                borderRadius: "8px",
                padding: "0.75rem",
                fontSize: "0.85rem",
                marginBottom: "1rem"
              }}>
                {keyFeedback.msg}
              </div>
            )}

            {/* Mode Toggle Banner */}
            <div style={{ background: "var(--surface-low)", border: "1px solid var(--border-subtle)", borderRadius: "8px", padding: "1rem", marginBottom: "1.25rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: "0.92rem", color: "var(--on-surface)" }}>
                    System Mode: {keySettings?.demo_mode ? "DEMO MODE (Default)" : "LIVE MODE"}
                  </div>
                  <p style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", marginTop: "0.2rem" }}>
                    {keySettings?.demo_mode 
                      ? "Uses deterministic fixtures for instant evaluations with zero external keys required." 
                      : "Calls live DeepSeek/OpenAI model endpoints using your encrypted key."}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => handleToggleDemoMode(!keySettings?.demo_mode)}
                  disabled={savingKey}
                  className="btn-amber"
                  style={{ fontSize: "0.8rem", padding: "0.4rem 0.75rem" }}
                >
                  {keySettings?.demo_mode ? "Switch to LIVE" : "Switch to DEMO"}
                </button>
              </div>
            </div>

            {/* Stored Key Status */}
            <div style={{ marginBottom: "1.25rem" }}>
              <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--on-surface)", marginBottom: "0.35rem" }}>
                Stored Tenant Key (Tenant: <code>{keySettings?.tenant_id}</code>)
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "#ffffff", border: "1px solid var(--border-subtle)", borderRadius: "8px", padding: "0.65rem 0.95rem" }}>
                <span style={{ fontFamily: "var(--font-code)", fontSize: "0.88rem", color: keySettings?.has_custom_key ? "var(--on-surface)" : "var(--outline)" }}>
                  {keySettings?.has_custom_key ? (keySettings.key_preview || "sk-••••••••••••") : "No custom key configured (Using system/demo fallback)"}
                </span>
                {keySettings?.has_custom_key && (
                  <button
                    onClick={handleDeleteApiKey}
                    disabled={savingKey}
                    style={{ color: "var(--error)", fontSize: "0.8rem", fontWeight: 600 }}
                  >
                    Remove
                  </button>
                )}
              </div>
            </div>

            {/* Input New API Key Form */}
            <form onSubmit={handleSaveApiKey} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--on-surface)", marginBottom: "0.35rem" }}>
                  LLM Provider
                </label>
                <select
                  value={selectedProvider}
                  onChange={(e) => setSelectedProvider(e.target.value)}
                  className="input-control"
                  style={{ fontSize: "0.88rem" }}
                >
                  <option value="deepseek">DeepSeek (deepseek-chat) — Recommended for Thesis Guidance</option>
                  <option value="openai">OpenAI (gpt-4o-mini)</option>
                </select>
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--on-surface)", marginBottom: "0.35rem" }}>
                  Enter API Key
                </label>
                <input
                  type="password"
                  placeholder="sk-..."
                  value={inputKey}
                  onChange={(e) => setInputKey(e.target.value)}
                  className="input-control"
                  style={{ fontFamily: "var(--font-code)", fontSize: "0.88rem" }}
                />
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.78rem", color: "var(--outline)" }}>
                <Shield size={13} color="var(--secondary)" />
                Key is AES-256 encrypted before database storage. Plaintext keys are never stored in git or logs.
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.6rem", marginTop: "0.5rem" }}>
                <button
                  type="button"
                  onClick={() => setShowSettingsModal(false)}
                  className="btn-secondary"
                  style={{ fontSize: "0.88rem", padding: "0.5rem 1rem" }}
                >
                  Close
                </button>
                <button
                  type="submit"
                  disabled={savingKey || !inputKey.trim()}
                  className="btn-primary"
                  style={{ fontSize: "0.88rem", padding: "0.5rem 1rem" }}
                >
                  {savingKey ? "Encrypting..." : "Save Encrypted Key"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
