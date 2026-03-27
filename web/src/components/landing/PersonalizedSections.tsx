"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BookOpen, Clock, Sparkles } from "lucide-react";
import { API_URL } from "@/lib/constants";

interface ReadingEntry {
  storyId: string;
  currentScene: number;
  totalScenes: number;
  progress: number;
  lastReadAt: string;
  category: string;
  animationStyle: string;
}

interface StoryData {
  id: string;
  title: string;
  cover_image_url: string;
  category: string;
  categories: string[];
  animation_style: string;
  scene_count: number;
  moral?: string;
}

export function PersonalizedSections() {
  const [continueReading, setContinueReading] = useState<ReadingEntry[]>([]);
  const [recommended, setRecommended] = useState<StoryData[]>([]);
  const [storyDetails, setStoryDetails] = useState<Record<string, StoryData>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        // Get reading activity
        const readingRes = await fetch("/api/reading");
        if (!readingRes.ok) {
          setLoading(false);
          return;
        }
        const readingData = await readingRes.json();

        if (
          !readingData.continueReading?.length &&
          !readingData.preferredCategories?.length
        ) {
          setLoading(false);
          return;
        }

        setContinueReading(readingData.continueReading || []);

        // Fetch story details for continue reading entries
        const details: Record<string, StoryData> = {};
        for (const entry of readingData.continueReading || []) {
          try {
            const res = await fetch(
              `${API_URL}/api/v1/stories/${entry.storyId}`
            );
            if (res.ok) {
              const story = await res.json();
              details[entry.storyId] = story;
            }
          } catch {}
        }
        setStoryDetails(details);

        // Get recommendations based on preferred categories
        const prefCats = readingData.preferredCategories || [];
        const readIds = new Set(readingData.readStoryIds || []);

        if (prefCats.length > 0) {
          // Fetch stories from preferred categories
          const recStories: StoryData[] = [];
          for (const cat of prefCats.slice(0, 2)) {
            try {
              const res = await fetch(
                `${API_URL}/api/v1/library?category=${cat}&per_page=10`
              );
              if (res.ok) {
                const data = await res.json();
                for (const s of data.stories || []) {
                  if (!readIds.has(s.id) && !recStories.find((r) => r.id === s.id)) {
                    recStories.push(s);
                  }
                }
              }
            } catch {}
          }
          setRecommended(recStories.slice(0, 6));
        }
      } catch {
        // Not logged in or error — just hide sections
      }
      setLoading(false);
    }

    loadData();
  }, []);

  if (loading || (!continueReading.length && !recommended.length)) {
    return null;
  }

  return (
    <>
      {/* Continue Reading */}
      {continueReading.length > 0 && (
        <section className="py-10 sm:py-14">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-2 mb-6">
              <Clock className="h-5 w-5 text-[var(--color-pastel-pink)]" />
              <h2 className="text-2xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
                Continue Reading
              </h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {continueReading.map((entry) => {
                const story = storyDetails[entry.storyId];
                return (
                  <Link
                    key={entry.storyId}
                    href={`/stories/${entry.storyId}`}
                  >
                    <Card className="group cursor-pointer border-0 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 overflow-hidden">
                      <div className="flex gap-3 p-3">
                        {/* Cover thumbnail */}
                        <div className="flex-shrink-0 w-20 h-28 rounded-lg overflow-hidden bg-[var(--color-pastel-cream)]">
                          {story?.cover_image_url ? (
                            <img
                              src={`${API_URL}${story.cover_image_url}`}
                              alt={story?.title || "Story"}
                              className="w-full h-full object-cover"
                              loading="lazy"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center">
                              <BookOpen className="h-6 w-6 text-[var(--color-warm-brown)]/20" />
                            </div>
                          )}
                        </div>

                        {/* Story info */}
                        <div className="flex-1 min-w-0 flex flex-col justify-between">
                          <div>
                            <h3 className="font-semibold text-sm text-[var(--color-warm-brown)] line-clamp-2 group-hover:text-primary transition-colors">
                              {story?.title || entry.storyId.replace(/_/g, " ")}
                            </h3>
                            {entry.category && (
                              <Badge
                                variant="secondary"
                                className="text-[10px] capitalize bg-[var(--color-pastel-cream)] text-[var(--color-warm-brown)] mt-1"
                              >
                                {entry.category}
                              </Badge>
                            )}
                          </div>

                          {/* Progress bar */}
                          <div className="mt-2">
                            <div className="flex items-center justify-between text-[10px] text-muted-foreground mb-1">
                              <span>
                                Scene {entry.currentScene} of{" "}
                                {entry.totalScenes}
                              </span>
                              <span>{entry.progress}%</span>
                            </div>
                            <div className="h-1.5 rounded-full bg-[var(--color-pastel-cream)]">
                              <div
                                className="h-full rounded-full bg-gradient-to-r from-[var(--color-pastel-pink)] to-[var(--color-pastel-lavender)]"
                                style={{ width: `${entry.progress}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </Card>
                  </Link>
                );
              })}
            </div>
          </div>
        </section>
      )}

      {/* Recommended for You */}
      {recommended.length > 0 && (
        <section className="py-10 sm:py-14 bg-[var(--color-pastel-cream)]/30">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-2 mb-6">
              <Sparkles className="h-5 w-5 text-[var(--color-pastel-lavender)]" />
              <h2 className="text-2xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
                Recommended for You
              </h2>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
              {recommended.map((story) => (
                <Link key={story.id} href={`/stories/${story.id}`}>
                  <Card className="group cursor-pointer border-0 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 overflow-hidden h-full">
                    <div className="h-36 sm:h-44 overflow-hidden bg-[var(--color-pastel-cream)]">
                      <img
                        src={`${API_URL}${story.cover_image_url}`}
                        alt={story.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        loading="lazy"
                      />
                    </div>
                    <CardContent className="p-2.5">
                      <h3 className="font-semibold text-xs text-[var(--color-warm-brown)] line-clamp-2 group-hover:text-primary transition-colors">
                        {story.title}
                      </h3>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}
    </>
  );
}
