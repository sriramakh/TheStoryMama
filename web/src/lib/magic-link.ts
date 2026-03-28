import { Resend } from "resend";
import jwt from "jsonwebtoken";

function getResend() {
  return new Resend(process.env.RESEND_API_KEY);
}

function getSecret() {
  return process.env.AUTH_SECRET || process.env.NEXTAUTH_SECRET || "fallback";
}

/**
 * Generate a magic link token (JWT valid for 15 minutes)
 */
export function generateMagicToken(email: string, name?: string): string {
  return jwt.sign(
    { email, name: name || email.split("@")[0], type: "magic-link" },
    getSecret(),
    { expiresIn: "15m" }
  );
}

/**
 * Verify a magic link token
 */
export function verifyMagicToken(token: string): { email: string; name: string } | null {
  try {
    const payload = jwt.verify(token, getSecret()) as { email: string; name: string; type: string };
    if (payload.type !== "magic-link") return null;
    return { email: payload.email, name: payload.name };
  } catch {
    return null;
  }
}

/**
 * Send magic link email via Resend
 */
export async function sendMagicLinkEmail(email: string, magicUrl: string) {
  const { error } = await getResend().emails.send({
    from: "TheStoryMama <hello@thestorymama.club>",
    to: email,
    subject: "Sign in to TheStoryMama",
    html: `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="margin:0; padding:0; background-color:#FFF9EB; font-family:'Nunito',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#FFF9EB; padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="480" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:16px; padding:40px; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
          <tr>
            <td align="center" style="padding-bottom:24px;">
              <h1 style="margin:0; font-size:24px; color:#654321; font-weight:700;">TheStoryMama</h1>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding-bottom:16px;">
              <p style="margin:0; font-size:18px; color:#654321; font-weight:600;">
                Welcome! Click below to sign in
              </p>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding-bottom:24px;">
              <p style="margin:0; font-size:14px; color:#8B7D6B; line-height:1.6;">
                This link will expire in 15 minutes.<br>
                If you didn't request this, you can safely ignore it.
              </p>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding-bottom:32px;">
              <a href="${magicUrl}" style="display:inline-block; padding:14px 32px; background:#FFD6E0; color:#654321; text-decoration:none; border-radius:12px; font-size:16px; font-weight:600;">
                Sign In to TheStoryMama
              </a>
            </td>
          </tr>
          <tr>
            <td align="center">
              <p style="margin:0; font-size:12px; color:#B0A090;">
                Bedtime stories that bring families closer, one page at a time.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`,
  });

  if (error) {
    console.error("Resend error:", error);
    throw new Error(`Failed to send email: ${error.message}`);
  }
}
