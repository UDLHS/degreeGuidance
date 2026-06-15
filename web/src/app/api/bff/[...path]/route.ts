import { getToken } from "next-auth/jwt";
import type { NextRequest } from "next/server";

// Server-side proxy (BFF): the browser calls /api/bff/<...>, this handler reads
// the FastAPI access token from the encrypted Auth.js JWT, attaches it as a
// Bearer header, and forwards to the FastAPI backend. The token never reaches
// the browser (masterplan §11.B). Only admins/superadmins pass.
const API = process.env.API_BASE_URL ?? "http://127.0.0.1:8077";
const ADMIN_ROLES = new Set(["admin", "superadmin"]);

async function proxy(req: NextRequest, ctx: { params: { path?: string[] } }) {
  const token = await getToken({ req, secret: process.env.AUTH_SECRET });
  const accessToken = token?.accessToken as string | undefined;
  const role = token?.role as string | undefined;
  if (!accessToken || !role || !ADMIN_ROLES.has(role)) {
    return Response.json({ detail: "Not authenticated" }, { status: 401 });
  }

  const path = (ctx.params.path ?? []).join("/");
  const url = `${API}/api/${path}${req.nextUrl.search}`;

  const headers = new Headers();
  headers.set("authorization", `Bearer ${accessToken}`);
  const contentType = req.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);

  const init: RequestInit & { duplex?: "half" } = { method: req.method, headers };
  if (req.method !== "GET" && req.method !== "HEAD") {
    init.body = req.body;
    init.duplex = "half"; // required when streaming a request body (undici)
  }

  const upstream = await fetch(url, init);

  const respHeaders = new Headers();
  const upstreamType = upstream.headers.get("content-type");
  if (upstreamType) respHeaders.set("content-type", upstreamType);
  const disposition = upstream.headers.get("content-disposition");
  if (disposition) respHeaders.set("content-disposition", disposition);

  return new Response(upstream.body, { status: upstream.status, headers: respHeaders });
}

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
