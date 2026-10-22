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

export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const token = getToken();
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  return response;
}
