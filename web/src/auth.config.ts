import type { NextAuthConfig } from "next-auth";

// Edge-safe shared config (no providers / no Node-only code) so middleware can
// import it. The full config (with the Credentials provider) lives in auth.ts.
// The FastAPI access token is kept on the encrypted JWT only — never copied into
// the session object, so it is never exposed to the browser (masterplan §11.B).
export const authConfig = {
  trustHost: true,
  session: { strategy: "jwt" },
  pages: { signIn: "/admin/login" },
  providers: [],
  callbacks: {
    async jwt({ token, user, account, profile }) {
      if (user) {
        // Credentials (admin) sign-in
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        token.accessToken = (user as any).accessToken;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        token.role = (user as any).role;
        token.uid = user.id;
      }
      if (account?.provider === "google" && profile) {
        // Google (student) sign-in — upsert once, store uid in JWT
        const API = process.env.API_BASE_URL ?? "http://127.0.0.1:8077";
        try {
          const res = await fetch(`${API}/api/v1/student/auth`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              google_id: (profile as any).sub,
              email: profile.email,
              name: profile.name,
            }),
            cache: "no-store",
          });
          if (res.ok) {
            const data = await res.json();
            token.uid = data.user_id;
            token.role = "student";
          }
        } catch {
          // Fail open — student can still chat anonymously
        }
      }
      return token;
    },
    session({ session, token }) {
      if (session.user) {
        session.user.role = token.role as string | undefined;
        session.user.id = token.uid as string;
      }
      return session;
    },
    authorized({ auth, request }) {
      const role = auth?.user?.role;
      const isAdmin = role === "admin" || role === "superadmin";
      const { pathname } = request.nextUrl;
      if (pathname === "/admin/login") return true;
      if (pathname.startsWith("/admin")) return isAdmin;
      return true;
    },
  },
} satisfies NextAuthConfig;

export default authConfig;
