import type { Metadata } from "next";
import { Suspense } from "react";
import { CategoryPills } from "@/components/library/CategoryPills";
import { StoryGrid } from "@/components/library/StoryGrid";
import { Skeleton } from "@/components/ui/skeleton";
import { BookOpen, Search } from "lucide-react";

export const metadata: Metadata = {
  title: "Story Library - Free Bedtime Stories",
  description:
    "Browse 1000+ free illustrated bedtime stories for children. Filter by category, art style, and more. New stories added daily!",
};

function StoryGridSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {[...Array(12)].map((_, i) => (
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

export default async function LibraryPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | undefined }>;
}) {
  const params = await searchParams;

  return (
    <div className="min-h-screen bg-[var(--color-pastel-cream)]/30">
      {/* Header */}
      <div className="bg-gradient-to-b from-[var(--color-pastel-lavender)]/20 to-transparent">
        <div className="mx-auto max-w-7xl px-4 pt-10 pb-6 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="h-10 w-10 rounded-xl bg-[var(--color-pastel-lavender)] flex items-center justify-center">
              <BookOpen className="h-5 w-5 text-purple-600" />
            </div>
            <h1 className="text-3xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
              Story Library
            </h1>
          </div>
          <p className="text-muted-foreground">
            Browse our collection of beautifully illustrated bedtime stories —
            all free to read!
          </p>

          {/* Search */}
          <div className="mt-6 relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <form action="/library" method="get">
              <input
                type="text"
                name="search"
                defaultValue={params.search || ""}
                placeholder="Search stories..."
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-border bg-white text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-pastel-pink)] focus:border-transparent"
              />
              {params.category && (
                <input type="hidden" name="category" value={params.category} />
              )}
            </form>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 pb-16 sm:px-6 lg:px-8">
        {/* Category filters */}
        <div className="mb-8">
          <Suspense>
            <CategoryPills />
          </Suspense>
        </div>

        {/* Story grid */}
        <Suspense fallback={<StoryGridSkeleton />}>
          <StoryGrid
            category={params.category}
            search={params.search}
            orientation={params.orientation}
            page={params.page ? parseInt(params.page) : 1}
          />
        </Suspense>
      </div>
    </div>
  );
}
