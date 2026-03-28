import { NextRequest, NextResponse } from "next/server";
import { verifyMagicToken } from "@/lib/magic-link";
import { encode } from "next-auth/jwt";

export async function GET(req: NextRequest) {
  const token = req.nextUrl.searchParams.get("token");

  if (!token) {
    return NextResponse.redirect(new URL("/auth/signin?error=missing-token", req.url));
  }

  const user = verifyMagicToken(token);
  if (!user) {
    return NextResponse.redirect(new URL("/auth/signin?error=invalid-token", req.url));
  }

  // Create a NextAuth-compatible JWT session
  const secret = process.env.AUTH_SECRET || process.env.NEXTAUTH_SECRET || "";
  const sessionToken = await encode({
    token: {
      id: user.email,
      email: user.email,
      name: user.name,
      picture: "",
    } as Record<string, unknown>,
    secret,
    maxAge: 30 * 24 * 60 * 60, // 30 days
  } as Parameters<typeof encode>[0]);

  // Set the session cookie and redirect to home
  const response = NextResponse.redirect(new URL("/", req.url));

  response.cookies.set("authjs.session-token", sessionToken, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: 30 * 24 * 60 * 60,
  });

  return response;
}
