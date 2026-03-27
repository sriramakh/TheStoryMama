import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { db, readingHistory } from "@/lib/db";
import { eq, and, desc, sql } from "drizzle-orm";

// GET /api/reading — get user's reading activity (continue reading + recommendations)
export async function GET() {
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ continueReading: [], recommended: [] });
  }

  const userId = session.user.id;

  // Continue Reading: in-progress stories (not completed), sorted by last read
  const inProgress = await db
    .select()
    .from(readingHistory)
    .where(and(eq(readingHistory.userId, userId), eq(readingHistory.completed, false)))
    .orderBy(desc(readingHistory.lastReadAt))
    .limit(6)
    .all();

  // Get user's most-read categories for recommendations
  const categoryPrefs = await db
    .select({
      category: readingHistory.category,
      count: sql<number>`count(*)`.as("count"),
    })
    .from(readingHistory)
    .where(eq(readingHistory.userId, userId))
    .groupBy(readingHistory.category)
    .orderBy(desc(sql`count(*)`))
    .limit(3)
    .all();

  // Recently completed stories for "read again" suggestions
  const recentlyCompleted = await db
    .select()
    .from(readingHistory)
    .where(and(eq(readingHistory.userId, userId), eq(readingHistory.completed, true)))
    .orderBy(desc(readingHistory.lastReadAt))
    .limit(10)
    .all();

  // All read story IDs (to exclude from recommendations)
  const readStoryIds = new Set([
    ...inProgress.map((r) => r.storyId),
    ...recentlyCompleted.map((r) => r.storyId),
  ]);

  return NextResponse.json({
    continueReading: inProgress.map((r) => ({
      storyId: r.storyId,
      currentScene: r.currentScene,
      totalScenes: r.totalScenes,
      progress: Math.round(((r.currentScene || 1) / (r.totalScenes || 1)) * 100),
      lastReadAt: r.lastReadAt,
      category: r.category,
      animationStyle: r.animationStyle,
    })),
    preferredCategories: categoryPrefs.map((c) => c.category).filter(Boolean),
    recentlyRead: recentlyCompleted.map((r) => r.storyId),
    readStoryIds: Array.from(readStoryIds),
  });
}

// POST /api/reading — save reading progress
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

  const userId = session.user.id;
  const completed = currentScene >= totalScenes;

  // Upsert reading progress
  const existing = await db
    .select()
    .from(readingHistory)
    .where(and(eq(readingHistory.userId, userId), eq(readingHistory.storyId, storyId)))
    .get();

  if (existing) {
    await db
      .update(readingHistory)
      .set({
        currentScene,
        totalScenes,
        completed,
        category: category || existing.category,
        animationStyle: animationStyle || existing.animationStyle,
        lastReadAt: new Date().toISOString(),
      })
      .where(eq(readingHistory.id, existing.id));
  } else {
    await db.insert(readingHistory).values({
      userId,
      storyId,
      currentScene,
      totalScenes,
      completed,
      category,
      animationStyle,
    });
  }

  return NextResponse.json({ ok: true });
}
