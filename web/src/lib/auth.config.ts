import type { NextAuthConfig } from "next-auth";

/**
 * Edge-compatible auth config — NO providers, NO database imports.
 * Used by middleware for route protection only.
 * Providers are added in auth.ts (Node.js runtime).
 */
export const authConfig: NextAuthConfig = {
  session: { strategy: "jwt" },
  pages: {
    signIn: "/auth/signin",
  },
  providers: [], // Providers defined in auth.ts only
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user && token.id) {
        session.user.id = token.id as string;
      }
      return session;
    },
    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user;
      const isProtected =
        nextUrl.pathname.startsWith("/dashboard") ||
        nextUrl.pathname.startsWith("/create");

      if (isProtected && !isLoggedIn) {
        return Response.redirect(
          new URL(`/auth/signin?callbackUrl=${nextUrl.pathname}`, nextUrl)
        );
      }
      return true;
    },
  },
};
