import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Protect /dashboard and any child routes
  if (pathname.startsWith("/dashboard")) {
    const token = request.cookies.get("mtis_token")?.value;

    // Also allow Supabase auth tokens in cookies if configured
    const sbToken = request.cookies.get("sb-access-token")?.value;

    if (!token && !sbToken) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("redirectedFrom", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*"],
};
