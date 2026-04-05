import { MetadataRoute } from "next";

const BASE_URL = "https://www.thestorymama.club";
// Always use production API for sitemap (runs server-side on Vercel, not localhost)
const API_URL = "https://api.thestorymama.club";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const staticPages: MetadataRoute.Sitemap = [
    {
      url: BASE_URL,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 1,
    },
    {
      url: `${BASE_URL}/library`,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 0.9,
    },
    {
      url: `${BASE_URL}/pricing`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.7,
    },
  ];

  // Fetch story list for dynamic pages
  try {
    const res = await fetch(`${API_URL}/api/v1/library?per_page=500`, {
      next: { revalidate: 3600 },
    });
    if (res.ok) {
      const data = await res.json();
      const stories = data.stories || [];
      const storyPages: MetadataRoute.Sitemap = stories.map(
        (s: { id: string }) => ({
          url: `${BASE_URL}/stories/${s.id}`,
          lastModified: new Date(),
          changeFrequency: "monthly" as const,
          priority: 0.6,
        })
      );
      return [...staticPages, ...storyPages];
    }
  } catch {
    // API unavailable — return static pages only
  }

  return staticPages;
}
