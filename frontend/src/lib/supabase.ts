import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://dummy-project.supabase.co";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "dummy-anon-key";

export const isSupabaseConfigured = Boolean(
  process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export async function signInWithGoogle() {
  if (isSupabaseConfigured) {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/dashboard`,
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
