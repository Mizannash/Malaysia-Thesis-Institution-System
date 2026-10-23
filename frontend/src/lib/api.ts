import {
  DEMO_USERS,
  DEMO_TENANTS,
  DEMO_SEARCH_PAPERS,
  DEMO_GAPS,
  DEMO_TITLES,
  DEMO_PLAN,
  INITIAL_DEMO_PROJECTS,
} from "./demoData";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("mtis_token");
}

export function setToken(token: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("mtis_token", token);
    // Also set a cookie so Next.js middleware can inspect auth status
    document.cookie = `mtis_token=${token}; path=/; max-age=28800; SameSite=Lax`;
  }
}

export function clearToken() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("mtis_token");
    localStorage.removeItem("mtis_user");
    document.cookie = "mtis_token=; path=/; max-age=0";
  }
}

/**
 * Client-Side Demo Mock Engine
 * Activates when deployed on Netlify / remote hosts without a live backend connection.
 */
function handleOfflineDemoResponse(endpoint: string, options: RequestInit = {}): Response {
  const method = (options.method || "GET").toUpperCase();
  const body = options.body ? JSON.parse(options.body as string) : {};

  // 1. /auth/me
  if (endpoint === "/auth/me") {
    const stored = typeof window !== "undefined" ? localStorage.getItem("mtis_user") : null;
    const user = stored ? JSON.parse(stored) : DEMO_USERS[0];
    return new Response(JSON.stringify(user), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  // 2. /auth/demo-login
  if (endpoint === "/auth/demo-login") {
    const email = body.email || "student@demo.test";
    const foundUser = DEMO_USERS.find((u) => u.email === email) || {
      id: `usr-${email.split("@")[0]}`,
      tenant_id: body.tenant_id || "tenant-demo-002",
      name: body.name || email.split("@")[0],
      email: email,
      role: body.role || "student",
      plan: body.role === "student" ? "free" : "pro",
      quota_remaining: body.role === "student" ? 3 : 99,
      quota_reset_at: new Date(Date.now() + 86400000).toISOString(),
      created_at: new Date().toISOString(),
    };
    const tenant = DEMO_TENANTS[foundUser.tenant_id] || {
      id: foundUser.tenant_id,
      name: "Demo University Campus",
    };
    return new Response(
      JSON.stringify({
        access_token: `demo-token-${foundUser.role}-${Date.now()}`,
        token_type: "bearer",
        user: foundUser,
        tenant: tenant,
      }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  }

  // 3. /projects
  if (endpoint === "/projects") {
    const rawProjects = typeof window !== "undefined" ? localStorage.getItem("mtis_demo_projects") : null;
    let projects = rawProjects ? JSON.parse(rawProjects) : INITIAL_DEMO_PROJECTS;

    if (method === "POST") {
      const newP = {
        id: `proj-demo-${Date.now()}`,
        tenant_id: body.tenant_id || "tenant-demo-002",
        user_id: "usr-student",
        title: body.title || "New Malaysian Thesis Topic",
        stage: body.stage || "search",
        state_json: body.state_json || {},
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      projects = [newP, ...projects];
      if (typeof window !== "undefined") {
        localStorage.setItem("mtis_demo_projects", JSON.stringify(projects));
      }
      return new Response(JSON.stringify(newP), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }

    return new Response(JSON.stringify(projects), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  // 4. /projects/:id
  if (endpoint.startsWith("/projects/")) {
    const projId = endpoint.replace("/projects/", "");
    const rawProjects = typeof window !== "undefined" ? localStorage.getItem("mtis_demo_projects") : null;
    const projects = rawProjects ? JSON.parse(rawProjects) : INITIAL_DEMO_PROJECTS;
    let proj = projects.find((p: any) => p.id === projId) || projects[0];

    if (method === "PATCH") {
      proj = {
        ...proj,
        stage: body.stage || proj.stage,
        state_json: { ...(proj.state_json || {}), ...(body.state_json || {}) },
        updated_at: new Date().toISOString(),
      };
      const updatedList = projects.map((p: any) => (p.id === proj.id ? proj : p));
      if (typeof window !== "undefined") {
        localStorage.setItem("mtis_demo_projects", JSON.stringify(updatedList));
      }
    }

    return new Response(JSON.stringify(proj), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  // 5. /api/settings/keys
  if (endpoint === "/api/settings/keys") {
    return new Response(
      JSON.stringify({
        provider: "deepseek",
        has_custom_key: false,
        key_preview: null,
        demo_mode: true,
        tenant_id: "tenant-demo-002",
      }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  }

  // 6. /api/admin/users
  if (endpoint === "/api/admin/users") {
    const rawUsers = typeof window !== "undefined" ? localStorage.getItem("mtis_demo_admin_users") : null;
    let users = rawUsers ? JSON.parse(rawUsers) : DEMO_USERS;

    if (method === "POST") {
      const newUser = {
        id: `usr-${body.email.split("@")[0]}`,
        tenant_id: body.tenant_id || "tenant-demo-002",
        name: body.name,
        email: body.email,
        role: body.role || "student",
        plan: body.plan || "free",
        quota_remaining: body.plan === "pro" ? 99 : 3,
        quota_reset_at: new Date(Date.now() + 86400000).toISOString(),
        created_at: new Date().toISOString(),
      };
      users = [...users, newUser];
      if (typeof window !== "undefined") {
        localStorage.setItem("mtis_demo_admin_users", JSON.stringify(users));
      }
      return new Response(JSON.stringify(newUser), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }

    return new Response(JSON.stringify(users), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  // 7. /api/admin/users/:id/plan
  if (endpoint.includes("/api/admin/users/") && endpoint.endsWith("/plan")) {
    const parts = endpoint.split("/");
    const userId = parts[parts.length - 2];
    const rawUsers = typeof window !== "undefined" ? localStorage.getItem("mtis_demo_admin_users") : null;
    const users = rawUsers ? JSON.parse(rawUsers) : DEMO_USERS;
    const user = users.find((u: any) => u.id === userId) || users[0];
    user.plan = body.plan;
    user.quota_remaining = body.plan === "enterprise" ? 999 : body.plan === "pro" ? 99 : 3;
    if (typeof window !== "undefined") {
      localStorage.setItem("mtis_demo_admin_users", JSON.stringify(users));
    }
    return new Response(JSON.stringify(user), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  // 8. /api/admin/stats
  if (endpoint === "/api/admin/stats") {
    return new Response(
      JSON.stringify({
        total_users: 18,
        active_projects: 34,
        total_searches: 142,
        system_health: "Optimal (Zero-Key Demo Active)",
      }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  }

  // 9. /search/literature
  if (endpoint === "/search/literature") {
    return new Response(JSON.stringify(DEMO_SEARCH_PAPERS), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  // 10. /pipeline/stage2-gap
  if (endpoint === "/pipeline/stage2-gap") {
    return new Response(JSON.stringify({ gaps: DEMO_GAPS }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  // 11. /pipeline/stage3-titles
  if (endpoint === "/pipeline/stage3-titles") {
    return new Response(JSON.stringify({ titles: DEMO_TITLES }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  // 12. /pipeline/stage4-deepdive
  if (endpoint === "/pipeline/stage4-deepdive") {
    return new Response(
      JSON.stringify({
        chosen_title: body.chosen_title || DEMO_TITLES[0].title,
        gap_id: body.gap_id || "GAP-1",
        papers: DEMO_SEARCH_PAPERS,
      }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  }

  // 13. /pipeline/stage5-plan
  if (endpoint === "/pipeline/stage5-plan") {
    return new Response(JSON.stringify(DEMO_PLAN), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  // 14. /pipeline/refine-plan
  if (endpoint === "/pipeline/refine-plan") {
    const refinedPlan = {
      ...DEMO_PLAN,
      version: 2,
      objectives: [
        ...DEMO_PLAN.objectives,
        {
          objective_id: "RO-4",
          text: `Refined Focus: ${body.refine_prompt || "Enhanced quantitative sampling across SME retail hubs."}`,
        },
      ],
    };
    return new Response(JSON.stringify(refinedPlan), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Default fallback
  return new Response(JSON.stringify({ status: "ok", demo: true }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const token = getToken();
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  // If running in browser on a deployed cloud domain (e.g. Netlify) and API_BASE is localhost
  const isRemoteDeployment =
    typeof window !== "undefined" &&
    window.location.hostname !== "localhost" &&
    window.location.hostname !== "127.0.0.1" &&
    API_BASE.includes("localhost");

  if (isRemoteDeployment) {
    return handleOfflineDemoResponse(endpoint, options);
  }

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });
    return response;
  } catch (err) {
    console.warn(`[MTIS Demo Fallback] Backend fetch to ${endpoint} failed. Serving demo response.`);
    return handleOfflineDemoResponse(endpoint, options);
  }
}

export function getApiErrorMessage(err: any, fallback: string = "An error occurred"): string {
  if (!err) return fallback;
  if (typeof err === "string") return err;
  if (typeof err.message === "string" && err.message) return err.message;
  if (typeof err.detail === "string" && err.detail) return err.detail;
  if (err.detail && typeof err.detail === "object") {
    if (typeof err.detail.message === "string" && err.detail.message) return err.detail.message;
    if (typeof err.detail.first_error === "string" && err.detail.first_error) return err.detail.first_error;
    try {
      return JSON.stringify(err.detail);
    } catch {
      return fallback;
    }
  }
  if (typeof err.error === "string" && err.error) return err.error;
  return fallback;
}
