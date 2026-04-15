import type { Metadata } from "next";
import Link from "next/link";
import { SERIES } from "@/lib/series";
import { API_URL } from "@/lib/constants";
import { BookOpen, ChevronRight } from "lucide-react";

const SITE_URL = "https://www.thestorymama.club";

export const metadata: Metadata = {
  title: "Story Series — Chapter-by-Chapter Bedtime Adventures",
  description:
    "Recurring characters, new adventures every episode. Follow Caleb and friends through a full season of warm, illustrated bedtime stories — free to read online.",
  alternates: { canonical: `${SITE_URL}/series` },
  openGraph: {
    title: "Story Series — TheStoryMama",
    description:
      "Recurring characters, new adventures every episode. Follow Caleb and friends through a full season of illustrated bedtime stories.",
    url: `${SITE_URL}/series`,
    siteName: "TheStoryMama",
    type: "website",
  },
};

export default function SeriesListPage() {
  return (
    <div className="min-h-screen bg-[var(--color-pastel-cream)]/30">
      <div className="bg-gradient-to-b from-[var(--color-pastel-lavender)]/20 to-transparent">
        <div className="mx-auto max-w-5xl px-4 pt-12 pb-8 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3 mb-3">
            <div className="h-10 w-10 rounded-xl bg-[var(--color-pastel-lavender)] flex items-center justify-center">
              <BookOpen className="h-5 w-5 text-purple-600" />
            </div>
            <h1 className="text-3xl sm:text-4xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
              Story Series
            </h1>
          </div>
          <p className="text-base text-foreground/80 leading-relaxed max-w-3xl">
            Recurring characters, new adventures every episode. Our story series
            follow the same lovable cast through a full season — perfect for
            bedtime routines where your little one wants to come back for more.
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-5xl px-4 pb-16 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {SERIES.map((s) => {
            const firstEp = s.episodes[0];
            const cover = firstEp
              ? `${API_URL}/api/v1/stories/${firstEp.storyId}/scenes/1/image`
              : null;
            return (
              <Link
                key={s.id}
                href={`/series/${s.id}`}
                className="group rounded-2xl overflow-hidden bg-white border border-border/40 shadow-sm hover:shadow-lg hover:-translate-y-0.5 transition-all"
              >
                {cover && (
                  <div className="h-56 overflow-hidden bg-[var(--color-pastel-cream)]">
                    <img
                      src={cover}
                      alt={`${s.title} — series cover`}
                      className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-500"
                      loading="lazy"
                    />
                  </div>
                )}
                <div className="p-5">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)]">
                      {s.episodes.length} episodes
                    </span>
                  </div>
                  <h2 className="text-xl font-bold text-[var(--color-warm-brown)] mb-1">
                    {s.title}
                  </h2>
                  <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                    {s.tagline}
                  </p>
                  <span className="inline-flex items-center gap-1 text-sm font-medium text-[var(--color-warm-brown)] group-hover:text-primary transition-colors">
                    Start watching <ChevronRight className="h-4 w-4" />
                  </span>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
