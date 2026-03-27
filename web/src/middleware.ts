import NextAuth from "next-auth";
import { authConfig } from "@/lib/auth.config";

// Edge-compatible middleware — uses auth.config.ts (no database imports)
export default NextAuth(authConfig).auth;

export const config = {
  matcher: ["/dashboard/:path*", "/create/:path*"],
};
