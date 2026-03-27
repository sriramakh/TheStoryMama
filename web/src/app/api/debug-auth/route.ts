import { NextResponse } from "next/server";

export async function GET() {
  try {
    // Try importing and checking auth
    const { auth } = await import("@/lib/auth");
    const session = await auth();
    
    return NextResponse.json({
      status: "auth loaded OK",
      session: session ? "exists" : "null",
      envVars: {
        GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID?.substring(0, 15) || "NOT SET",
        AUTH_GOOGLE_ID: process.env.AUTH_GOOGLE_ID?.substring(0, 15) || "NOT SET",
        GOOGLE_CLIENT_SECRET: !!process.env.GOOGLE_CLIENT_SECRET,
        AUTH_GOOGLE_SECRET: !!process.env.AUTH_GOOGLE_SECRET,
        NEXTAUTH_SECRET: !!process.env.NEXTAUTH_SECRET,
        AUTH_SECRET: !!process.env.AUTH_SECRET,
        NEXTAUTH_URL: process.env.NEXTAUTH_URL || "NOT SET",
        AUTH_URL: process.env.AUTH_URL || "NOT SET",
        AUTH_TRUST_HOST: process.env.AUTH_TRUST_HOST || "NOT SET",
      }
    });
  } catch (e: unknown) {
    const error = e as Error;
    return NextResponse.json({
      status: "ERROR",
      error: error.message,
      stack: error.stack?.split("\n").slice(0, 5),
    }, { status: 500 });
  }
}
