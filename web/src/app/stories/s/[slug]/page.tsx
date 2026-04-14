/**
 * Clean-URL story alias route: /stories/s/aidens-big-race
 *
 * Existing canonical URLs are the numeric-prefixed IDs:
 *   /stories/207_Aidens_Big_Race
 *
 * This route resolves a clean slug to the numeric-prefixed ID and 301-redirects.
 * We keep the numeric URLs canonical (via the main story page's `alternates.canonical`)
 * so inbound links to the old URLs remain authoritative.
 *
 * TODO: once we're ready to switch canonical to clean URLs, swap the redirect direction
 * and update sitemap + canonical tags accordingly.
 */

import { redirect, notFound } from "next/navigation";
import { API_URL } from "@/lib/constants";

interface Story {
  id: string;
  title: string;
}

function normalize(s: string): string {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

async function findStoryIdBySlug(slug: string): Promise<string | null> {
  const target = normalize(slug);
  try {
    // API caps per_page at 100 — paginate
    for (let page = 1; page <= 20; page++) {
      const res = await fetch(
        `${API_URL}/api/v1/library?per_page=100&page=${page}`,
        { next: { revalidate: 3600 } }
      );
      if (!res.ok) break;
      const data = await res.json();
      const stories: Story[] = data.stories || [];
      if (stories.length === 0) break;

      const match = stories.find((s) => {
        const idWithoutPrefix = s.id.replace(/^\d+_/, "");
        return (
          normalize(idWithoutPrefix) === target ||
          normalize(s.title) === target
        );
      });
      if (match) return match.id;
      if (stories.length < 100) break;
    }
    return null;
  } catch {
    return null;
  }
}

export default async function CleanSlugStoryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const storyId = await findStoryIdBySlug(slug);
  if (!storyId) {
    notFound();
  }
  redirect(`/stories/${storyId}`);
}
