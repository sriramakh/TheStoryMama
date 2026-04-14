import { MetadataRoute } from "next";
import { CATEGORY_PAGES } from "@/lib/seo-categories";

const BASE_URL = "https://www.thestorymama.club";
// Always use production API for sitemap (runs server-side on Vercel, not localhost)
const API_URL = "https://api.thestorymama.club";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const now = new Date();

  const staticPages: MetadataRoute.Sitemap = [
    {
      url: BASE_URL,
      lastModified: now,
      changeFrequency: "daily",
      priority: 1,
    },
    {
      url: `${BASE_URL}/library`,
      lastModified: now,
      changeFrequency: "weekly",
      priority: 0.9,
    },
    {
      url: `${BASE_URL}/personalized-bedtime-stories`,
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.9,
    },
    {
      url: `${BASE_URL}/pricing`,
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.7,
    },
    {
      url: `${BASE_URL}/create`,
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.8,
    },
  ];

  // SEO category landing pages
  const categoryPages: MetadataRoute.Sitemap = CATEGORY_PAGES.map((c) => ({
    url: `${BASE_URL}/${c.slug}`,
    lastModified: now,
    changeFrequency: "weekly" as const,
    priority: 0.85,
  }));

  // Dynamic story pages — API caps per_page at 100, so we paginate
  try {
    const allStories: { id: string }[] = [];
    for (let page = 1; page <= 20; page++) {
      const res = await fetch(
        `${API_URL}/api/v1/library?per_page=100&page=${page}`,
        { next: { revalidate: 3600 } }
      );
      if (!res.ok) break;
      const data = await res.json();
      const stories = data.stories || [];
      if (stories.length === 0) break;
      allStories.push(...stories);
      if (stories.length < 100) break;
    }

    const storyPages: MetadataRoute.Sitemap = allStories.map((s) => ({
      url: `${BASE_URL}/stories/${s.id}`,
      lastModified: now,
      changeFrequency: "monthly" as const,
      priority: 0.6,
    }));
    return [...staticPages, ...categoryPages, ...storyPages];
  } catch {
    // API unavailable — return static + category pages only
  }

  return [...staticPages, ...categoryPages];
}
