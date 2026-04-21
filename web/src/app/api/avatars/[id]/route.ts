import { NextResponse } from "next/server";
import { backendFetch } from "@/lib/backend";

export async function DELETE(
  _req: Request,
  ctx: { params: Promise<{ id: string }> }
) {
  const { id } = await ctx.params;
  const res = await backendFetch(`/api/v1/avatars/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
  const body = await res.text();
  return new NextResponse(body || null, { status: res.status });
}
