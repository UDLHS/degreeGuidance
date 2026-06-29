import { auth } from "@/auth";
import type { NextRequest } from "next/server";

// Server-side proxy for authenticated student endpoints.
// Reads the session server-side, injects X-Student-Id header, then forwards
// to the FastAPI backend. The browser never touches the backend URL directly.
const API = process.env.API_BASE_URL ?? "http://127.0.0.1:8077";

async function proxy(req: NextRequest, ctx: { params: Promise<{ path?: string[] }> }) {
  const session = await auth();
  if (!session?.user?.id || session.user.role !== "student") {
    return new Response(JSON.stringify({ detail: "Unauthorized" }), {
      status: 401,
      headers: { "content-type": "application/json" },
    });
  }

  const { path } = await ctx.params;
  const segments = path ?? [];
  const url = `${API}/api/v1/student/${segments.join("/")}${req.nextUrl.search}`;

  const headers = new Headers();
  headers.set("x-student-id", session.user.id);
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
