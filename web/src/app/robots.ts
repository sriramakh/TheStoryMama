import { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: [
          "/",
          "/library",
          "/stories/",
          "/bedtime-stories-for-kids",
          "/animal-stories-for-children",
          "/adventure-stories-for-kids",
          "/fantasy-stories-for-children",
          "/friendship-stories-for-kids",
          "/personalized-bedtime-stories",
          "/pricing",
          "/create",
        ],
        disallow: ["/dashboard", "/api/", "/auth/"],
      },
    ],
    sitemap: "https://www.thestorymama.club/sitemap.xml",
  };
}
