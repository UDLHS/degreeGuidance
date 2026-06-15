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
    jwt({ token, user }) {
      if (user) {
        token.accessToken = user.accessToken;
        token.role = user.role;
        token.uid = user.id;
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
