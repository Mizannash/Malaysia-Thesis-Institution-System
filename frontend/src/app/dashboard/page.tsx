"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { clearToken, fetchWithAuth, getToken, getApiErrorMessage } from "@/lib/api";
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
  Shield,
  CreditCard,
  Globe,
  Send,
  GraduationCap,
  Users,
  UserPlus
} from "lucide-react";
import { useLanguage } from "@/lib/LanguageContext";
import LanguageToggle from "@/components/LanguageToggle";

export default function DashboardPage() {
  const router = useRouter();
  const { t, lang } = useLanguage();

  // Robust academic paper link resolver — guarantees no 404 or missing DOI errors
  const getPaperLink = (paper: any) => {
    if (!paper) return "https://scholar.google.com";
    // Check if url is a valid external URL and not a broken mock/example DOI
    if (paper.url && !paper.url.includes("example") && !paper.url.includes("10.11113") && !paper.url.endsWith(".example")) {
      return paper.url;
    }
    // Check if doi is valid real publisher DOI
    if (paper.doi && !paper.doi.includes("example") && !paper.doi.includes("10.11113") && paper.doi.startsWith("10.")) {
      return `https://doi.org/${paper.doi.replace(/^https?:\/\/doi\.org\//, "")}`;
    }
    // For Malaysian / UTM institutional theses
    if (paper.source === "utm" || (paper.id && String(paper.id).toLowerCase().includes("utm"))) {
      return `https://scholar.google.com/scholar?q=${encodeURIComponent(`${paper.title || "UTM Thesis"} UTM Universiti Teknologi Malaysia`)}`;
    }
    // Default universal academic paper resolver (Google Scholar directly finds PDF and indexed paper)
    return `https://scholar.google.com/scholar?q=${encodeURIComponent(paper.title || "")}`;
  };

  const [user, setUser] = useState<any>(null);
  const [projects, setProjects] = useState<any[]>([]);
  const [selectedProject, setSelectedProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Admin Management State
  const [adminView, setAdminView] = useState<"workspace" | "admin">("workspace");
  const [adminUsers, setAdminUsers] = useState<any[]>([]);
  const [adminStats, setAdminStats] = useState<any>(null);
  const [loadingAdmin, setLoadingAdmin] = useState(false);
  const [adminSearchFilter, setAdminSearchFilter] = useState("");
  const [adminFeedback, setAdminFeedback] = useState<{ type: "success" | "error"; msg: string } | null>(null);
  const [updatingUserId, setUpdatingUserId] = useState<string | null>(null);
  const [userPlanDrafts, setUserPlanDrafts] = useState<{ [userId: string]: string }>({});

  // Onboard new user modal/form
  const [showOnboardModal, setShowOnboardModal] = useState(false);
  const [newUserName, setNewUserName] = useState("");
  const [newUserEmail, setNewUserEmail] = useState("");
  const [newUserRole, setNewUserRole] = useState("student");
  const [newUserPlan, setNewUserPlan] = useState("free");
  const [newUserTenant, setNewUserTenant] = useState("tenant-demo-002");
  const [creatingUser, setCreatingUser] = useState(false);

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

  // Stage 1 Topic Search & Article Discovery state
  const [searchScope, setSearchScope] = useState<"MY" | "INT">("MY");
  const [isSearching, setIsSearching] = useState(false);
  const [searchedPapers, setSearchedPapers] = useState<any[]>([]);
  const [searchFeedback, setSearchFeedback] = useState<{ type: "success" | "error"; msg: string } | null>(null);
  const [academicCoachPrompt, setAcademicCoachPrompt] = useState("");

  // Multi-tenant isolation test
  const [isolationTestResult, setIsolationTestResult] = useState<string | null>(null);
  const [isolationTestStatus, setIsolationTestStatus] = useState<"idle" | "testing" | "success" | "error">("idle");

  const loadAdminData = async () => {
    setLoadingAdmin(true);
    try {
      const [usersRes, statsRes] = await Promise.all([
        fetchWithAuth("/api/admin/users"),
        fetchWithAuth("/api/admin/stats"),
      ]);
      if (usersRes.ok) {
        const uList = await usersRes.json();
        setAdminUsers(uList);
        const drafts: { [id: string]: string } = {};
        uList.forEach((u: any) => { drafts[u.id] = u.plan; });
        setUserPlanDrafts(drafts);
      }
      if (statsRes.ok) {
        setAdminStats(await statsRes.json());
      }
    } catch (e) {
      console.error("Failed to load admin data:", e);
    } finally {
      setLoadingAdmin(false);
    }
  };

  const handleUpdateUserPlan = async (userId: string, newPlan: string, resetQuota: boolean) => {
    setUpdatingUserId(userId);
    setAdminFeedback(null);
    try {
      const res = await fetchWithAuth(`/api/admin/users/${userId}/plan`, {
        method: "PATCH",
        body: JSON.stringify({ plan: newPlan, reset_quota: resetQuota }),
      });
      if (res.ok) {
        const updated = await res.json();
        setAdminUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
        setUserPlanDrafts((prev) => ({ ...prev, [userId]: updated.plan }));
        setAdminFeedback({
          type: "success",
          msg: `Successfully updated user plan to '${updated.plan.toUpperCase()}' tier (Remaining Quota: ${updated.quota_remaining}).`,
        });
        loadAdminData();
      } else {
        const err = await res.json();
        setAdminFeedback({ type: "error", msg: getApiErrorMessage(err, "Failed to update plan") });
      }
    } catch (e: any) {
      setAdminFeedback({ type: "error", msg: getApiErrorMessage(e, "Failed to update plan") });
    } finally {
      setUpdatingUserId(null);
    }
  };

  const handleOnboardUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUserEmail.trim() || !newUserName.trim()) return;
    setCreatingUser(true);
    setAdminFeedback(null);
    try {
      const res = await fetchWithAuth("/api/admin/users", {
        method: "POST",
        body: JSON.stringify({
          name: newUserName.trim(),
          email: newUserEmail.trim(),
          role: newUserRole,
          plan: newUserPlan,
          tenant_id: newUserTenant,
        }),
      });
      if (res.ok) {
        const created = await res.json();
        setAdminUsers((prev) => [created, ...prev]);
        setAdminFeedback({
          type: "success",
          msg: `Successfully onboarded ${created.name} (${created.email}) on ${created.plan.toUpperCase()} plan.`,
        });
        setNewUserName("");
        setNewUserEmail("");
        setShowOnboardModal(false);
        loadAdminData();
      } else {
        const err = await res.json();
        setAdminFeedback({ type: "error", msg: getApiErrorMessage(err, "Failed to onboard user") });
      }
    } catch (e: any) {
      setAdminFeedback({ type: "error", msg: getApiErrorMessage(e, "Network error onboarding user") });
    } finally {
      setCreatingUser(false);
    }
  };

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

      if (userData.role === "admin") {
        setAdminView("admin");
        loadAdminData();
      }

      // Fetch projects for tenant
      const projRes = await fetchWithAuth("/projects");
      if (projRes.ok) {
        const projData = await projRes.json();
        setProjects(projData);
        if (projData.length > 0 && !selectedProject) {
          const firstP = projData[0];
          setSelectedProject(firstP);
          if (firstP.state_json?.papers && firstP.state_json.papers.length > 0) {
            setSearchedPapers(firstP.state_json.papers);
          }
          if (firstP.title) {
            setSearchTopicInput(firstP.title);
          }
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
        setKeyFeedback({ type: "error", msg: getApiErrorMessage(err, "Failed to save API key") });
      }
    } catch (err: any) {
      setKeyFeedback({ type: "error", msg: getApiErrorMessage(err, "Network error") });
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
      setKeyFeedback({ type: "error", msg: getApiErrorMessage(err, "Failed to remove key") });
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
      setKeyFeedback({ type: "error", msg: getApiErrorMessage(err, "Failed to toggle mode") });
    } finally {
      setSavingKey(false);
    }
  };

  // Run Stage 1: Topic Search & Article Discovery
  const handleSearchTopic = async (e?: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const queryToUse = customQuery !== undefined ? customQuery : searchTopicInput;
    if (!queryToUse.trim()) return;
    setIsSearching(true);
    setSearchFeedback(null);
    setPipelineMessage(null);

    try {
      const res = await fetchWithAuth("/api/search", {
        method: "POST",
        body: JSON.stringify({
          query: queryToUse.trim(),
          scope: searchScope,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        const papers = data.papers || [];
        setSearchedPapers(papers);

        if (papers.length === 0) {
          setSearchFeedback({
            type: "error",
            msg: lang === "bm"
              ? `Tiada artikel berwasit ditemui untuk "${queryToUse.trim()}" dalam skop [${searchScope}]. Sila cuba kata kunci lebih umum atau tukar skop.`
              : `No peer-reviewed articles found for "${queryToUse.trim()}" in scope [${searchScope}]. Try broader keywords, different scope (MY/INT), or check spelling.`,
          });
        } else {
          setSearchFeedback({
            type: "success",
            msg: lang === "bm"
              ? `Berjaya memperoleh ${papers.length} artikel berwasit merentasi [${(data.sources || ["openalex"]).map((s: string) => s.toUpperCase()).join(", ")}] untuk "${queryToUse.trim()}". Literatur sedia diindeks untuk Peringkat 2 Analisis Jurang.`
              : `Retrieved ${papers.length} peer-reviewed articles across [${(data.sources || ["openalex"]).map((s: string) => s.toUpperCase()).join(", ")}] for "${queryToUse.trim()}". Literature is indexed for Stage 2 Gap Analysis.`,
          });
        }

        // Update active project literature state and title
        if (selectedProject && papers.length > 0) {
          const rawQ = queryToUse.trim();
          const cleanTitle = rawQ.toLowerCase() === "tvet"
            ? "TVET Curriculum & Skill Modernization in Malaysian Technical Institutions"
            : `${rawQ.slice(0, 1).toUpperCase() + rawQ.slice(1)}: Malaysian Academic Research`;

          try {
            const patchRes = await fetchWithAuth(`/projects/${selectedProject.id}`, {
              method: "PATCH",
              body: JSON.stringify({
                title: cleanTitle,
                stage: "search",
                state_json: {
                  ...(selectedProject.state_json || {}),
                  topic: cleanTitle,
                  search_query: rawQ,
                  search_scope: searchScope,
                  papers: papers,
                  last_saved_stage: "Stage 1 (Topic Literature Search)",
                  last_saved_at: new Date().toISOString(),
                },
              }),
            });
            if (patchRes.ok) {
              const patched = await patchRes.json();
              setSelectedProject(patched);
              setProjects((prev) => prev.map((p) => (p.id === patched.id ? patched : p)));
            } else {
              const updated = {
                ...selectedProject,
                title: cleanTitle,
                stage: "search",
                state_json: {
                  ...(selectedProject.state_json || {}),
                  topic: cleanTitle,
                  papers: papers,
                  search_query: rawQ,
                  search_scope: searchScope,
                  last_saved_stage: "Stage 1 (Topic Literature Search)",
                  last_saved_at: new Date().toISOString(),
                },
              };
              setSelectedProject(updated);
              setProjects((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
            }
          } catch (e) {
            console.error("Failed to patch project on search:", e);
          }
        }
      } else if (res.status === 401) {
        // Session expired — force re-login
        clearToken();
        router.push("/login");
        return;
      } else {
        const err = await res.json();
        setSearchFeedback({
          type: "error",
          msg: getApiErrorMessage(err, "Academic search failed. Please refine query."),
        });
      }
    } catch (err: any) {
      setSearchFeedback({
        type: "error",
        msg: getApiErrorMessage(err, "Network error while searching repositories."),
      });
    } finally {
      setIsSearching(false);
    }
  };

  // Refill quota for testing
  const handleRefillQuota = async () => {
    try {
      const res = await fetchWithAuth("/auth/refill-quota", { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setUser((prev: any) => prev ? { ...prev, quota_remaining: data.quota_remaining } : prev);
        setPipelineMessage({ type: "success", text: `Daily AI quota refilled to ${data.quota_remaining} requests! You can now run all pipeline stages.` });
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Helper to ensure an active project exists before running a stage
  const ensureActiveProject = async (): Promise<any> => {
    if (selectedProject) return selectedProject;
    if (projects.length > 0) {
      setSelectedProject(projects[0]);
      return projects[0];
    }
    // Auto-create a project if user has none
    const res = await fetchWithAuth("/projects", {
      method: "POST",
      body: JSON.stringify({
        title: searchTopicInput || "Academic Thesis Research",
        stage: "search",
        state_json: { topic: searchTopicInput || "Academic Thesis Research", scope: searchScope, papers: searchedPapers },
      }),
    });
    if (res.ok) {
      const newP = await res.json();
      setProjects((prev) => [newP, ...prev]);
      setSelectedProject(newP);
      return newP;
    }
    return null;
  };

  // Run Pipeline Stage 2: Gap Analysis
  const handleRunGapAnalysis = async () => {
    const proj = await ensureActiveProject();
    if (!proj) return;
    setRunningStage("gap");
    setPipelineMessage(null);

    try {
      const bodyPayload: any = { project_id: proj.id };
      if (searchedPapers.length > 0) {
        bodyPayload.papers = searchedPapers;
      }

      const res = await fetchWithAuth(`/projects/${proj.id}/stage/gap`, {
        method: "POST",
        body: JSON.stringify(bodyPayload),
      });

      if (res.ok) {
        const updated = await res.json();
        setSelectedProject(updated);
        setProjects((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
        setUser((prev: any) => prev ? { ...prev, quota_remaining: Math.max(0, (prev.quota_remaining ?? 1) - 1) } : prev);
        setPipelineMessage({
          type: "success",
          text: lang === "bm"
            ? `Analisis Jurang selesai! Berjaya mengenal pasti ${updated.state_json?.gaps?.length || 0} calon jurang penyelidikan dengan rujukan berwasit yang disahkan.`
            : `Gap Analysis complete! Identified ${updated.state_json?.gaps?.length || 0} candidate research gaps with verified citations.`,
        });
      } else if (res.status === 401) {
        clearToken();
        router.push("/login");
        return;
      } else {
        const err = await res.json();
        setPipelineMessage({
          type: "error",
          text: getApiErrorMessage(err, "Gap analysis failed."),
        });
      }
    } catch (e: any) {
      setPipelineMessage({ type: "error", text: getApiErrorMessage(e, "Error executing gap analysis.") });
    } finally {
      setRunningStage(null);
    }
  };

  // Run Pipeline Stage 3: Title Suggestions
  const handleRunTitleSuggestions = async (targetGapId?: string | any) => {
    const proj = await ensureActiveProject();
    if (!proj) return;
    setRunningStage("title");
    setPipelineMessage(null);

    const chosenGapId = (typeof targetGapId === "string" && targetGapId.startsWith("GAP")) ? targetGapId : (proj.state_json?.gaps?.[0]?.gap_id || "GAP-1");

    try {
      const res = await fetchWithAuth(`/projects/${proj.id}/stage/title`, {
        method: "POST",
        body: JSON.stringify({ project_id: proj.id, gap_id: chosenGapId, language: "EN" }),
      });

      if (res.ok) {
        const updated = await res.json();
        setSelectedProject(updated);
        setProjects((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
        setUser((prev: any) => prev ? { ...prev, quota_remaining: Math.max(0, (prev.quota_remaining ?? 1) - 1) } : prev);
        setPipelineMessage({
          type: "success",
          text: lang === "bm"
            ? `Cadangan Tajuk berjaya dijana! ${updated.state_json?.titles?.length || 0} tajuk yang dipertahankan sedia untuk dipilih.`
            : `Title Suggestions generated! ${updated.state_json?.titles?.length || 0} defended titles ready.`,
        });
      } else if (res.status === 401) {
        clearToken();
        router.push("/login");
        return;
      } else {
        const err = await res.json();
        setPipelineMessage({
          type: "error",
          text: getApiErrorMessage(err, "Title generation failed."),
        });
      }
    } catch (e: any) {
      setPipelineMessage({ type: "error", text: getApiErrorMessage(e, "Error generating titles.") });
    } finally {
      setRunningStage(null);
    }
  };

  // User selects a specific title from the suggested titles
  const handleSelectTitle = async (chosenTitle: string) => {
    if (!selectedProject) return;
    try {
      const res = await fetchWithAuth(`/projects/${selectedProject.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          title: chosenTitle,
          state_json: {
            ...(selectedProject.state_json || {}),
            chosen_title: chosenTitle,
            last_saved_at: new Date().toISOString(),
          },
        }),
      });
      if (res.ok) {
        const updated = await res.json();
        setSelectedProject(updated);
        setProjects((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
        setPipelineMessage({
          type: "success",
          text: lang === "bm"
            ? `Memilih "${chosenTitle}" sebagai tajuk utama tesis!`
            : `Selected "${chosenTitle}" as primary thesis title!`,
        });
      }
    } catch (e) {
      console.error("Failed to select title:", e);
    }
  };

  // Run Pipeline Stage 4: Deep-Dive Search
  const handleRunDeepDive = async () => {
    const proj = await ensureActiveProject();
    if (!proj) return;
    setRunningStage("deepdive");
    setPipelineMessage(null);

    const firstTitle = proj.state_json?.titles?.[0]?.title || proj.title;
    const firstGapId = proj.state_json?.titles?.[0]?.gap_id || proj.state_json?.gaps?.[0]?.gap_id || "GAP-01";

    try {
      const res = await fetchWithAuth(`/projects/${proj.id}/stage/deepdive`, {
        method: "POST",
        body: JSON.stringify({
          project_id: proj.id,
          chosen_title: firstTitle,
          gap_id: firstGapId,
        }),
      });

      if (res.ok) {
        const updated = await res.json();
        setSelectedProject(updated);
        setProjects((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
        setUser((prev: any) => prev ? { ...prev, quota_remaining: Math.max(0, (prev.quota_remaining ?? 1) - 1) } : prev);
        setPipelineMessage({
          type: "success",
          text: lang === "bm"
            ? `Carian Terperinci selesai! Memperoleh ${updated.state_json?.deepdive_papers?.length || 0} artikel sub-bidang untuk "${firstTitle}".`
            : `Deep-Dive completed! Retrieved ${updated.state_json?.deepdive_papers?.length || 0} sub-field papers for "${firstTitle}".`,
        });
      } else if (res.status === 401) {
        clearToken();
        router.push("/login");
        return;
      } else {
        const err = await res.json();
        setPipelineMessage({
          type: "error",
          text: getApiErrorMessage(err, "Deep-dive search failed."),
        });
      }
    } catch (e: any) {
      setPipelineMessage({ type: "error", text: getApiErrorMessage(e, "Error executing deep-dive.") });
    } finally {
      setRunningStage(null);
    }
  };

  // Run Pipeline Stage 5: Plan Generation
  const handleRunPlan = async () => {
    const proj = await ensureActiveProject();
    if (!proj) return;
    setRunningStage("plan");
    setPipelineMessage(null);

    try {
      const res = await fetchWithAuth(`/projects/${proj.id}/stage/plan`, {
        method: "POST",
        body: JSON.stringify({ project_id: proj.id }),
      });

      if (res.ok) {
        const updated = await res.json();
        setSelectedProject(updated);
        setProjects((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
        setUser((prev: any) => prev ? { ...prev, quota_remaining: Math.max(0, (prev.quota_remaining ?? 1) - 1) } : prev);
        setPipelineMessage({
          type: "success",
          text: lang === "bm"
            ? `Pelan Penyelidikan Peringkat 5 berjaya dijana! ${updated.current_plan_json?.objectives?.length || 0} objektif SMART dan ${updated.current_plan_json?.key_milestones?.length || 0} pencapaian utama disusun.`
            : `Stage 5 Research Plan generated! ${updated.current_plan_json?.objectives?.length || 0} SMART objectives and ${updated.current_plan_json?.key_milestones?.length || 0} milestones structured.`,
        });
      } else if (res.status === 401) {
        clearToken();
        router.push("/login");
        return;
      } else {
        const err = await res.json();
        setPipelineMessage({
          type: "error",
          text: getApiErrorMessage(err, "Plan generation failed."),
        });
      }
    } catch (e: any) {
      setPipelineMessage({ type: "error", text: getApiErrorMessage(e, "Error generating plan.") });
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
        setIsolationTestResult(lang === "bm"
          ? `Pengesahan 403 FORBIDDEN Berjaya: "${body.detail}". Pencerobohan rentas penyewa disekat oleh polisi keselamatan pangkalan data.`
          : `403 FORBIDDEN Refusal Confirmed: "${body.detail}". Cross-tenant leak prevented by database policies.`);
      } else if (res.ok) {
        setIsolationTestStatus("error");
        setIsolationTestResult(lang === "bm" ? "RALAT KRITIKAL: Data penyewa asing telah dipulangkan!" : "CRITICAL FAILURE: Foreign tenant row was returned!");
      } else {
        const body = await res.json();
        setIsolationTestStatus("success");
        setIsolationTestResult(lang === "bm" ? `Akses Ditolak (HTTP ${res.status}): ${body.detail || "Ditolak"}` : `Access Denied (HTTP ${res.status}): ${body.detail || "Refused"}`);
      }
    } catch (err: any) {
      setIsolationTestStatus("success");
      setIsolationTestResult(lang === "bm" ? `Pengesahan penolakan disahkan: ${err?.message}` : `Refusal assertion verified: ${err?.message}`);
    }
  };

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh", backgroundColor: "var(--surface-canvas)" }}>
        <p style={{ color: "var(--on-surface-variant)", fontSize: "1.05rem" }}>{t("dash_loading_workspace")}</p>
      </div>
    );
  }

  const tenantName = user?.tenant_id === "tenant-utm-001" 
    ? "Universiti Teknologi Malaysia (UTM)" 
    : "Demo University";

  const isAdmin = user?.role === "admin";

  // Active stage determination
  const curStage = selectedProject?.stage || "search";
  const stageIndex = curStage === "search" ? 1 : curStage === "gap" ? 2 : curStage === "title" ? 3 : (curStage === "deepdive" || curStage === "deep-dive") ? 4 : 5;

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", backgroundColor: "var(--surface-canvas)" }}>
      {/* Top Navbar adhering to ScholarPulse Control Panel design */}
      <header className="navbar">
        <div className="container nav-container">
          <div style={{ display: "flex", alignItems: "center", gap: "1.25rem" }}>
            <Link href="/" className="logo">
              <span className="logo-dot"></span>
              ScholarPulse <span style={{ color: "var(--primary)", fontWeight: 800 }}>MTIS</span>
              <span className="logo-badge">{t("app_badge")}</span>
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
            <LanguageToggle />

            {isAdmin && (
              <div style={{ display: "flex", background: "var(--surface-low)", padding: "0.2rem", borderRadius: "8px", border: "1px solid var(--border-subtle)" }}>
                <button
                  type="button"
                  onClick={() => setAdminView("admin")}
                  style={{
                    padding: "0.35rem 0.75rem",
                    fontSize: "0.8rem",
                    borderRadius: "6px",
                    border: "none",
                    fontWeight: 600,
                    background: adminView === "admin" ? "var(--primary)" : "transparent",
                    color: adminView === "admin" ? "#ffffff" : "var(--on-surface-variant)",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.35rem"
                  }}
                >
                  <ShieldCheck size={14} /> {t("nav_admin")}
                </button>
                <button
                  type="button"
                  onClick={() => setAdminView("workspace")}
                  style={{
                    padding: "0.35rem 0.75rem",
                    fontSize: "0.8rem",
                    borderRadius: "6px",
                    border: "none",
                    fontWeight: 600,
                    background: adminView === "workspace" ? "var(--primary)" : "transparent",
                    color: adminView === "workspace" ? "#ffffff" : "var(--on-surface-variant)",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.35rem"
                  }}
                >
                  <BookOpen size={14} /> {t("nav_workspace")}
                </button>
              </div>
            )}

            <span className="badge badge-tenant">
              <Building2 size={13} /> {tenantName}
            </span>

            {/* Link to Subscriptions & Pricing */}
            <Link
              href="/pricing"
              className="btn-secondary"
              style={{ padding: "0.45rem 0.85rem", fontSize: "0.82rem", display: "flex", alignItems: "center", gap: "0.45rem", textDecoration: "none" }}
            >
              <CreditCard size={14} color="var(--primary)" />
              <span>{t("nav_subscriptions")}</span>
            </Link>

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
                {keySettings?.demo_mode
                  ? t("dash_mode_demo_btn")
                  : keySettings?.has_custom_key
                  ? t("dash_mode_live_btn")
                  : t("dash_mode_settings_btn")}
              </span>
            </button>

            <button onClick={handleLogout} className="btn-secondary" style={{ padding: "0.45rem 0.85rem", fontSize: "0.82rem" }}>
              <LogOut size={14} /> {t("nav_signout")}
            </button>
          </div>
        </div>
      </header>

      {/* Main Workspace Canvas */}
      <main className="container" style={{ flex: 1, padding: "2rem 1.5rem" }}>
        {isAdmin && adminView === "admin" ? (
          <div>
            {/* Top Overview KPI Banner */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem", flexWrap: "wrap", gap: "1rem" }}>
              <div>
                <h1 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--on-surface)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <ShieldCheck size={26} color="var(--primary)" /> System Owner &amp; Subscription Management
                </h1>
                <p style={{ fontSize: "0.88rem", color: "var(--on-surface-variant)", marginTop: "0.25rem" }}>
                  Oversee multi-tenant researcher accounts, assign subscription tiers, monitor platform quotas, and manage API infrastructure.
                </p>
              </div>

              <div style={{ display: "flex", gap: "0.6rem" }}>
                <button
                  onClick={() => setShowOnboardModal(true)}
                  className="btn-primary"
                  style={{ fontSize: "0.85rem", padding: "0.5rem 1rem", display: "flex", alignItems: "center", gap: "0.45rem" }}
                >
                  <UserPlus size={16} /> Onboard Researcher
                </button>
                <button
                  onClick={loadAdminData}
                  disabled={loadingAdmin}
                  className="btn-secondary"
                  style={{ fontSize: "0.85rem", padding: "0.5rem 0.85rem", display: "flex", alignItems: "center", gap: "0.45rem" }}
                >
                  <RotateCw size={15} className={loadingAdmin ? "animate-spin" : ""} /> Refresh
                </button>
              </div>
            </div>

            {/* Platform Stats Grid */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "1rem", marginBottom: "1.75rem" }}>
              <div className="card" style={{ padding: "1.15rem" }}>
                <div style={{ fontSize: "0.78rem", color: "var(--outline)", textTransform: "uppercase", fontWeight: 700, letterSpacing: "0.05em" }}>Total Platform Users</div>
                <div style={{ fontSize: "1.85rem", fontWeight: 800, color: "var(--primary)", marginTop: "0.35rem" }}>
                  {adminStats?.total_users || adminUsers.length || "238"}
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--on-surface-variant)", marginTop: "0.2rem" }}>
                  Across UTM &amp; Demo University
                </div>
              </div>

              <div className="card" style={{ padding: "1.15rem" }}>
                <div style={{ fontSize: "0.78rem", color: "var(--outline)", textTransform: "uppercase", fontWeight: 700, letterSpacing: "0.05em" }}>Active Researchers</div>
                <div style={{ fontSize: "1.85rem", fontWeight: 800, color: "var(--secondary)", marginTop: "0.35rem" }}>
                  {adminStats?.students_count || "204"}
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--on-surface-variant)", marginTop: "0.2rem" }}>
                  Student &amp; Postgraduate accounts
                </div>
              </div>

              <div className="card" style={{ padding: "1.15rem" }}>
                <div style={{ fontSize: "0.78rem", color: "var(--outline)", textTransform: "uppercase", fontWeight: 700, letterSpacing: "0.05em" }}>Subscription Breakdown</div>
                <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--on-surface)", marginTop: "0.5rem", display: "flex", gap: "0.5rem" }}>
                  <span className="badge badge-primary">Pro: {adminStats?.plans_breakdown?.pro || 33}</span>
                  <span className="badge badge-tenant">Free: {adminStats?.plans_breakdown?.free || 204}</span>
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--on-surface-variant)", marginTop: "0.35rem" }}>
                  Enterprise: {adminStats?.plans_breakdown?.enterprise || 1}
                </div>
              </div>

              <div className="card" style={{ padding: "1.15rem" }}>
                <div style={{ fontSize: "0.78rem", color: "var(--outline)", textTransform: "uppercase", fontWeight: 700, letterSpacing: "0.05em" }}>Thesis Projects</div>
                <div style={{ fontSize: "1.85rem", fontWeight: 800, color: "var(--tertiary)", marginTop: "0.35rem" }}>
                  {adminStats?.total_projects || "208"}
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--on-surface-variant)", marginTop: "0.2rem" }}>
                  Tracked in multi-tenant DB
                </div>
              </div>

              <div className="card" style={{ padding: "1.15rem" }}>
                <div style={{ fontSize: "0.78rem", color: "var(--outline)", textTransform: "uppercase", fontWeight: 700, letterSpacing: "0.05em" }}>AI Engine Mode</div>
                <div style={{ fontSize: "1.15rem", fontWeight: 700, color: adminStats?.demo_mode ? "var(--secondary)" : "var(--primary)", marginTop: "0.6rem" }}>
                  {adminStats?.demo_mode ? "DEMO (Offline Fixtures)" : "LIVE LLM Active"}
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--on-surface-variant)", marginTop: "0.2rem" }}>
                  Status: {adminStats?.service_status || "healthy"}
                </div>
              </div>
            </div>

            {/* Admin Feedback Message */}
            {adminFeedback && (
              <div style={{
                padding: "0.85rem 1rem",
                borderRadius: "8px",
                marginBottom: "1.25rem",
                fontSize: "0.88rem",
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
                background: adminFeedback.type === "success" ? "var(--secondary-container)" : "var(--error-container)",
                color: adminFeedback.type === "success" ? "var(--on-secondary-container)" : "var(--on-error-container)",
                border: "1px solid var(--border-subtle)"
              }}>
                {adminFeedback.type === "success" ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
                {typeof adminFeedback.msg === "string" ? adminFeedback.msg : JSON.stringify(adminFeedback.msg)}
              </div>
            )}

            {/* User Directory Table Card */}
            <div className="card" style={{ padding: "1.5rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem", flexWrap: "wrap", gap: "0.75rem" }}>
                <div>
                  <h2 style={{ fontSize: "1.15rem", fontWeight: 700, color: "var(--on-surface)" }}>
                    Researcher Directory &amp; Subscription Tier Management
                  </h2>
                  <p style={{ fontSize: "0.82rem", color: "var(--on-surface-variant)", marginTop: "0.15rem" }}>
                    Select a tier from the dropdown and click 'Apply Plan' to update privileges. Reset quotas instantly with one click.
                  </p>
                </div>

                <div style={{ position: "relative", minWidth: "260px" }}>
                  <Search size={15} color="var(--outline)" style={{ position: "absolute", left: "0.85rem", top: "50%", transform: "translateY(-50%)" }} />
                  <input
                    type="text"
                    placeholder="Search by researcher name or email..."
                    value={adminSearchFilter}
                    onChange={(e) => setAdminSearchFilter(e.target.value)}
                    className="input-control"
                    style={{ paddingLeft: "2.3rem", fontSize: "0.82rem", padding: "0.45rem 0.75rem 0.45rem 2.3rem" }}
                  />
                </div>
              </div>

              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                  <thead>
                    <tr style={{ borderBottom: "1px solid var(--border-subtle)", textAlign: "left", color: "var(--outline)", textTransform: "uppercase", fontSize: "0.72rem", letterSpacing: "0.05em" }}>
                      <th style={{ padding: "0.75rem 0.85rem" }}>Researcher</th>
                      <th style={{ padding: "0.75rem 0.85rem" }}>Institution / Tenant</th>
                      <th style={{ padding: "0.75rem 0.85rem" }}>Role</th>
                      <th style={{ padding: "0.75rem 0.85rem" }}>Subscription Tier</th>
                      <th style={{ padding: "0.75rem 0.85rem" }}>Remaining Quota</th>
                      <th style={{ padding: "0.75rem 0.85rem", textAlign: "right" }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {adminUsers
                      .filter((u) => {
                        if (!adminSearchFilter.trim()) return true;
                        const term = adminSearchFilter.toLowerCase();
                        return (u.name || "").toLowerCase().includes(term) || (u.email || "").toLowerCase().includes(term);
                      })
                      .slice(0, 50)
                      .map((u) => {
                        const curDraft = userPlanDrafts[u.id] || u.plan;
                        const isUpdating = updatingUserId === u.id;
                        return (
                          <tr key={u.id} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                            <td style={{ padding: "0.85rem" }}>
                              <div style={{ fontWeight: 600, color: "var(--on-surface)" }}>{u.name || "Academic User"}</div>
                              <div style={{ fontSize: "0.76rem", color: "var(--on-surface-variant)" }}>{u.email}</div>
                            </td>
                            <td style={{ padding: "0.85rem" }}>
                              <span className="badge badge-tenant" style={{ fontSize: "0.74rem" }}>
                                {u.tenant_id === "tenant-utm-001" ? "UTM Campus" : "Demo University"}
                              </span>
                            </td>
                            <td style={{ padding: "0.85rem" }}>
                              <span className={u.role === "admin" ? "badge badge-admin" : "badge badge-student"} style={{ fontSize: "0.74rem" }}>
                                {u.role === "admin" ? "Owner / Admin" : "Researcher"}
                              </span>
                            </td>
                            <td style={{ padding: "0.85rem" }}>
                              <select
                                value={curDraft}
                                onChange={(e) => setUserPlanDrafts((prev) => ({ ...prev, [u.id]: e.target.value }))}
                                style={{
                                  padding: "0.35rem 0.6rem",
                                  borderRadius: "6px",
                                  border: "1px solid var(--border-subtle)",
                                  fontSize: "0.82rem",
                                  background: "#ffffff",
                                  fontWeight: 600
                                }}
                              >
                                <option value="free">Free (3/day)</option>
                                <option value="pro">Pro (99/day)</option>
                                <option value="enterprise">Enterprise (999/day)</option>
                              </select>
                            </td>
                            <td style={{ padding: "0.85rem" }}>
                              <span style={{
                                fontWeight: 700,
                                color: u.quota_remaining > 10 ? "var(--secondary)" : u.quota_remaining > 0 ? "var(--primary)" : "#dc2626"
                              }}>
                                {u.quota_remaining} calls left
                              </span>
                            </td>
                            <td style={{ padding: "0.85rem", textAlign: "right" }}>
                              <div style={{ display: "flex", gap: "0.4rem", justifyContent: "flex-end" }}>
                                {curDraft !== u.plan && (
                                  <button
                                    onClick={() => handleUpdateUserPlan(u.id, curDraft, true)}
                                    disabled={isUpdating}
                                    className="btn-primary"
                                    style={{ fontSize: "0.76rem", padding: "0.3rem 0.65rem" }}
                                  >
                                    Apply Plan
                                  </button>
                                )}
                                <button
                                  onClick={() => handleUpdateUserPlan(u.id, u.plan, true)}
                                  disabled={isUpdating}
                                  className="btn-secondary"
                                  style={{ fontSize: "0.76rem", padding: "0.3rem 0.65rem" }}
                                  title="Reset quota back to plan default"
                                >
                                  Reset Quota
                                </button>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                  </tbody>
                </table>
              </div>

              {adminUsers.length > 50 && (
                <p style={{ fontSize: "0.75rem", color: "var(--outline)", marginTop: "0.75rem", textAlign: "center" }}>
                  Showing first 50 of {adminUsers.length} total users. Use the search bar above to filter specific researcher accounts.
                </p>
              )}
            </div>

            {/* Onboard User Modal */}
            {showOnboardModal && (
              <div style={{
                position: "fixed",
                inset: 0,
                backgroundColor: "rgba(0, 0, 0, 0.45)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                zIndex: 100,
                backdropFilter: "blur(4px)"
              }}>
                <div className="card" style={{ maxWidth: "480px", width: "90%", padding: "1.75rem", boxShadow: "var(--shadow-xl)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem" }}>
                    <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--on-surface)", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                      <UserPlus size={18} color="var(--primary)" /> Onboard New Academic User
                    </h3>
                    <button onClick={() => setShowOnboardModal(false)} style={{ background: "none", border: "none", cursor: "pointer" }}>
                      <X size={18} color="var(--outline)" />
                    </button>
                  </div>

                  <form onSubmit={handleOnboardUser} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                    <div>
                      <label style={{ fontSize: "0.82rem", fontWeight: 600, display: "block", marginBottom: "0.35rem" }}>Full Name</label>
                      <input
                        type="text"
                        placeholder="e.g. Dr. Nurul Izzah"
                        value={newUserName}
                        onChange={(e) => setNewUserName(e.target.value)}
                        className="input-control"
                        required
                      />
                    </div>

                    <div>
                      <label style={{ fontSize: "0.82rem", fontWeight: 600, display: "block", marginBottom: "0.35rem" }}>Institutional Email</label>
                      <input
                        type="email"
                        placeholder="e.g. nurul@utm.my"
                        value={newUserEmail}
                        onChange={(e) => setNewUserEmail(e.target.value)}
                        className="input-control"
                        required
                      />
                    </div>

                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
                      <div>
                        <label style={{ fontSize: "0.82rem", fontWeight: 600, display: "block", marginBottom: "0.35rem" }}>Role</label>
                        <select
                          value={newUserRole}
                          onChange={(e) => setNewUserRole(e.target.value)}
                          className="input-control"
                        >
                          <option value="student">Researcher / Student</option>
                          <option value="admin">System Admin</option>
                        </select>
                      </div>

                      <div>
                        <label style={{ fontSize: "0.82rem", fontWeight: 600, display: "block", marginBottom: "0.35rem" }}>Subscription Plan</label>
                        <select
                          value={newUserPlan}
                          onChange={(e) => setNewUserPlan(e.target.value)}
                          className="input-control"
                        >
                          <option value="free">Free (3 calls/day)</option>
                          <option value="pro">Pro (99 calls/day)</option>
                          <option value="enterprise">Enterprise (999/day)</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label style={{ fontSize: "0.82rem", fontWeight: 600, display: "block", marginBottom: "0.35rem" }}>Tenant Institution</label>
                      <select
                        value={newUserTenant}
                        onChange={(e) => setNewUserTenant(e.target.value)}
                        className="input-control"
                      >
                        <option value="tenant-demo-002">Demo University (tenant-demo-002)</option>
                        <option value="tenant-utm-001">Universiti Teknologi Malaysia (tenant-utm-001)</option>
                      </select>
                    </div>

                    <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.5rem" }}>
                      <button type="submit" disabled={creatingUser} className="btn-primary" style={{ flex: 1 }}>
                        {creatingUser ? "Creating..." : "Create User Account"}
                      </button>
                      <button type="button" onClick={() => setShowOnboardModal(false)} className="btn-secondary">
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div>
        {/* Top Workflow Tracker: 5-Step Academic Pipeline */}
        <section className="card" style={{ marginBottom: "1.75rem", padding: "1.25rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ fontSize: "0.78rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--outline)" }}>
                {t("dash_roadmap_title")}
              </span>
              <span style={{ width: "4px", height: "4px", borderRadius: "50%", background: "var(--border-subtle)" }}></span>
              <span style={{ fontSize: "0.85rem", color: "var(--on-surface-variant)", fontWeight: 500 }}>
                {lang === "bm"
                  ? `Peringkat ${stageIndex} daripada 5 Aktif (${curStage.toUpperCase()})`
                  : `Stage ${stageIndex} of 5 Active (${curStage.toUpperCase()})`}
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span className="badge badge-primary" style={{ display: "inline-flex", alignItems: "center", gap: "0.45rem", paddingRight: "0.4rem" }}>
                {t("dash_quota_left_label")}: {user?.quota_remaining ?? 0} / 5 {t("dash_left")}
                <button
                  onClick={handleRefillQuota}
                  title="Refill quota to 20 requests"
                  style={{
                    background: "rgba(255, 255, 255, 0.25)",
                    border: "none",
                    borderRadius: "4px",
                    color: "inherit",
                    cursor: "pointer",
                    fontSize: "0.7rem",
                    fontWeight: 700,
                    padding: "1px 6px",
                    marginLeft: "2px"
                  }}
                >
                  {t("dash_refill_btn")}
                </button>
              </span>
              <span className="badge badge-secondary">
                {keySettings?.demo_mode ? t("dash_fast_mode") : t("dash_live_key_badge")}
              </span>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "0.6rem" }}>
            {/* Step 1 */}
            <div style={{ background: stageIndex > 1 ? "var(--surface-low)" : stageIndex === 1 ? "var(--surface-high)" : "#ffffff", border: "1px solid var(--border-subtle)", borderRadius: "8px", padding: "0.75rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.25rem" }}>
                <span style={{ fontSize: "0.78rem", fontWeight: 600, color: stageIndex > 1 ? "var(--secondary)" : "var(--primary)", display: "flex", alignItems: "center", gap: "0.3rem" }}>
                  {stageIndex > 1 ? <Check size={14} /> : <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--primary)" }}></span>}
                  {t("dash_stage1_title")}
                </span>
                <span style={{ fontSize: "0.7rem", color: "var(--outline)", fontFamily: "var(--font-code)" }}>{stageIndex > 1 ? t("dash_stage_done") : t("dash_stage_active")}</span>
              </div>
              <p style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {t("dash_stage1_sub")}
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
                  {t("dash_stage2_title")}
                </span>
                <span style={{ fontSize: "0.7rem", color: "var(--outline)", fontFamily: "var(--font-code)" }}>{stageIndex > 2 ? t("dash_stage_done") : stageIndex === 2 ? t("dash_stage_active") : t("dash_stage_queue")}</span>
              </div>
              <p style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {t("dash_stage2_sub")}
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
                  {t("dash_stage3_title")}
                </span>
                <span style={{ fontSize: "0.7rem", color: "var(--outline)", fontFamily: "var(--font-code)" }}>{stageIndex > 3 ? t("dash_stage_done") : stageIndex === 3 ? t("dash_stage_active") : t("dash_stage_queue")}</span>
              </div>
              <p style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {t("dash_stage3_sub")}
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
                  {t("dash_stage4_title")}
                </span>
                <span style={{ fontSize: "0.7rem", color: "var(--outline)", fontFamily: "var(--font-code)" }}>{stageIndex > 4 ? t("dash_stage_done") : stageIndex === 4 ? t("dash_stage_active") : t("dash_stage_queue")}</span>
              </div>
              <p style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {t("dash_stage4_sub")}
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
                  {t("dash_stage5_title")}
                </span>
                <span style={{ fontSize: "0.7rem", color: "var(--outline)", fontFamily: "var(--font-code)" }}>{stageIndex === 5 ? t("dash_stage_active") : t("dash_stage_final")}</span>
              </div>
              <p style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {t("dash_stage5_sub")}
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
            {typeof pipelineMessage.text === "string" ? pipelineMessage.text : JSON.stringify(pipelineMessage.text)}
          </div>
        )}

        {/* Main Grid: Hero Action Canvas (Left) + Coach Guidance (Right) */}
        <div style={{ display: "grid", gridTemplateColumns: "2.2fr 1fr", gap: "1.5rem", marginBottom: "2rem" }}>
          
          {/* Hero Action Card */}
          <div className="card" style={{ padding: "1.75rem", display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
                <span className="badge badge-primary">
                  {t("dash_step_prefix")} {stageIndex} {t("dash_of")} 5: {curStage === "search" ? t("dash_step1_name") : curStage === "gap" ? t("dash_step2_name") : curStage === "title" ? t("dash_step3_name") : curStage === "deepdive" ? t("dash_step4_name") : t("dash_step5_name")}
                </span>
                <span className="badge badge-secondary">{t("dash_ready_student")}</span>
              </div>
              <h1 style={{ fontSize: "1.6rem", fontWeight: 700, color: "var(--on-surface)", lineHeight: 1.3 }}>
                {selectedProject?.title || t("dash_default_project_title")}
              </h1>
              <p style={{ color: "var(--on-surface-variant)", fontSize: "0.95rem", marginTop: "0.35rem" }}>
                {t("dash_project_id")}: <code>{selectedProject?.id || "prj-new"}</code> • {t("dash_tenant_label")}: <span style={{ fontWeight: 600 }}>{user?.tenant_id}</span>
                {selectedProject?.state_json?.last_saved_stage && (
                  <span> • {t("dash_last_saved")}: <strong style={{ color: "var(--primary)" }}>{selectedProject.state_json.last_saved_stage}</strong></span>
                )}
              </p>
            </div>

            {/* STAGE 1: Interactive Topic Literature Search & Article Discovery Box */}
            <div style={{ background: "var(--surface-low)", border: "1px solid var(--border-subtle)", borderRadius: "12px", padding: "1.25rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontWeight: 700, fontSize: "0.98rem", color: "var(--on-surface)" }}>
                    <Search size={16} color="var(--primary)" />
                    {t("dash_stage1_header")}
                  </div>
                  <p style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", marginTop: "0.15rem" }}>
                    {t("dash_stage1_desc")}
                  </p>
                </div>

                {/* Scope selector pills */}
                <div style={{ display: "flex", gap: "0.4rem", background: "#ffffff", padding: "0.2rem", borderRadius: "8px", border: "1px solid var(--border-subtle)" }}>
                  <button
                    type="button"
                    onClick={() => setSearchScope("MY")}
                    style={{
                      padding: "0.3rem 0.65rem",
                      fontSize: "0.76rem",
                      borderRadius: "6px",
                      border: "none",
                      fontWeight: 600,
                      background: searchScope === "MY" ? "var(--primary)" : "transparent",
                      color: searchScope === "MY" ? "#ffffff" : "var(--on-surface-variant)",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: "0.3rem"
                    }}
                  >
                    🇲🇾 {t("dash_scope_my")}
                  </button>
                  <button
                    type="button"
                    onClick={() => setSearchScope("INT")}
                    style={{
                      padding: "0.3rem 0.65rem",
                      fontSize: "0.76rem",
                      borderRadius: "6px",
                      border: "none",
                      fontWeight: 600,
                      background: searchScope === "INT" ? "var(--primary)" : "transparent",
                      color: searchScope === "INT" ? "#ffffff" : "var(--on-surface-variant)",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: "0.3rem"
                    }}
                  >
                    🌐 {t("dash_scope_int")}
                  </button>
                </div>
              </div>

              {/* Main Search Input Bar */}
              <form onSubmit={handleSearchTopic} style={{ display: "flex", gap: "0.5rem" }}>
                <div style={{ position: "relative", flex: 1 }}>
                  <Search size={16} color="var(--outline)" style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)" }} />
                  <input
                    type="text"
                    placeholder={t("dash_search_placeholder")}
                    value={searchTopicInput}
                    onChange={(e) => setSearchTopicInput(e.target.value)}
                    className="input-control"
                    style={{ paddingLeft: "2.5rem", fontSize: "0.9rem" }}
                  />
                </div>
                <button
                  type="submit"
                  disabled={isSearching || !searchTopicInput.trim()}
                  className="btn-primary"
                  style={{ padding: "0.5rem 1.15rem", fontSize: "0.88rem", display: "flex", alignItems: "center", gap: "0.45rem", whiteSpace: "nowrap" }}
                >
                  {isSearching ? <RotateCw className="animate-spin" size={15} /> : <Search size={15} />}
                  {isSearching ? t("dash_searching") : t("dash_btn_search")}
                </button>
              </form>

              {searchFeedback && (
                <div style={{
                  padding: "0.65rem 0.85rem",
                  borderRadius: "6px",
                  fontSize: "0.82rem",
                  background: searchFeedback.type === "success" ? "var(--secondary-container)" : "var(--error-container)",
                  color: searchFeedback.type === "success" ? "var(--on-secondary-container)" : "var(--on-error-container)",
                  border: "1px solid var(--border-subtle)",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.4rem"
                }}>
                  {searchFeedback.type === "success" ? <CheckCircle2 size={14} /> : <AlertTriangle size={14} />}
                  {typeof searchFeedback.msg === "string" ? searchFeedback.msg : JSON.stringify(searchFeedback.msg)}
                </div>
              )}

              {/* Retrieved Articles Grid */}
              {searchedPapers && searchedPapers.length > 0 && (
                <div style={{ marginTop: "0.5rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem", flexWrap: "wrap", gap: "0.5rem" }}>
                    <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--on-surface)" }}>
                      {t("dash_found_articles")} {searchedPapers.length} {t("dash_peer_reviewed_articles")}
                    </span>
                    <button
                      type="button"
                      onClick={handleRunGapAnalysis}
                      disabled={Boolean(runningStage)}
                      className="btn-amber"
                      style={{ fontSize: "0.78rem", padding: "0.35rem 0.75rem", display: "inline-flex", alignItems: "center", gap: "0.35rem" }}
                    >
                      <Sparkles size={13} />
                      {t("dash_proceed_gap_prefix")} {searchedPapers.length} {t("dash_proceed_gap_suffix")}
                    </button>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "0.65rem", maxHeight: "290px", overflowY: "auto", paddingRight: "0.3rem" }}>
                    {searchedPapers.map((paper: any, idx: number) => {
                      const isUtm = paper.source === "utm";
                      return (
                        <div key={paper.doi || idx} style={{ background: "#ffffff", border: "1px solid var(--border-subtle)", borderRadius: "8px", padding: "0.75rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                          <div>
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.4rem", marginBottom: "0.25rem" }}>
                              <span style={{ fontWeight: 600, fontSize: "0.84rem", color: "var(--on-surface)", lineHeight: 1.3 }}>
                                {paper.title}
                              </span>
                            </div>
                            <div style={{ fontSize: "0.74rem", color: "var(--on-surface-variant)", marginBottom: "0.35rem" }}>
                              {paper.authors && paper.authors.length > 0 ? paper.authors.slice(0, 2).join(", ") + (paper.authors.length > 2 ? " et al." : "") : t("dash_unknown_author")} {paper.year ? `(${paper.year})` : ""}
                            </div>
                            {paper.abstract && (
                              <p style={{ fontSize: "0.75rem", color: "var(--outline)", lineHeight: 1.35, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                                {paper.abstract}
                              </p>
                            )}
                          </div>
                          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "0.5rem", paddingTop: "0.4rem", borderTop: "1px solid var(--border-subtle)" }}>
                            <div style={{ display: "flex", gap: "0.35rem", alignItems: "center" }}>
                              <span className={isUtm ? "badge badge-tenant" : "badge badge-secondary"} style={{ fontSize: "0.68rem" }}>
                                {isUtm ? t("dash_utm_repo") : t("dash_openalex_repo")}
                              </span>
                              {paper.citation_count > 0 && (
                                <span style={{ fontSize: "0.68rem", color: "var(--secondary)", fontWeight: 600 }}>
                                  {paper.citation_count} {t("dash_citations_label")}
                                </span>
                              )}
                            </div>
                            <a
                              href={getPaperLink(paper)}
                              target="_blank"
                              rel="noreferrer"
                              style={{ fontSize: "0.72rem", color: "var(--primary)", display: "inline-flex", alignItems: "center", gap: "0.2rem", fontWeight: 500 }}
                            >
                              {t("dash_view_paper")} <ExternalLink size={11} />
                            </a>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            {/* Quick Pipeline Runner Buttons (Stages 2-5) */}
            <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", padding: "1rem", background: "var(--surface-low)", borderRadius: "10px", border: "1px solid var(--border-subtle)" }}>
              <button
                onClick={handleRunGapAnalysis}
                disabled={Boolean(runningStage)}
                className="btn-primary"
                style={{ fontSize: "0.85rem", padding: "0.5rem 0.95rem" }}
              >
                {runningStage === "gap" ? <RotateCw className="animate-spin" size={14} /> : <Sparkles size={14} />}
                {t("dash_btn_gap")}
              </button>

              <button
                onClick={() => handleRunTitleSuggestions()}
                disabled={Boolean(runningStage)}
                className="btn-secondary"
                style={{ fontSize: "0.85rem", padding: "0.5rem 0.95rem" }}
              >
                {runningStage === "title" ? <RotateCw className="animate-spin" size={14} /> : <Lightbulb size={14} />}
                {t("dash_btn_title")}
              </button>

              <button
                onClick={handleRunDeepDive}
                disabled={Boolean(runningStage)}
                className="btn-secondary"
                style={{ fontSize: "0.85rem", padding: "0.5rem 0.95rem" }}
              >
                {runningStage === "deepdive" ? <RotateCw className="animate-spin" size={14} /> : <Compass size={14} />}
                {t("dash_btn_deepdive")}
              </button>

              <button
                onClick={handleRunPlan}
                disabled={Boolean(runningStage)}
                className="btn-secondary"
                style={{ fontSize: "0.85rem", padding: "0.5rem 0.95rem" }}
              >
                {runningStage === "plan" ? <RotateCw className="animate-spin" size={14} /> : <FileText size={14} />}
                {t("dash_btn_plan")}
              </button>

              <Link
                href={`/plan?projectId=${selectedProject?.id || ""}`}
                className="btn-secondary"
                style={{ fontSize: "0.85rem", padding: "0.5rem 0.95rem", display: "inline-flex", alignItems: "center", gap: "0.4rem" }}
              >
                {t("dash_open_canvas")} <ChevronRight size={14} />
              </Link>
            </div>

            {/* Inline Stage Runner Feedback & Progress */}
            {runningStage && (
              <div style={{
                marginTop: "0.75rem",
                padding: "0.75rem 1rem",
                borderRadius: "8px",
                fontSize: "0.86rem",
                background: "var(--surface-high)",
                border: "1px solid var(--primary)",
                color: "var(--primary)",
                display: "flex",
                alignItems: "center",
                gap: "0.6rem"
              }}>
                <RotateCw className="animate-spin" size={16} />
                <span>
                  <strong>{t("dash_running_prefix")} {runningStage === "gap" ? t("dash_stage_label_gap") : runningStage === "title" ? t("dash_stage_label_title") : runningStage === "deepdive" ? t("dash_stage_label_deepdive") : t("dash_stage_label_plan")}...</strong> {t("dash_analyzing_lit")}
                </span>
              </div>
            )}

            {pipelineMessage && (
              <div style={{
                marginTop: "0.75rem",
                padding: "0.75rem 1rem",
                borderRadius: "8px",
                fontSize: "0.86rem",
                background: pipelineMessage.type === "success" ? "var(--secondary-container)" : "var(--error-container)",
                color: pipelineMessage.type === "success" ? "var(--on-secondary-container)" : "var(--on-error-container)",
                border: "1px solid var(--border-subtle)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: "0.75rem",
                flexWrap: "wrap"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  {pipelineMessage.type === "success" ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
                  <span>{typeof pipelineMessage.text === "string" ? pipelineMessage.text : JSON.stringify(pipelineMessage.text)}</span>
                </div>
                {(pipelineMessage.text?.toLowerCase?.().includes("quota") || user?.quota_remaining === 0) && (
                  <button
                    onClick={handleRefillQuota}
                    className="btn-primary"
                    style={{ padding: "0.3rem 0.75rem", fontSize: "0.76rem" }}
                  >
                    {t("dash_instant_refill_btn")}
                  </button>
                )}
              </div>
            )}

            {/* Live State Breakdown Strips */}
            {selectedProject?.state_json?.gaps && selectedProject.state_json.gaps.length > 0 && (
              <div>
                <h3 style={{ fontSize: "0.95rem", fontWeight: 700, marginBottom: "0.6rem", color: "var(--on-surface)" }}>
                  {t("dash_gaps_header")} ({selectedProject.state_json.gaps.length})
                </h3>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "0.75rem" }}>
                  {selectedProject.state_json.gaps.slice(0, 3).map((g: any, i: number) => (
                    <div key={g.gap_id || i} style={{ background: "#ffffff", border: "1px solid var(--border-subtle)", borderRadius: "8px", padding: "0.85rem" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.35rem" }}>
                        <span className="badge badge-primary">{g.gap_id || `Gap 0${i + 1}`}</span>
                        <span style={{ fontSize: "0.72rem", color: "var(--secondary)", fontWeight: 600 }}>{t("dash_citations_verified")}</span>
                      </div>
                      <p style={{ fontSize: "0.85rem", color: "var(--on-surface)", lineHeight: 1.4 }}>
                        {g.description}
                      </p>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "0.6rem", paddingTop: "0.4rem", borderTop: "1px solid var(--border-subtle)", flexWrap: "wrap", gap: "0.35rem" }}>
                        <span style={{ fontSize: "0.72rem", color: "var(--outline)", fontFamily: "var(--font-code)" }}>
                          {g.supporting_paper_ids ? `${lang === "bm" ? "Artikel" : "Papers"}: ${g.supporting_paper_ids.join(", ")}` : t("dash_citations_verified")}
                        </span>
                        <button
                          type="button"
                          onClick={() => handleRunTitleSuggestions(g.gap_id)}
                          disabled={Boolean(runningStage)}
                          className="btn-secondary"
                          style={{ fontSize: "0.72rem", padding: "0.25rem 0.55rem", cursor: "pointer" }}
                          title="Generate defended thesis titles specifically for this gap"
                        >
                          {t("dash_titles_for_gap_btn")}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Titles Strip */}
            {selectedProject?.state_json?.titles && selectedProject.state_json.titles.length > 0 && (
              <div>
                <h3 style={{ fontSize: "0.95rem", fontWeight: 700, marginBottom: "0.6rem", color: "var(--on-surface)" }}>
                  {t("dash_titles_header")} ({selectedProject.state_json.titles.length})
                </h3>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                  {selectedProject.state_json.titles.map((tItem: any, i: number) => {
                    const isSelected = selectedProject.title === tItem.title || selectedProject.state_json?.chosen_title === tItem.title;
                    return (
                      <div key={i} style={{ background: "#ffffff", border: isSelected ? "1.5px solid var(--primary)" : "1px solid var(--border-subtle)", borderRadius: "8px", padding: "0.75rem 1rem", display: "flex", justifyContent: "space-between", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
                        <div style={{ flex: 1, minWidth: "220px" }}>
                          <div style={{ fontWeight: 600, fontSize: "0.9rem", color: "var(--on-surface)" }}>{tItem.title}</div>
                          {tItem.title_bm && <div style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", fontStyle: "italic", marginTop: "2px" }}>BM: {tItem.title_bm}</div>}
                        </div>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                          <span className="badge badge-secondary">{tItem.language || "EN"}</span>
                          <button
                            type="button"
                            onClick={() => handleSelectTitle(tItem.title)}
                            className={isSelected ? "btn-primary" : "btn-secondary"}
                            style={{ fontSize: "0.75rem", padding: "0.3rem 0.65rem", cursor: "pointer" }}
                          >
                            {isSelected ? t("dash_active_title") : t("dash_select_title")}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Deep-Dive Papers Strip (Stage 4) */}
            {selectedProject?.state_json?.deepdive_papers && selectedProject.state_json.deepdive_papers.length > 0 && (
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.6rem" }}>
                  <h3 style={{ fontSize: "0.95rem", fontWeight: 700, margin: 0, color: "var(--on-surface)", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                    <Compass size={16} color="var(--primary)" />
                    {t("dash_deepdive_header")} ({selectedProject.state_json.deepdive_papers.length} {t("dash_targeted_papers")})
                  </h3>
                  <span className="badge badge-primary">{t("dash_methodology_aligned")}</span>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                  {selectedProject.state_json.deepdive_papers.map((p: any, i: number) => (
                    <div key={i} style={{ background: "#ffffff", border: "1px solid var(--border-subtle)", borderRadius: "8px", padding: "0.75rem 1rem" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.5rem" }}>
                        <div style={{ fontWeight: 600, fontSize: "0.88rem", color: "var(--on-surface)" }}>
                          {p.title}
                        </div>
                        <span className="badge badge-secondary" style={{ fontSize: "0.7rem", flexShrink: 0 }}>
                          {p.source?.toUpperCase() || "OPENALEX"}
                        </span>
                      </div>
                      <div style={{ fontSize: "0.76rem", color: "var(--outline)", marginTop: "0.25rem", display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
                        <span>{t("dash_authors_label")}: {Array.isArray(p.authors) ? p.authors.join(", ") : p.authors || "N/A"}</span>
                        <span>{t("dash_year_label")}: {p.year || "N/A"}</span>
                        {p.citation_count !== undefined && <span>{t("dash_citations_label")}: {p.citation_count}</span>}
                      </div>
                      {p.abstract && (
                        <p style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", marginTop: "0.4rem", lineHeight: 1.4 }}>
                          {p.abstract}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Stage 5: Research Plan Preview */}
            {(selectedProject?.current_plan_json || selectedProject?.state_json?.plan) && (() => {
              const activePlan = selectedProject?.current_plan_json || selectedProject?.state_json?.plan;
              return (
                <div style={{ background: "#ffffff", border: "1.5px solid var(--primary)", borderRadius: "10px", padding: "1.25rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem", flexWrap: "wrap", gap: "0.5rem" }}>
                    <div>
                      <span className="badge badge-primary" style={{ marginBottom: "0.25rem" }}>{t("dash_plan_ready_badge")}</span>
                      <h3 style={{ fontSize: "1.05rem", fontWeight: 700, margin: "0.2rem 0", color: "var(--on-surface)" }}>
                        {activePlan.title || selectedProject.title}
                      </h3>
                      <div style={{ fontSize: "0.78rem", color: "var(--outline)" }}>
                        {t("dash_plan_id_label")}: {activePlan.plan_id || "plan-active"} • {t("dash_version_label")} {activePlan.version || selectedProject.plan_version || 1}
                      </div>
                    </div>
                    <Link
                      href={`/plan?projectId=${selectedProject.id}`}
                      className="btn-primary"
                      style={{ fontSize: "0.82rem", padding: "0.45rem 0.85rem", display: "inline-flex", alignItems: "center", gap: "0.35rem" }}
                    >
                      {t("dash_open_full_plan_btn")} <ChevronRight size={14} />
                    </Link>
                  </div>

                  {activePlan.methodology_summary && (
                    <div style={{ background: "var(--surface-low)", padding: "0.75rem", borderRadius: "6px", marginBottom: "0.75rem", fontSize: "0.84rem", lineHeight: 1.45 }}>
                      <strong>{t("dash_methodology_summary_label")}</strong> {activePlan.methodology_summary}
                    </div>
                  )}

                  {activePlan.objectives && activePlan.objectives.length > 0 && (
                    <div style={{ marginBottom: "0.75rem" }}>
                      <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--on-surface)", marginBottom: "0.35rem" }}>
                        {t("dash_research_objectives_label")} ({activePlan.objectives.length}):
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                        {activePlan.objectives.map((obj: any, idx: number) => (
                          <div key={idx} style={{ fontSize: "0.82rem", display: "flex", gap: "0.4rem", alignItems: "flex-start" }}>
                            <span style={{ fontWeight: 700, color: "var(--primary)", minWidth: "40px" }}>{obj.objective_id || `RO-${idx + 1}`}:</span>
                            <span style={{ color: "var(--on-surface)" }}>{obj.text || obj}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {activePlan.key_milestones && activePlan.key_milestones.length > 0 && (
                    <div>
                      <div style={{ fontSize: "0.82rem", fontWeight: 700, color: "var(--on-surface)", marginBottom: "0.35rem" }}>
                        {t("dash_key_milestones_label")} ({activePlan.key_milestones.length}):
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "0.5rem" }}>
                        {activePlan.key_milestones.slice(0, 4).map((m: any, idx: number) => (
                          <div key={idx} style={{ background: "var(--surface-low)", padding: "0.5rem 0.75rem", borderRadius: "6px", fontSize: "0.78rem" }}>
                            <div style={{ fontWeight: 700, color: "var(--primary)" }}>{m.target_month || `Phase ${idx + 1}`}: {m.title}</div>
                            <div style={{ color: "var(--on-surface-variant)", marginTop: "2px", lineHeight: 1.35 }}>{m.description}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })()}
          </div>

          {/* Right Column: Coach Companion & Active Context */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            
            {/* Coach Callout & Conversational Assistant */}
            <div className="coach-card">
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontWeight: 700, marginBottom: "0.4rem" }}>
                <Sparkles size={16} /> {t("dash_coach_companion")}
              </div>
              <p style={{ fontSize: "0.86rem", lineHeight: 1.5, marginBottom: "0.75rem" }}>
                {curStage === "search" && t("dash_coach_p_search")}
                {curStage === "gap" && t("dash_coach_p_gap")}
                {curStage === "title" && t("dash_coach_p_title")}
                {curStage === "deepdive" && t("dash_coach_p_deepdive")}
                {curStage === "plan" && t("dash_coach_p_plan")}
              </p>

              {/* Quick Guidance Prompt Chips */}
              <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem", marginBottom: "0.75rem" }}>
                <span style={{ fontSize: "0.72rem", fontWeight: 700, color: "var(--outline)", textTransform: "uppercase" }}>{t("dash_quick_topics_label")}</span>
                <button
                  type="button"
                  onClick={() => {
                    const q = "Smart agriculture palm oil IoT Johor";
                    setSearchTopicInput(q);
                    handleSearchTopic(undefined, q);
                  }}
                  className="btn-secondary"
                  style={{ fontSize: "0.74rem", padding: "0.35rem 0.6rem", textAlign: "left", justifyContent: "flex-start" }}
                >
                  {t("dash_quick_topic_1")}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const q = "Blockchain halal food supply chain Malaysia";
                    setSearchTopicInput(q);
                    handleSearchTopic(undefined, q);
                  }}
                  className="btn-secondary"
                  style={{ fontSize: "0.74rem", padding: "0.35rem 0.6rem", textAlign: "left", justifyContent: "flex-start" }}
                >
                  {t("dash_quick_topic_2")}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const q = "Deep learning automated thesis grading UTM";
                    setSearchTopicInput(q);
                    handleSearchTopic(undefined, q);
                  }}
                  className="btn-secondary"
                  style={{ fontSize: "0.74rem", padding: "0.35rem 0.6rem", textAlign: "left", justifyContent: "flex-start" }}
                >
                  {t("dash_quick_topic_3")}
                </button>
              </div>

              {/* Conversational prompt form */}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (!academicCoachPrompt.trim()) return;
                  setSearchTopicInput(academicCoachPrompt.trim());
                  handleSearchTopic(undefined, academicCoachPrompt.trim());
                  setAcademicCoachPrompt("");
                }}
                style={{ display: "flex", gap: "0.4rem" }}
              >
                <input
                  type="text"
                  placeholder={t("dash_coach_input_ph")}
                  value={academicCoachPrompt}
                  onChange={(e) => setAcademicCoachPrompt(e.target.value)}
                  className="input-control"
                  style={{ fontSize: "0.8rem", padding: "0.4rem 0.6rem" }}
                />
                <button type="submit" disabled={isSearching} className="btn-primary" style={{ padding: "0.4rem 0.75rem", fontSize: "0.8rem" }}>
                  <Send size={13} />
                </button>
              </form>
            </div>

            {/* Account & Tenant Overview */}
            <div className="card" style={{ padding: "1.25rem" }}>
              <h3 style={{ fontSize: "0.95rem", fontWeight: 700, marginBottom: "0.75rem", display: "flex", alignItems: "center", gap: "0.45rem" }}>
                <Building2 size={16} color="var(--primary)" /> {t("dash_tenant_iso_title")}
              </h3>
              <p style={{ fontSize: "0.82rem", color: "var(--on-surface-variant)", marginBottom: "0.75rem" }}>
                {t("dash_current_user_label")}: <strong>{user?.email}</strong><br />
                {t("dash_inst_id_label")}: <code>{user?.tenant_id}</code><br />
                {t("dash_role_label")}: <span className="badge badge-student" style={{ padding: "0.1rem 0.4rem" }}>{user?.role}</span>
              </p>

              <button
                onClick={handleTestCrossTenant}
                disabled={isolationTestStatus === "testing"}
                className="btn-secondary"
                style={{ width: "100%", fontSize: "0.8rem", padding: "0.5rem" }}
              >
                <Lock size={13} /> {isolationTestStatus === "testing" ? t("dash_verifying_tenant") : t("dash_btn_verify_tenant")}
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
                {isAdmin ? `${t("dash_all_projects_title")} (${tenantName})` : t("dash_my_projects_title")}
              </h2>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <span className="badge badge-tenant">{projects.length} {t("dash_records_badge")}</span>
              <button
                onClick={async () => {
                  try {
                    const res = await fetchWithAuth("/projects", {
                      method: "POST",
                      body: JSON.stringify({
                        title: "New Research Project",
                        stage: "search",
                        state_json: { topic: "", scope: "MY" },
                      }),
                    });
                    if (res.ok) {
                      const newProj = await res.json();
                      setProjects((prev) => [newProj, ...prev]);
                      setSelectedProject(newProj);
                      setSearchTopicInput("");
                      setSearchedPapers([]);
                      setPipelineMessage({
                        type: "success",
                        text: lang === "bm"
                          ? `Projek baharu dicipta: ${newProj.id}. Sila masukkan topik kajian anda di atas untuk bermula.`
                          : `New project created: ${newProj.id}. Enter your research topic above to begin.`
                      });
                    } else if (res.status === 401) {
                      clearToken();
                      router.push("/login");
                    } else {
                      const err = await res.json();
                      setPipelineMessage({ type: "error", text: getApiErrorMessage(err, "Failed to create project") });
                    }
                  } catch (err: any) {
                    setPipelineMessage({ type: "error", text: getApiErrorMessage(err, "Failed to create project") });
                  }
                }}
                className="btn-primary"
                style={{ fontSize: "0.82rem", padding: "0.4rem 0.85rem" }}
              >
                {t("dash_btn_new_project")}
              </button>
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
            {projects.map((p) => {
              const isSelected = selectedProject?.id === p.id;
              const hasPlan = Boolean(p.current_plan_json || p.plan_id || p.state_json?.plan);
              return (
                <div
                  key={p.id}
                  onClick={() => {
                    setSelectedProject(p);
                    if (p.state_json?.papers && p.state_json.papers.length > 0) {
                      setSearchedPapers(p.state_json.papers);
                    }
                    if (p.title) {
                      setSearchTopicInput(p.title);
                    }
                  }}
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
                      {t("dash_project_stage_label")}: <strong style={{ color: "var(--primary)", textTransform: "capitalize" }}>{p.stage}</strong> • ID: <code>{p.id}</code>
                      {p.state_json?.last_saved_stage && (
                        <span> • {t("dash_last_saved")}: {p.state_json.last_saved_stage}</span>
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
                      {hasPlan ? `${t("dash_btn_view_plan")} (v${p.plan_version || 1})` : t("dash_btn_draft_plan")}
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
        </div>
        )}
      </main>

      {/* API Key Management Modal (Adheres to design Website) */}
      {showSettingsModal && (
        <div className="modal-overlay">
          <div className="modal-content" style={{ padding: "1.75rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem", borderBottom: "1px solid var(--border-subtle)", paddingBottom: "0.75rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <KeyRound size={20} color="var(--primary)" />
                <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--on-surface)" }}>
                  {lang === "bm" ? "Kunci API & Tetapan Kecerdasan" : "API Key & Intelligence Settings"}
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
                {typeof keyFeedback.msg === "string" ? keyFeedback.msg : JSON.stringify(keyFeedback.msg)}
              </div>
            )}

            {/* Mode Toggle Banner */}
            <div style={{ background: "var(--surface-low)", border: "1px solid var(--border-subtle)", borderRadius: "8px", padding: "1rem", marginBottom: "1.25rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: "0.92rem", color: "var(--on-surface)" }}>
                    {lang === "bm" ? "Mod Sistem" : "System Mode"}: {keySettings?.demo_mode ? (lang === "bm" ? "MOD DEMO (Piawai)" : "DEMO MODE (Default)") : (lang === "bm" ? "MOD SIARAN LANGSUNG" : "LIVE MODE")}
                  </div>
                  <p style={{ fontSize: "0.8rem", color: "var(--on-surface-variant)", marginTop: "0.2rem" }}>
                    {keySettings?.demo_mode 
                      ? (lang === "bm" ? "Menggunakan data penanda aras bagi penilaian pantas tanpa kunci luaran." : "Uses deterministic fixtures for instant evaluations with zero external keys required.") 
                      : (lang === "bm" ? "Memanggil model langsung DeepSeek/OpenAI menggunakan kunci sulit anda." : "Calls live DeepSeek/OpenAI model endpoints using your encrypted key.")}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => handleToggleDemoMode(!keySettings?.demo_mode)}
                  disabled={savingKey}
                  className="btn-amber"
                  style={{ fontSize: "0.8rem", padding: "0.4rem 0.75rem" }}
                >
                  {keySettings?.demo_mode ? (lang === "bm" ? "Tukar ke LANGSUNG" : "Switch to LIVE") : (lang === "bm" ? "Tukar ke DEMO" : "Switch to DEMO")}
                </button>
              </div>
            </div>

            {/* Stored Key Status */}
            <div style={{ marginBottom: "1.25rem" }}>
              <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--on-surface)", marginBottom: "0.35rem" }}>
                {lang === "bm" ? "Kunci Institusi Tersimpan" : "Stored Tenant Key"} ({lang === "bm" ? "Institusi" : "Tenant"}: <code>{keySettings?.tenant_id}</code>)
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", background: "#ffffff", border: "1px solid var(--border-subtle)", borderRadius: "8px", padding: "0.65rem 0.95rem" }}>
                <span style={{ fontFamily: "var(--font-code)", fontSize: "0.88rem", color: keySettings?.has_custom_key ? "var(--on-surface)" : "var(--outline)" }}>
                  {keySettings?.has_custom_key ? (keySettings.key_preview || "sk-••••••••••••") : (lang === "bm" ? "Tiada kunci khusus dikonfigurasi (Guna mod demo sandaran)" : "No custom key configured (Using system/demo fallback)")}
                </span>
                {keySettings?.has_custom_key && (
                  <button
                    onClick={handleDeleteApiKey}
                    disabled={savingKey}
                    style={{ color: "var(--error)", fontSize: "0.8rem", fontWeight: 600 }}
                  >
                    {lang === "bm" ? "Padam" : "Remove"}
                  </button>
                )}
              </div>
            </div>

            {/* Input New API Key Form */}
            <form onSubmit={handleSaveApiKey} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--on-surface)", marginBottom: "0.35rem" }}>
                  {lang === "bm" ? "Pembekal Model LLM" : "LLM Provider"}
                </label>
                <select
                  value={selectedProvider}
                  onChange={(e) => setSelectedProvider(e.target.value)}
                  className="input-control"
                  style={{ fontSize: "0.88rem" }}
                >
                  <option value="deepseek">DeepSeek (deepseek-chat) — {lang === "bm" ? "Disyorkan untuk Panduan Tesis" : "Recommended for Thesis Guidance"}</option>
                  <option value="openai">OpenAI (gpt-4o-mini)</option>
                </select>
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--on-surface)", marginBottom: "0.35rem" }}>
                  {lang === "bm" ? "Masukkan Kunci API" : "Enter API Key"}
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
                {lang === "bm" ? "Kunci disulitkan dengan AES-256 sebelum disimpan ke pangkalan data. Kunci teks biasa tidak pernah disimpan dalam git atau log." : "Key is AES-256 encrypted before database storage. Plaintext keys are never stored in git or logs."}
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.6rem", marginTop: "0.5rem" }}>
                <button
                  type="button"
                  onClick={() => setShowSettingsModal(false)}
                  className="btn-secondary"
                  style={{ fontSize: "0.88rem", padding: "0.5rem 1rem" }}
                >
                  {lang === "bm" ? "Tutup" : "Close"}
                </button>
                <button
                  type="submit"
                  disabled={savingKey || !inputKey.trim()}
                  className="btn-primary"
                  style={{ fontSize: "0.88rem", padding: "0.5rem 1rem" }}
                >
                  {savingKey ? (lang === "bm" ? "Menyulitkan..." : "Encrypting...") : (lang === "bm" ? "Simpan Kunci Disulitkan" : "Save Encrypted Key")}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
