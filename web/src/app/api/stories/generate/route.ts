import { NextRequest, NextResponse } from "next/server";
import { backendFetch } from "@/lib/backend";

export async function POST(req: NextRequest) {
  const body = await req.text();
  const res = await backendFetch("/api/v1/stories/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
  const resBody = await res.text();
  return new NextResponse(resBody, {
    status: res.status,
    headers: { "Content-Type": "application/json" },
  });
}
