import type { Metadata } from "next";
import { StoryReader } from "@/components/reader/StoryReader";
import { getStory } from "@/lib/api";
import { API_URL } from "@/lib/constants";

interface StoryPageProps {
  params: Promise<{ storyId: string }>;
}

export async function generateMetadata({
  params,
}: StoryPageProps): Promise<Metadata> {
  const { storyId } = await params;
  try {
    const story = await getStory(storyId);
    const characters = story.characters?.map((c) => c.name).join(", ");
    const description = story.moral
      ? `${story.moral} — A bedtime story featuring ${characters}.`
      : `Read "${story.title}" — a beautiful illustrated bedtime story featuring ${characters}.`;
    const imageUrl = `${API_URL}/api/v1/stories/${storyId}/scenes/1/image`;

    return {
      title: story.title,
      description,
      openGraph: {
        title: story.title,
        description,
        siteName: "TheStoryMama",
        type: "article",
        images: [{ url: imageUrl, width: 1024, height: 1536, alt: story.title }],
      },
      twitter: {
        card: "summary_large_image",
        title: story.title,
        description,
        images: [imageUrl],
      },
    };
  } catch {
    return { title: "Story Not Found" };
  }
}

export default async function StoryPage({ params }: StoryPageProps) {
  const { storyId } = await params;
  let story;
  let error = null;

  try {
    story = await getStory(storyId);
  } catch (e) {
    error = e instanceof Error ? e.message : "Story not found";
  }

  if (error || !story) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--color-pastel-cream)]">
        <div className="text-center">
          <p className="text-4xl mb-4">📖</p>
          <h1 className="text-2xl font-bold text-[var(--color-warm-brown)] mb-2">
            Story Not Found
          </h1>
          <p className="text-muted-foreground">
            This story may have wandered off to another adventure.
          </p>
        </div>
      </div>
    );
  }

  return <StoryReader story={story} />;
}
