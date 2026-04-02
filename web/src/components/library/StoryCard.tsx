import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BookOpen } from "lucide-react";
import type { Story } from "@/types/story";
import { API_URL } from "@/lib/constants";

export function StoryCard({ story }: { story: Story }) {
  const coverUrl = story.cover_image_url
    ? `${API_URL}${story.cover_image_url}`
    : null;

  return (
    <Link href={`/stories/${story.id}`}>
      <Card className="group cursor-pointer border-0 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 overflow-hidden h-full">
        {coverUrl ? (
          <div className="h-52 overflow-hidden bg-[var(--color-pastel-cream)]">
            <img
              src={coverUrl}
              alt={story.title}
              className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-500"
              loading="lazy"
            />
          </div>
        ) : (
          <div className="bg-[var(--color-pastel-cream)] h-52 flex items-center justify-center">
            <BookOpen className="h-14 w-14 text-[var(--color-warm-brown)]/20 group-hover:scale-110 transition-transform" />
          </div>
        )}
        <CardContent className="p-4">
          <div className="flex items-center gap-1.5 flex-wrap mb-2">
            {(story.categories || (story.category ? [story.category] : []))
              .slice(0, 3)
              .map((cat: string) => (
                <Badge
                  key={cat}
                  variant="secondary"
                  className="text-[10px] capitalize bg-[var(--color-pastel-cream)] text-[var(--color-warm-brown)] px-2 py-0.5"
                >
                  {cat}
                </Badge>
              ))}
            {story.orientation === "landscape" && (
              <Badge
                variant="secondary"
                className="text-[10px] bg-[var(--color-pastel-sky)] text-blue-700 px-2 py-0.5"
              >
                Landscape
              </Badge>
            )}
            {story.scene_count && (
              <span className="text-[10px] text-muted-foreground ml-auto">
                {story.scene_count} scenes
              </span>
            )}
          </div>
          <h3 className="font-semibold text-[var(--color-warm-brown)] group-hover:text-primary transition-colors line-clamp-2">
            {story.title}
          </h3>
          {story.moral && (
            <p className="mt-1.5 text-xs text-muted-foreground line-clamp-2">
              {story.moral}
            </p>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
