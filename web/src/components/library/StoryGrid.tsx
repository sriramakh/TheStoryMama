import Link from "next/link";
import { StoryCard } from "./StoryCard";
import { Button } from "@/components/ui/button";
import { getLibraryStories } from "@/lib/api";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface StoryGridProps {
  category?: string;
  search?: string;
  page?: number;
}

export async function StoryGrid({
  category,
  search,
  page = 1,
}: StoryGridProps) {
  let stories;
  let error = null;

  try {
    stories = await getLibraryStories({
      page,
      per_page: 20,
      category,
      search,
    });
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed to load stories";
  }

  if (error || !stories) {
    return (
      <div className="text-center py-16">
        <p className="text-muted-foreground text-lg">
          Stories are being prepared! Check back soon.
        </p>
        <p className="text-sm text-muted-foreground mt-2">
          Our library is loading up with magical bedtime stories.
        </p>
      </div>
    );
  }

  if (stories.stories.length === 0) {
    return (
      <div className="text-center py-16">
        <p className="text-2xl mb-2">📚</p>
        <p className="text-muted-foreground text-lg">No stories found</p>
        <p className="text-sm text-muted-foreground mt-1">
          Try a different category or search term
        </p>
      </div>
    );
  }

  const totalPages = Math.ceil(stories.total / stories.per_page);

  function buildPageUrl(p: number) {
    const params = new URLSearchParams();
    params.set("page", String(p));
    if (category) params.set("category", category);
    if (search) params.set("search", search);
    return `/library?${params.toString()}`;
  }

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {stories.stories.map((story) => (
          <StoryCard key={story.id} story={story} />
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-10">
          {page > 1 && (
            <Link href={buildPageUrl(page - 1)}>
              <Button
                variant="outline"
                size="sm"
                className="gap-1 rounded-xl"
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
            </Link>
          )}
          <span className="text-sm text-muted-foreground px-4">
            Page {page} of {totalPages}
          </span>
          {page < totalPages && (
            <Link href={buildPageUrl(page + 1)}>
              <Button
                variant="outline"
                size="sm"
                className="gap-1 rounded-xl"
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </Link>
          )}
        </div>
      )}
    </>
  );
}
