import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import Google from "next-auth/providers/google";
import { DrizzleAdapter } from "@auth/drizzle-adapter";
import { db, users } from "./db";
import { eq } from "drizzle-orm";
import bcrypt from "bcryptjs";

export const { handlers, signIn, signOut, auth } = NextAuth({
  adapter: DrizzleAdapter(db) as ReturnType<typeof DrizzleAdapter>,
  session: { strategy: "jwt" },
  pages: {
    signIn: "/auth/signin",
  },
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    Credentials({
      name: "Email",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
        name: { label: "Name", type: "text" },
        action: { label: "Action", type: "text" }, // "login" or "register"
      },
      async authorize(credentials) {
        const email = credentials?.email as string;
        const password = credentials?.password as string;
        const name = credentials?.name as string;
        const action = credentials?.action as string;

        if (!email || !password) return null;

        const existingUser = await db
          .select()
          .from(users)
          .where(eq(users.email, email))
          .get();

        if (action === "register") {
          if (existingUser) {
            throw new Error("Email already registered");
          }
          const hash = await bcrypt.hash(password, 12);
          const id = crypto.randomUUID();
          await db.insert(users).values({
            id,
            email,
            name: name || email.split("@")[0],
            passwordHash: hash,
            provider: "credentials",
          });
          return { id, email, name: name || email.split("@")[0] };
        }

        // Login
        if (!existingUser || !existingUser.passwordHash) {
          return null;
        }

        const valid = await bcrypt.compare(password, existingUser.passwordHash);
        if (!valid) return null;

        return {
          id: existingUser.id,
          email: existingUser.email,
          name: existingUser.name,
          image: existingUser.image,
        };
      },
    }),
  ],
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
  },
});
