import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    hasGoogleClientId: !!process.env.GOOGLE_CLIENT_ID,
    googleClientIdPrefix: process.env.GOOGLE_CLIENT_ID?.substring(0, 10) || "NOT SET",
    hasGoogleClientSecret: !!process.env.GOOGLE_CLIENT_SECRET,
    googleSecretPrefix: process.env.GOOGLE_CLIENT_SECRET?.substring(0, 8) || "NOT SET",
    hasNextAuthSecret: !!process.env.NEXTAUTH_SECRET,
    nextAuthUrl: process.env.NEXTAUTH_URL || "NOT SET",
    authTrustHost: process.env.AUTH_TRUST_HOST || "NOT SET",
  });
}
