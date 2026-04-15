import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getSeriesById, SERIES } from "@/lib/series";
import { API_URL } from "@/lib/constants";
import { BookOpen, Play } from "lucide-react";

const SITE_URL = "https://www.thestorymama.club";

interface Props {
  params: Promise<{ seriesId: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { seriesId } = await params;
  const series = getSeriesById(seriesId);
  if (!series) return { title: "Series Not Found" };

  return {
    title: {
      absolute: `${series.title} — ${series.episodes.length}-Episode Bedtime Series | TheStoryMama`,
    },
    description: series.description,
    alternates: { canonical: `${SITE_URL}/series/${seriesId}` },
    openGraph: {
      title: `${series.title} — TheStoryMama`,
      description: series.description,
      url: `${SITE_URL}/series/${seriesId}`,
      siteName: "TheStoryMama",
      type: "website",
      images: series.episodes[0]
        ? [
            {
              url: `${API_URL}/api/v1/stories/${series.episodes[0].storyId}/scenes/1/image`,
              alt: `${series.title} cover`,
            },
          ]
        : [],
    },
  };
}

export async function generateStaticParams() {
  return SERIES.map((s) => ({ seriesId: s.id }));
}

export default async function SeriesDetailPage({ params }: Props) {
  const { seriesId } = await params;
  const series = getSeriesById(seriesId);
  if (!series) notFound();

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "TVSeries",
    name: series.title,
    description: series.description,
    numberOfEpisodes: series.episodes.length,
    numberOfSeasons: 1,
    audience: { "@type": "Audience", audienceType: "Children" },
    publisher: {
      "@type": "Organization",
      name: "TheStoryMama",
      url: SITE_URL,
    },
    url: `${SITE_URL}/series/${seriesId}`,
    episode: series.episodes.map((ep, idx) => ({
      "@type": "Episode",
      name: ep.title,
      episodeNumber: idx + 1,
      description: ep.synopsis,
      url: `${SITE_URL}/stories/${ep.storyId}`,
    })),
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <div className="min-h-screen bg-[var(--color-pastel-cream)]/30">
        {/* Hero */}
        <div className="bg-gradient-to-b from-[var(--color-pastel-lavender)]/30 to-transparent">
          <div className="mx-auto max-w-5xl px-4 pt-12 pb-8 sm:px-6 lg:px-8">
            <Link
              href="/series"
              className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-4"
            >
              ← All Series
            </Link>
            <div className="flex items-center gap-3 mb-3">
              <div className="h-10 w-10 rounded-xl bg-[var(--color-pastel-pink)] flex items-center justify-center">
                <BookOpen className="h-5 w-5 text-[var(--color-warm-brown)]" />
              </div>
              <h1 className="text-3xl sm:text-4xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
                {series.title}
              </h1>
            </div>
            <p className="text-lg text-foreground/80 mb-2 max-w-3xl">
              {series.tagline}
            </p>
            <p className="text-sm text-muted-foreground max-w-3xl">
              {series.description}
            </p>
            <p className="mt-3 text-xs font-semibold text-[var(--color-warm-brown)] uppercase tracking-wider">
              {series.episodes.length} episodes · Season 1
            </p>
          </div>
        </div>

        {/* Episode grid */}
        <div className="mx-auto max-w-5xl px-4 pb-16 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {series.episodes.map((ep, idx) => {
              const cover = `${API_URL}/api/v1/stories/${ep.storyId}/scenes/1/image`;
              return (
                <Link
                  key={ep.storyId}
                  href={`/stories/${ep.storyId}`}
                  className="group rounded-2xl overflow-hidden bg-white border border-border/40 shadow-sm hover:shadow-lg hover:-translate-y-0.5 transition-all"
                >
                  <div className="relative aspect-[2/3] bg-[var(--color-pastel-cream)] flex items-center justify-center">
                    <img
                      src={cover}
                      alt={`Cover for ${ep.title}`}
                      className="max-h-full max-w-full object-contain group-hover:scale-[1.03] transition-transform duration-500"
                      loading="lazy"
                    />
                    <div className="absolute top-2 left-2 bg-black/60 text-white text-xs px-2 py-1 rounded-md font-semibold">
                      {ep.code}
                    </div>
                    <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/30">
                      <div className="h-12 w-12 rounded-full bg-white flex items-center justify-center shadow-lg">
                        <Play className="h-5 w-5 text-[var(--color-warm-brown)] fill-current ml-0.5" />
                      </div>
                    </div>
                  </div>
                  <div className="p-4">
                    <div className="text-xs text-muted-foreground mb-1">
                      Episode {idx + 1}
                    </div>
                    <h3 className="font-bold text-[var(--color-warm-brown)] mb-1 line-clamp-1">
                      {ep.title}
                    </h3>
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {ep.synopsis}
                    </p>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </>
  );
}
