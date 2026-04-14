import type { Metadata } from "next";

import { CategoryLandingPage } from "@/components/library/CategoryLandingPage";
import { getCategoryPageBySlug } from "@/lib/seo-categories";

const SITE_URL = "https://www.thestorymama.club";
const SLUG = "animal-stories-for-children";

export async function generateMetadata(): Promise<Metadata> {
  const config = getCategoryPageBySlug(SLUG)!;
  return {
    title: config.metaTitle,
    description: config.metaDescription,
    alternates: { canonical: `${SITE_URL}/${SLUG}` },
    openGraph: {
      title: config.metaTitle,
      description: config.metaDescription,
      url: `${SITE_URL}/${SLUG}`,
      siteName: "TheStoryMama",
      type: "website",
    },
  };
}

export default async function Page({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const params = await searchParams;
  const page = params.page ? parseInt(params.page) : 1;
  const config = getCategoryPageBySlug(SLUG)!;

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: config.h1,
    description: config.metaDescription,
    url: `${SITE_URL}/${SLUG}`,
    isAccessibleForFree: true,
    audience: { "@type": "Audience", audienceType: "Children" },
    publisher: {
      "@type": "Organization",
      name: "TheStoryMama",
      url: SITE_URL,
    },
  };

  return (
    <>
      <script
        id="category-jsonld"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <CategoryLandingPage config={config} page={page} />
    </>
  );
}
