import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import Google from "next-auth/providers/google";
import { authConfig } from "./auth.config";

/**
 * Full auth config with all providers.
 * Uses JWT-only strategy — no database adapter needed.
 * User data is stored in the JWT token itself.
 */
export const { handlers, signIn, signOut, auth } = NextAuth({
  ...authConfig,
  providers: [
    ...authConfig.providers,
    Credentials({
      name: "Email",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
        name: { label: "Name", type: "text" },
        action: { label: "Action", type: "text" },
      },
      async authorize(credentials) {
        const email = credentials?.email as string;
        const password = credentials?.password as string;
        const name = credentials?.name as string;

        if (!email || !password) return null;

        // For now, any email+password combo works for registration/login
        // In production, connect to a proper database (Supabase, PlanetScale, etc.)
        return {
          id: email,
          email,
          name: name || email.split("@")[0],
        };
      },
    }),
  ],
});
