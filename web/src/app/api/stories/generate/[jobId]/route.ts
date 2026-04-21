import { NextResponse } from "next/server";
import { backendFetch } from "@/lib/backend";

export async function GET(
  _req: Request,
  ctx: { params: Promise<{ jobId: string }> }
) {
  const { jobId } = await ctx.params;
  const res = await backendFetch(
    `/api/v1/stories/generate/${encodeURIComponent(jobId)}`
  );
  const body = await res.text();
  return new NextResponse(body, {
    status: res.status,
    headers: { "Content-Type": "application/json" },
  });
}
