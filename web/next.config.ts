import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [
      // SEO: alias old /library?category=X to new SEO-friendly category pages
      // These 301 redirects preserve any inbound link equity.
      {
        source: "/library",
        has: [{ type: "query", key: "category", value: "bedtime" }],
        destination: "/bedtime-stories-for-kids",
        permanent: true,
      },
      {
        source: "/library",
        has: [{ type: "query", key: "category", value: "animals" }],
        destination: "/animal-stories-for-children",
        permanent: true,
      },
      {
        source: "/library",
        has: [{ type: "query", key: "category", value: "adventure" }],
        destination: "/adventure-stories-for-kids",
        permanent: true,
      },
      {
        source: "/library",
        has: [{ type: "query", key: "category", value: "fantasy" }],
        destination: "/fantasy-stories-for-children",
        permanent: true,
      },
      {
        source: "/library",
        has: [{ type: "query", key: "category", value: "friendship" }],
        destination: "/friendship-stories-for-kids",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
