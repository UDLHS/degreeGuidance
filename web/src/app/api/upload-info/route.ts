import { getToken } from "next-auth/jwt";
import type { NextRequest } from "next/server";

// The one browser->API direct call: handbook uploads bypass the BFF because
// Vercel caps proxied request bodies at 4.5 MB (handbooks are 6-15 MB). The
// browser needs to know the API's public base URL, which lives in the
// server-side API_BASE_URL env — this admin-gated route hands it over. It is
// a public URL, not a secret; the gate just keeps the surface tidy.
const API = process.env.API_BASE_URL ?? "http://127.0.0.1:8077";
const ADMIN_ROLES = new Set(["admin", "superadmin"]);

export async function GET(req: NextRequest) {
  const token = await getToken({
    req,
    secret: process.env.AUTH_SECRET,
    secureCookie: process.env.NODE_ENV === "production",
  });
  const role = token?.role as string | undefined;
  if (!role || !ADMIN_ROLES.has(role)) {
    return Response.json({ detail: "Not authenticated" }, { status: 401 });
  }
  return Response.json({ apiBase: API });
}
