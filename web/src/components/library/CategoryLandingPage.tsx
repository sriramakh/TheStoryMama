import Link from "next/link";
import { Suspense } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { StoryGrid } from "./StoryGrid";
import { Heart, BookOpen } from "lucide-react";
import type { CategoryPageConfig } from "@/lib/seo-categories";

function StoryGridSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {[...Array(8)].map((_, i) => (
        <div key={i} className="rounded-2xl overflow-hidden">
          <Skeleton className="h-52 w-full" />
          <div className="p-4 space-y-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-5 w-full" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function CategoryLandingPage({
  config,
  page = 1,
}: {
  config: CategoryPageConfig;
  page?: number;
}) {
  return (
    <div className="min-h-screen bg-[var(--color-pastel-cream)]/30">
      {/* Header with intro copy */}
      <div className="bg-gradient-to-b from-[var(--color-pastel-lavender)]/20 to-transparent">
        <div className="mx-auto max-w-5xl px-4 pt-12 pb-8 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="h-10 w-10 rounded-xl bg-[var(--color-pastel-lavender)] flex items-center justify-center">
              <BookOpen className="h-5 w-5 text-purple-600" />
            </div>
            <h1 className="text-3xl sm:text-4xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
              {config.h1}
            </h1>
          </div>
          <p className="text-base text-foreground/80 leading-relaxed max-w-3xl">
            {config.introCopy}
          </p>

          {/* Inline CTA to /create */}
          <div className="mt-6">
            <Link href="/create">
              <Button className="rounded-2xl bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)] shadow-md gap-2">
                <Heart className="h-4 w-4" />
                {config.ctaLabel}
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Story grid */}
      <div className="mx-auto max-w-7xl px-4 pb-16 sm:px-6 lg:px-8">
        <Suspense fallback={<StoryGridSkeleton />}>
          <StoryGrid category={config.categoryId} page={page} />
        </Suspense>
      </div>

      {/* Secondary CTA */}
      <div className="bg-gradient-to-r from-[var(--color-pastel-pink)]/30 via-[var(--color-pastel-lavender)]/30 to-[var(--color-pastel-sky)]/30">
        <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl font-bold text-[var(--color-warm-brown)] mb-3">
            Make your child the hero of their own story
          </h2>
          <p className="text-muted-foreground mb-6">
            Create a personalized illustrated story starring your little one —
            their name, their world, their adventure.
          </p>
          <Link href="/create">
            <Button
              size="lg"
              className="rounded-2xl bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)] shadow-lg gap-2"
            >
              <Heart className="h-5 w-5" />
              Create Your Story
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
