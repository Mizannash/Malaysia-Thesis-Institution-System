"use client";

import { useEffect } from "react";
import { isSupabaseConfigured, supabase } from "@/lib/supabase";
import { clearToken, setToken } from "@/lib/api";

/**
 * Keeps mtis_token (localStorage + cookie read by middleware) in step with the Supabase session,
 * including the hourly access-token refresh. Renders nothing.
 */
export default function SupabaseSessionSync() {
  useEffect(() => {
    if (!isSupabaseConfigured) return;

    supabase.auth.getSession().then(({ data }) => {
      if (data.session) setToken(data.session.access_token);
    });

    const { data } = supabase.auth.onAuthStateChange((event, session) => {
      if (session && (event === "SIGNED_IN" || event === "TOKEN_REFRESHED" || event === "INITIAL_SESSION")) {
        setToken(session.access_token);
      } else if (event === "SIGNED_OUT") {
        clearToken();
      }
    });
    return () => data.subscription.unsubscribe();
  }, []);

  return null;
}
