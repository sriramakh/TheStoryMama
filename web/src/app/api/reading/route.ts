import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";

// In-memory reading history (per-server instance, resets on redeploy)
// For production, replace with Supabase/PlanetScale/Redis
const readingHistory = new Map<string, Map<string, {
  storyId: string;
  currentScene: number;
  totalScenes: number;
  completed: boolean;
  category: string;
  animationStyle: string;
  lastReadAt: string;
}>>();

function getUserHistory(userId: string) {
  if (!readingHistory.has(userId)) {
    readingHistory.set(userId, new Map());
  }
  return readingHistory.get(userId)!;
}

// GET /api/reading
export async function GET() {
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ continueReading: [], recommended: [] });
  }

  const history = getUserHistory(session.user.id);

  const inProgress = Array.from(history.values())
    .filter((r) => !r.completed)
    .sort((a, b) => b.lastReadAt.localeCompare(a.lastReadAt))
    .slice(0, 6)
    .map((r) => ({
      storyId: r.storyId,
      currentScene: r.currentScene,
      totalScenes: r.totalScenes,
      progress: Math.round((r.currentScene / r.totalScenes) * 100),
      lastReadAt: r.lastReadAt,
      category: r.category,
      animationStyle: r.animationStyle,
    }));

  // Get preferred categories from reading history
  const catCounts = new Map<string, number>();
  for (const r of history.values()) {
    if (r.category) {
      catCounts.set(r.category, (catCounts.get(r.category) || 0) + 1);
    }
  }
  const preferredCategories = Array.from(catCounts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([cat]) => cat);

  const readStoryIds = Array.from(history.keys());

  return NextResponse.json({
    continueReading: inProgress,
    preferredCategories,
    readStoryIds,
  });
}

// POST /api/reading
export async function POST(req: NextRequest) {
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  const body = await req.json();
  const { storyId, currentScene, totalScenes, category, animationStyle } = body;

  if (!storyId) {
    return NextResponse.json({ error: "storyId required" }, { status: 400 });
  }

  const history = getUserHistory(session.user.id);
  history.set(storyId, {
    storyId,
    currentScene,
    totalScenes,
    completed: currentScene >= totalScenes,
    category: category || "",
    animationStyle: animationStyle || "",
    lastReadAt: new Date().toISOString(),
  });

  return NextResponse.json({ ok: true });
}
