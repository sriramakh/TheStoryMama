import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { DrizzleAdapter } from "@auth/drizzle-adapter";
import { db, users } from "./db";
import { eq } from "drizzle-orm";
import bcrypt from "bcryptjs";
import { authConfig } from "./auth.config";

/**
 * Full auth config — includes database adapter and credentials provider.
 * Only used in Node.js runtime (API routes, server components), NOT in Edge middleware.
 */
export const { handlers, signIn, signOut, auth } = NextAuth({
  ...authConfig,
  adapter: DrizzleAdapter(db) as ReturnType<typeof DrizzleAdapter>,
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
});
