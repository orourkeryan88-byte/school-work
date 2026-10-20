import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { SESSION_COOKIE, verifySessionToken } from "@/lib/session";

// Auth gate. Supabase Auth when Supabase is configured, otherwise the
// built-in login (APP_LOGIN_EMAIL / APP_PASSWORD, see lib/session.ts).
// Webhook/sync endpoints are excluded here and check INGEST_SECRET themselves.
const PUBLIC = ["/login", "/manifest.webmanifest", "/icon", "/apple-icon", "/api/ingest", "/api/integrations", "/api/sync", "/api/health"];

function toLogin(request: NextRequest, error?: string) {
  if (request.nextUrl.pathname.startsWith("/api/")) return NextResponse.json({ error: "unauthorised" }, { status: 401 });
  const login = request.nextUrl.clone();
  login.pathname = "/login";
  login.search = error ? `?error=${error}` : "";
  return NextResponse.redirect(login);
}

export async function middleware(request: NextRequest) {
  if (PUBLIC.some((p) => request.nextUrl.pathname.startsWith(p))) return NextResponse.next();
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  // Built-in login (no Supabase): check the signed session cookie.
  if (!url || !anon || !process.env.SUPABASE_SERVICE_ROLE_KEY) {
    const email = await verifySessionToken(request.cookies.get(SESSION_COOKIE)?.value);
    return email ? NextResponse.next() : toLogin(request);
  }

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
  if (!email || (allowed.length && !allowed.includes(email))) return toLogin(request, email ? "not_allowed" : undefined);
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|ico)$).*)"],
};
