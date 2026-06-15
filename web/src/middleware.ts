import NextAuth from "next-auth";

import { authConfig } from "@/auth.config";

// Edge middleware uses the provider-less config; the authorized() callback gates
// every /admin/* route on the admin role and redirects to /admin/login otherwise.
export default NextAuth(authConfig).auth;

export const config = {
  matcher: ["/admin", "/admin/:path*"],
};
