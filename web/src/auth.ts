import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import Google from "next-auth/providers/google";

import { authConfig } from "@/auth.config";

const API = process.env.API_BASE_URL ?? "http://127.0.0.1:8077";
const ADMIN_ROLES = new Set(["admin", "superadmin"]);

export const { handlers, auth, signIn, signOut } = NextAuth({
  ...authConfig,
  debug: true,
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    }),
    Credentials({
      credentials: { email: {}, password: {} },
      async authorize(credentials) {
        const email = credentials?.email as string | undefined;
        const password = credentials?.password as string | undefined;
        if (!email || !password) return null;

        const res = await fetch(`${API}/api/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
          cache: "no-store",
        });
        if (!res.ok) return null;
        const data = await res.json();
        // Only admins/superadmins may use the panel (a student token is rejected
        // at the door even though the API would mint one).
        if (!ADMIN_ROLES.has(data.role)) return null;

        // Enrich with the profile (user_id, display_name); /me requires admin,
        // which we just confirmed.
        const meRes = await fetch(`${API}/api/auth/me`, {
          headers: { Authorization: `Bearer ${data.access_token}` },
          cache: "no-store",
        });
        const me = meRes.ok ? await meRes.json() : null;

        return {
          id: me?.user_id ?? email,
          email,
          name: me?.display_name ?? null,
          role: data.role,
          accessToken: data.access_token,
        };
      },
    }),
  ],
});
