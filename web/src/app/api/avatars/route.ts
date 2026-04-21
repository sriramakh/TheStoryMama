import { NextResponse } from "next/server";
import { backendFetch } from "@/lib/backend";

interface Avatar {
  id: string;
  image_url: string;
  [k: string]: unknown;
}

interface ListResponse {
  avatars: Avatar[];
  [k: string]: unknown;
}

export async function GET() {
  const res = await backendFetch("/api/v1/avatars");
  if (!res.ok) {
    return new NextResponse(await res.text(), {
      status: res.status,
      headers: { "Content-Type": "application/json" },
    });
  }
  const data: ListResponse = await res.json();
  // Rewrite backend image paths to our proxy so the browser can load them
  // without knowing the backend host.
  data.avatars = data.avatars.map((a) => ({
    ...a,
    image_url: `/api/avatars/${a.id}/image`,
  }));
  return NextResponse.json(data);
}
