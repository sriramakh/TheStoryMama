import { NextRequest, NextResponse } from "next/server";
import { backendFetch } from "@/lib/backend";

export async function POST(req: NextRequest) {
  const form = await req.formData();
  const res = await backendFetch("/api/v1/avatars/create", {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    return new NextResponse(await res.text(), {
      status: res.status,
      headers: { "Content-Type": "application/json" },
    });
  }
  const avatar = await res.json();
  // Rewrite image_url to the Next.js proxy path.
  avatar.image_url = `/api/avatars/${avatar.id}/image`;
  return NextResponse.json(avatar);
}
