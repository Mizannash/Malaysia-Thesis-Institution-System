import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://dummy-project.supabase.co";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "dummy-anon-key";

export const isSupabaseConfigured = Boolean(
  process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export async function signInWithGoogle() {
  if (isSupabaseConfigured) {
    // Return to /login (not /dashboard): the middleware needs mtis_token, which is set after the session is read
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/login`,
      },
    });
    if (error) throw error;
    return data;
  } else {
    // In DEMO_MODE fallback, redirect to dashboard with default demo student
    console.info("DEMO_MODE: Supabase keys not set, simulating Google OAuth callback.");
    window.location.href = "/login?demo_auto=true";
  }
}

// ── MTIS email + password accounts (passwords are stored by Supabase Auth, never by MTIS) ──

export async function signUpWithEmail(name: string, email: string, password: string) {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: { full_name: name },
      emailRedirectTo: `${window.location.origin}/login`,
    },
  });
  if (error) throw error;
  return data;
}

export async function resendConfirmation(email: string) {
  const { error } = await supabase.auth.resend({
    type: "signup",
    email,
    options: { emailRedirectTo: `${window.location.origin}/login` },
  });
  if (error) throw error;
}

export async function signInWithEmail(email: string, password: string) {
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) throw error;
  return data;
}

export async function sendPasswordReset(email: string) {
  const { error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${window.location.origin}/reset-password`,
  });
  if (error) throw error;
}

export async function updatePassword(newPassword: string) {
  const { error } = await supabase.auth.updateUser({ password: newPassword });
  if (error) throw error;
}

/** Maps Supabase Auth errors to translation keys for friendly EN/BM messages. */
export function authErrorKey(err: any): string {
  const code = String(err?.code || "").toLowerCase();
  const msg = String(err?.message || "").toLowerCase();
  if (code === "invalid_credentials" || msg.includes("invalid login credentials")) return "auth_err_invalid";
  if (code === "email_not_confirmed" || msg.includes("email not confirmed")) return "auth_err_unconfirmed";
  if (code === "user_already_exists" || msg.includes("already registered")) return "auth_err_exists";
  if (code === "weak_password" || msg.includes("password should")) return "auth_err_weak";
  if (code.includes("rate_limit") || msg.includes("rate limit") || err?.status === 429) return "auth_err_rate";
  return "auth_err_generic";
}

export async function signOutSupabase() {
  if (!isSupabaseConfigured) return;
  try {
    await supabase.auth.signOut();
  } catch {
    // already signed out or offline: local token is cleared by the caller
  }
}
