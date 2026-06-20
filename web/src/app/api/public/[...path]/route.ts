import type { NextRequest } from "next/server";

// Server-side proxy for the PUBLIC student endpoints (reference/eligibility/
// recommendations) -- no auth, anyone may call these. Still proxied through
// Next.js (not called directly from the browser) so the FastAPI base
// URL/port never has to be exposed and no CORS configuration is needed,
// matching the pattern used for the admin BFF.
const API = process.env.API_BASE_URL ?? "http://127.0.0.1:8077";

async function proxy(req: NextRequest, ctx: { params: { path?: string[] } }) {
  const path = (ctx.params.path ?? []).join("/");
  const url = `${API}/api/v1/${path}${req.nextUrl.search}`;

  const headers = new Headers();
  const contentType = req.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);

  const init: RequestInit & { duplex?: "half" } = { method: req.method, headers };
  if (req.method !== "GET" && req.method !== "HEAD" && req.body) {
    init.body = req.body;
    init.duplex = "half";
  }

  const upstream = await fetch(url, init);
  const respHeaders = new Headers();
  const upstreamType = upstream.headers.get("content-type");
  if (upstreamType) respHeaders.set("content-type", upstreamType);

  return new Response(upstream.body, { status: upstream.status, headers: respHeaders });
}

export const GET = proxy;
export const POST = proxy;
