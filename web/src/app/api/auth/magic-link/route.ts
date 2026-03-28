import { NextRequest, NextResponse } from "next/server";
import { generateMagicToken, sendMagicLinkEmail } from "@/lib/magic-link";

export async function POST(req: NextRequest) {
  try {
    const { email, name } = await req.json();

    if (!email || !email.includes("@")) {
      return NextResponse.json({ error: "Valid email required" }, { status: 400 });
    }

    const token = generateMagicToken(email, name);
    const baseUrl = process.env.NEXTAUTH_URL || process.env.AUTH_URL || "https://www.thestorymama.club";
    const magicUrl = `${baseUrl}/api/auth/verify?token=${token}`;

    await sendMagicLinkEmail(email, magicUrl);

    return NextResponse.json({ ok: true, message: "Check your email!" });
  } catch (e: unknown) {
    console.error("Magic link error:", e);
    return NextResponse.json(
      { error: "Failed to send email. Please try again." },
      { status: 500 }
    );
  }
}
