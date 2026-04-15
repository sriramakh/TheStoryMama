import type { Metadata } from "next";
import { StoryReader } from "@/components/reader/StoryReader";
import { getStory } from "@/lib/api";
import { API_URL } from "@/lib/constants";
import { findSeriesContainingStory } from "@/lib/series";

const SITE_URL = "https://www.thestorymama.club";

interface StoryPageProps {
  params: Promise<{ storyId: string }>;
}

function buildDescription(story: {
  title: string;
  moral?: string;
  characters?: { name: string }[];
  setting?: string;
  categories?: string[];
  category?: string;
}): string {
  const cats = story.categories?.length
    ? story.categories[0]
    : story.category || "wonder";
  const tagline = story.moral
    ? story.moral
    : `A beautifully illustrated bedtime story featuring ${story.characters?.map((c) => c.name).join(", ") || "charming characters"}`;
  return `${tagline}. Read ${story.title} free online at TheStoryMama — a beautifully illustrated bedtime story for children about ${cats}.`;
}

export async function generateMetadata({
  params,
}: StoryPageProps): Promise<Metadata> {
  const { storyId } = await params;
  try {
    const story = await getStory(storyId);
    const description = buildDescription(story);
    const imageUrl = `${API_URL}/api/v1/stories/${storyId}/scenes/1/image`;
    const canonical = `${SITE_URL}/stories/${storyId}`;

    return {
      // Use absolute so the suffix isn't stripped by the layout template
      title: {
        absolute: `${story.title} — Free Bedtime Story for Kids | TheStoryMama`,
      },
      description,
      alternates: { canonical },
      openGraph: {
        title: `${story.title} — Free Bedtime Story for Kids | TheStoryMama`,
        description,
        siteName: "TheStoryMama",
        type: "article",
        url: canonical,
        images: [
          {
            url: imageUrl,
            width: story.orientation === "landscape" ? 1536 : 1024,
            height: story.orientation === "landscape" ? 1024 : 1536,
            alt: `Cover illustration for ${story.title}`,
          },
        ],
      },
      twitter: {
        card: "summary_large_image",
        title: `${story.title} — Free Bedtime Story`,
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

  const canonical = `${SITE_URL}/stories/${storyId}`;
  const imageUrl = `${API_URL}/api/v1/stories/${storyId}/scenes/1/image`;
  const category = story.categories?.[0] || story.category || "children";

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Book",
    name: story.title,
    description: story.moral || buildDescription(story),
    genre: category,
    audience: { "@type": "Audience", audienceType: "Children" },
    publisher: {
      "@type": "Organization",
      name: "TheStoryMama",
      url: SITE_URL,
    },
    image: imageUrl,
    url: canonical,
    isAccessibleForFree: true,
    numberOfPages: story.scenes?.length ?? 0,
    inLanguage: "en",
    ...(story.characters && story.characters.length > 0 && {
      character: story.characters.map((c) => ({
        "@type": "Person",
        name: c.name,
      })),
    }),
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      {/* Client-side reader (primary UX) */}
      <StoryReader
        story={story}
        seriesNav={(() => {
          const found = findSeriesContainingStory(storyId);
          if (!found) return undefined;
          const { series, episodeIndex } = found;
          const ep = series.episodes[episodeIndex];
          const prev = episodeIndex > 0 ? series.episodes[episodeIndex - 1] : undefined;
          const next =
            episodeIndex < series.episodes.length - 1
              ? series.episodes[episodeIndex + 1]
              : undefined;
          return {
            seriesId: series.id,
            seriesTitle: series.title,
            episodeCode: ep.code,
            episodeIndex,
            totalEpisodes: series.episodes.length,
            prev: prev
              ? { storyId: prev.storyId, title: prev.title, code: prev.code }
              : undefined,
            next: next
              ? { storyId: next.storyId, title: next.title, code: next.code }
              : undefined,
          };
        })()}
      />

      {/* SEO: full story transcript — visible to crawlers, hidden from users */}
      <article className="sr-only" aria-hidden="true">
        <h1>{story.title}</h1>
        {story.moral && <p>{story.moral}</p>}
        {story.setting && <p>Setting: {story.setting}</p>}
        {story.characters && story.characters.length > 0 && (
          <section>
            <h2>Characters</h2>
            <ul>
              {story.characters.map((c) => (
                <li key={c.name}>
                  <strong>{c.name}</strong>
                  {c.type ? ` — ${c.type}` : ""}
                  {c.description ? `: ${c.description}` : ""}
                </li>
              ))}
            </ul>
          </section>
        )}
        <section>
          <h2>Full Story</h2>
          {story.scenes.map((scene) => (
            <p key={scene.scene_number}>
              <span>Scene {scene.scene_number}: </span>
              {scene.text}
            </p>
          ))}
        </section>
      </article>
    </>
  );
}
