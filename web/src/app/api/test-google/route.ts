import { NextResponse } from "next/server";

export async function GET() {
  // Test if we can reach Google's OpenID discovery endpoint
  // This is what NextAuth does internally
  try {
    const res = await fetch(
      "https://accounts.google.com/.well-known/openid-configuration",
      { signal: AbortSignal.timeout(5000) }
    );
    const data = await res.json();

    return NextResponse.json({
      status: "Google OIDC reachable",
      issuer: data.issuer,
      authorization_endpoint: data.authorization_endpoint,
      token_endpoint: data.token_endpoint,
      // Test our env vars
      clientId: (process.env.AUTH_GOOGLE_ID || process.env.GOOGLE_CLIENT_ID || "NOT SET").substring(0, 20),
      hasSecret: !!(process.env.AUTH_GOOGLE_SECRET || process.env.GOOGLE_CLIENT_SECRET),
      hasAuthSecret: !!(process.env.AUTH_SECRET || process.env.NEXTAUTH_SECRET),
    });
  } catch (e: unknown) {
    return NextResponse.json({
      status: "FAILED",
      error: (e as Error).message,
    }, { status: 500 });
  }
}
