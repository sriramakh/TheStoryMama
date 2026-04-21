import { NextResponse } from "next/server";
import { API_URL } from "@/lib/constants";

export async function GET(
  _req: Request,
  ctx: { params: Promise<{ id: string }> }
) {
  const { id } = await ctx.params;
  const res = await fetch(
    `${API_URL}/api/v1/avatars/${encodeURIComponent(id)}/image`
  );
  if (!res.ok) {
    return new NextResponse("Not found", { status: res.status });
  }
  const buf = await res.arrayBuffer();
  return new NextResponse(buf, {
    status: 200,
    headers: {
      "Content-Type": res.headers.get("Content-Type") || "image/png",
      "Cache-Control": "private, max-age=600",
    },
  });
}
