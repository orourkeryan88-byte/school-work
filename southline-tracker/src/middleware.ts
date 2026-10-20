import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

// Auth gate. Only active when Supabase is configured - in mock mode the app is open.
// Webhook/sync endpoints are excluded here and check INGEST_SECRET themselves.
const PUBLIC = ["/login", "/manifest.webmanifest", "/icon", "/apple-icon", "/api/ingest", "/api/integrations", "/api/sync", "/api/health"];

export async function middleware(request: NextRequest) {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !anon) return NextResponse.next();
  if (PUBLIC.some((p) => request.nextUrl.pathname.startsWith(p))) return NextResponse.next();

  let response = NextResponse.next({ request });
  const supabase = createServerClient(url, anon, {
    cookies: {
      getAll: () => request.cookies.getAll(),
      setAll: (list) => {
        list.forEach(({ name, value }) => request.cookies.set(name, value));
        response = NextResponse.next({ request });
        list.forEach(({ name, value, options }) => response.cookies.set(name, value, options));
      },
    },
  });

  const { data } = await supabase.auth.getUser();
  const email = data.user?.email?.toLowerCase();
  const allowed = (process.env.ALLOWED_EMAILS ?? "").split(",").map((s) => s.trim().toLowerCase()).filter(Boolean);
  if (!email || (allowed.length && !allowed.includes(email))) {
    if (request.nextUrl.pathname.startsWith("/api/")) return NextResponse.json({ error: "unauthorised" }, { status: 401 });
    const login = request.nextUrl.clone();
    login.pathname = "/login";
    login.search = email ? "?error=not_allowed" : "";
    return NextResponse.redirect(login);
  }
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|ico)$).*)"],
};
