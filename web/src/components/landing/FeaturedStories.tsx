import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BookOpen } from "lucide-react";
import { API_URL } from "@/lib/constants";

const STYLE_LABELS: Record<string, string> = {
  animation_movie: "Animation Movie",
  claymation: "Claymation",
  paper_cutout: "Paper Cutout",
  glowlight_fantasy: "Glowlight Fantasy",
  felt_plushie: "Felt & Plushie",
  stained_glass: "Stained Glass",
  toy_diorama: "Toy Diorama",
  crochet_amigurumi: "Crochet",
  candy_clay: "Candy Clay",
  picture_book_collage: "Collage",
};

async function getFeaturedStories() {
  try {
    const res = await fetch(`${API_URL}/api/v1/library/featured`, {
      next: { revalidate: 300 }, // Cache for 5 minutes
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.stories || [];
  } catch {
    return [];
  }
}

export async function FeaturedStories() {
  const stories = await getFeaturedStories();

  if (stories.length === 0) {
    return null;
  }

  return (
    <section className="py-16 sm:py-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)] sm:text-4xl">
            Featured Stories
          </h2>
          <p className="mt-3 text-muted-foreground text-lg">
            Handpicked tales your little ones will adore
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {stories.map(
            (story: {
              id: string;
              title: string;
              category?: string;
              animation_style?: string;
              cover_image_url?: string;
              moral?: string;
              scene_count?: number;
            }) => (
              <Link key={story.id} href={`/stories/${story.id}`}>
                <Card className="group cursor-pointer border-0 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 overflow-hidden">
                  <div className="h-52 overflow-hidden bg-[var(--color-pastel-cream)]">
                    <img
                      src={`${API_URL}${story.cover_image_url}`}
                      alt={story.title}
                      className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                  </div>
                  <CardContent className="p-5">
                    <div className="flex items-center gap-2 mb-2">
                      {story.category && (
                        <Badge
                          variant="secondary"
                          className="text-xs capitalize bg-[var(--color-pastel-cream)] text-[var(--color-warm-brown)]"
                        >
                          {story.category}
                        </Badge>
                      )}
                      <span className="text-xs text-muted-foreground">
                        {STYLE_LABELS[story.animation_style || ""] ||
                          story.animation_style}
                      </span>
                    </div>
                    <h3 className="font-semibold text-[var(--color-warm-brown)] group-hover:text-primary transition-colors">
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
            )
          )}
        </div>

        <div className="text-center mt-10">
          <Link
            href="/library"
            className="inline-flex items-center gap-2 text-primary font-medium hover:underline"
          >
            <BookOpen className="h-4 w-4" />
            Browse all stories
          </Link>
        </div>
      </div>
    </section>
  );
}
