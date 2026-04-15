"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, Download, X, Share2, Check, Film } from "lucide-react";
import { API_URL } from "@/lib/constants";
import type { Story } from "@/types/story";

interface SeriesNav {
  seriesId: string;
  seriesTitle: string;
  episodeCode: string;
  episodeIndex: number;
  totalEpisodes: number;
  prev?: { storyId: string; title: string; code: string };
  next?: { storyId: string; title: string; code: string };
}

export function StoryReader({
  story,
  seriesNav,
}: {
  story: Story;
  seriesNav?: SeriesNav;
}) {
  const [currentScene, setCurrentScene] = useState(0);
  const totalScenes = story.scenes.length;
  const scene = story.scenes[currentScene];
  const router = useRouter();
  const [shared, setShared] = useState(false);
  const touchStartX = useRef(0);
  const touchEndX = useRef(0);

  async function handleShare() {
    const url = window.location.href;
    const text = `Read "${story.title}" — a beautiful bedtime story on TheStoryMama`;

    // Use native share on mobile (WhatsApp, iMessage, etc.)
    if (navigator.share) {
      try {
        await navigator.share({ title: story.title, text, url });
        return;
      } catch {}
    }

    // Fallback: copy link
    try {
      await navigator.clipboard.writeText(url);
      setShared(true);
      setTimeout(() => setShared(false), 2000);
    } catch {}
  }

  const goNext = useCallback(() => {
    setCurrentScene((s) => Math.min(s + 1, totalScenes - 1));
  }, [totalScenes]);

  const goPrev = useCallback(() => {
    setCurrentScene((s) => Math.max(s - 1, 0));
  }, []);

  // Keyboard navigation
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "ArrowRight" || e.key === " ") {
        e.preventDefault();
        goNext();
      }
      if (e.key === "ArrowLeft") goPrev();
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [goNext, goPrev]);

  // Save reading progress (debounced — fires on scene change)
  useEffect(() => {
    const timer = setTimeout(() => {
      fetch("/api/reading", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          storyId: story.id,
          currentScene: currentScene + 1,
          totalScenes,
          category: story.category,
          animationStyle: story.animation_style,
        }),
      }).catch(() => {}); // Silently fail if not logged in
    }, 500);
    return () => clearTimeout(timer);
  }, [currentScene, story.id, totalScenes, story.category, story.animation_style]);

  // Swipe handlers for mobile
  function onTouchStart(e: React.TouchEvent) {
    touchStartX.current = e.targetTouches[0].clientX;
  }
  function onTouchMove(e: React.TouchEvent) {
    touchEndX.current = e.targetTouches[0].clientX;
  }
  function onTouchEnd() {
    const diff = touchStartX.current - touchEndX.current;
    if (Math.abs(diff) > 50) {
      if (diff > 0) goNext();  // Swipe left = next
      else goPrev();           // Swipe right = prev
    }
  }

  const progress = ((currentScene + 1) / totalScenes) * 100;
  const isFirst = currentScene === 0;
  const isLast = currentScene === totalScenes - 1;

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col bg-[var(--color-pastel-cream)] overflow-hidden"
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
    >
      {/* Top bar: progress + title + scene counter */}
      <div className="flex-shrink-0">
        {/* Progress bar */}
        <div className="h-1 bg-[var(--color-pastel-cream)]">
          <div
            className="h-full bg-gradient-to-r from-[var(--color-pastel-pink)] to-[var(--color-pastel-lavender)] transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Title bar */}
        <div className="flex items-center justify-between px-3 py-2 sm:px-6 sm:py-3">
          <button
            onClick={() => router.back()}
            className="flex-shrink-0 h-8 w-8 rounded-full bg-white/60 flex items-center justify-center hover:bg-white transition-colors mr-2"
            aria-label="Close"
          >
            <X className="h-4 w-4 text-[var(--color-warm-brown)]" />
          </button>
          <div className="flex-1 min-w-0 mr-2">
            {seriesNav && (
              <Link
                href={`/series/${seriesNav.seriesId}`}
                className="inline-flex items-center gap-1 text-[10px] sm:text-xs font-semibold text-[var(--color-warm-brown)] bg-[var(--color-pastel-pink)] px-2 py-0.5 rounded-full hover:bg-[var(--color-pastel-rose)] transition-colors"
              >
                <Film className="h-2.5 w-2.5" />
                {seriesNav.seriesTitle} · {seriesNav.episodeCode}
              </Link>
            )}
            <h1 className="text-sm sm:text-lg font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)] truncate">
              {story.title}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs sm:text-sm text-muted-foreground whitespace-nowrap">
              {currentScene + 1}/{totalScenes}
            </span>
            <button
              onClick={handleShare}
              className="flex-shrink-0 h-8 w-8 rounded-full bg-white/60 flex items-center justify-center hover:bg-white transition-colors"
              aria-label="Share story"
            >
              {shared ? (
                <Check className="h-4 w-4 text-emerald-600" />
              ) : (
                <Share2 className="h-4 w-4 text-[var(--color-warm-brown)]" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Scene content: image + text — fills remaining viewport */}
      <div className="flex-1 flex flex-col min-h-0 px-2 sm:px-6 pb-2 sm:pb-4">
        {/* Image — takes most of the space */}
        <div className="flex-1 min-h-0 flex items-center justify-center gap-2 lg:gap-4">
          {/* Previous episode card — desktop only */}
          {seriesNav?.prev && (
            <Link
              href={`/stories/${seriesNav.prev.storyId}`}
              className="hidden lg:flex flex-col items-center justify-center w-40 xl:w-48 flex-shrink-0 group"
              aria-label={`Previous episode: ${seriesNav.prev.title}`}
            >
              <div className="relative w-full aspect-[2/3] rounded-xl overflow-hidden shadow-md group-hover:shadow-xl transition-all bg-[var(--color-pastel-cream)] opacity-70 group-hover:opacity-100">
                <img
                  src={`${API_URL}/api/v1/stories/${seriesNav.prev.storyId}/scenes/1/image`}
                  alt={`Previous episode cover: ${seriesNav.prev.title}`}
                  className="h-full w-full object-cover"
                  loading="lazy"
                />
                <div className="absolute top-2 left-2 bg-black/60 text-white text-[10px] px-1.5 py-0.5 rounded font-bold">
                  {seriesNav.prev.code}
                </div>
                <div className="absolute inset-0 flex items-center justify-center bg-black/20 group-hover:bg-black/30 transition-colors">
                  <div className="h-10 w-10 rounded-full bg-white/90 flex items-center justify-center shadow-lg">
                    <ChevronLeft className="h-5 w-5 text-[var(--color-warm-brown)]" />
                  </div>
                </div>
              </div>
              <p className="mt-2 text-[11px] text-center text-muted-foreground uppercase tracking-wider font-semibold">
                Previous
              </p>
              <p className="text-xs text-center text-[var(--color-warm-brown)] line-clamp-2 font-medium">
                {seriesNav.prev.title}
              </p>
            </Link>
          )}

          <div className="relative w-full h-full max-w-2xl mx-auto flex items-center justify-center">
            <img
              src={`${API_URL}/api/v1/stories/${story.id}/scenes/${scene.scene_number}/image`}
              alt={`Illustrated scene ${scene.scene_number} from ${story.title}, a free children's bedtime story`}
              className="max-h-full max-w-full object-contain rounded-xl sm:rounded-2xl shadow-md"
            />

            {/* Tap zones for mobile (invisible, overlay on image) */}
            <button
              onClick={goPrev}
              disabled={isFirst}
              className="absolute left-0 top-0 w-1/4 h-full opacity-0 cursor-pointer disabled:cursor-default"
              aria-label="Previous scene"
            />
            <button
              onClick={goNext}
              disabled={isLast}
              className="absolute right-0 top-0 w-1/4 h-full opacity-0 cursor-pointer disabled:cursor-default"
              aria-label="Next scene"
            />
          </div>

          {/* Next episode card — desktop only */}
          {seriesNav?.next && (
            <Link
              href={`/stories/${seriesNav.next.storyId}`}
              className="hidden lg:flex flex-col items-center justify-center w-40 xl:w-48 flex-shrink-0 group"
              aria-label={`Next episode: ${seriesNav.next.title}`}
            >
              <div className="relative w-full aspect-[2/3] rounded-xl overflow-hidden shadow-md group-hover:shadow-xl transition-all bg-[var(--color-pastel-cream)] opacity-70 group-hover:opacity-100">
                <img
                  src={`${API_URL}/api/v1/stories/${seriesNav.next.storyId}/scenes/1/image`}
                  alt={`Next episode cover: ${seriesNav.next.title}`}
                  className="h-full w-full object-cover"
                  loading="lazy"
                />
                <div className="absolute top-2 left-2 bg-black/60 text-white text-[10px] px-1.5 py-0.5 rounded font-bold">
                  {seriesNav.next.code}
                </div>
                <div className="absolute inset-0 flex items-center justify-center bg-black/20 group-hover:bg-black/30 transition-colors">
                  <div className="h-10 w-10 rounded-full bg-white/90 flex items-center justify-center shadow-lg">
                    <ChevronRight className="h-5 w-5 text-[var(--color-warm-brown)]" />
                  </div>
                </div>
              </div>
              <p className="mt-2 text-[11px] text-center text-muted-foreground uppercase tracking-wider font-semibold">
                Next Episode
              </p>
              <p className="text-xs text-center text-[var(--color-warm-brown)] line-clamp-2 font-medium">
                {seriesNav.next.title}
              </p>
            </Link>
          )}
        </div>

        {/* Story text — compact, always visible */}
        <div className="flex-shrink-0 mt-2 sm:mt-3">
          <div className="max-w-2xl mx-auto bg-white/80 backdrop-blur-sm rounded-xl sm:rounded-2xl px-4 py-3 sm:px-6 sm:py-4 shadow-sm">
            <p className="text-sm sm:text-base lg:text-lg leading-snug sm:leading-relaxed text-[var(--color-warm-brown)] text-center">
              {scene.text}
            </p>

            {/* Moral on last scene */}
            {isLast && story.moral && (
              <p className="mt-2 pt-2 border-t border-[var(--color-pastel-cream)] text-center text-xs sm:text-sm text-[var(--color-soft-brown)] italic">
                {story.moral}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Bottom nav bar */}
      <div className="flex-shrink-0 px-3 pb-3 sm:px-6 sm:pb-4">
        <div className="max-w-2xl mx-auto flex items-center justify-between gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={goPrev}
            disabled={isFirst}
            className="rounded-xl gap-1 disabled:opacity-20 text-[var(--color-warm-brown)]"
          >
            <ChevronLeft className="h-4 w-4 sm:h-5 sm:w-5" />
            <span className="hidden sm:inline text-sm">Previous</span>
          </Button>

          {/* Scene dots — scrollable on mobile */}
          <div className="flex items-center gap-1 overflow-hidden max-w-[60%] justify-center">
            {story.scenes.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentScene(i)}
                className={`flex-shrink-0 h-1.5 sm:h-2 rounded-full transition-all ${
                  i === currentScene
                    ? "w-4 sm:w-6 bg-[var(--color-pastel-pink)]"
                    : i < currentScene
                      ? "w-1.5 sm:w-2 bg-[var(--color-pastel-rose)]"
                      : "w-1.5 sm:w-2 bg-[var(--color-pastel-cream)] border border-border/50"
                }`}
              />
            ))}
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={goNext}
            disabled={isLast}
            className="rounded-xl gap-1 disabled:opacity-20 text-[var(--color-warm-brown)]"
          >
            <span className="hidden sm:inline text-sm">Next</span>
            <ChevronRight className="h-4 w-4 sm:h-5 sm:w-5" />
          </Button>
        </div>

        {/* Last scene: PDF + series navigation */}
        {isLast && (
          <div className="text-center mt-2 space-y-2">
            {seriesNav?.next && (
              <div className="lg:hidden">
                <Link
                  href={`/stories/${seriesNav.next.storyId}`}
                  className="inline-flex items-center gap-2 bg-[var(--color-pastel-pink)] hover:bg-[var(--color-pastel-rose)] text-[var(--color-warm-brown)] font-semibold text-sm px-4 py-2 rounded-xl shadow-sm transition-colors"
                >
                  Next Episode: {seriesNav.next.title}
                  <ChevronRight className="h-4 w-4" />
                </Link>
              </div>
            )}
            <div className="flex items-center justify-center gap-4 flex-wrap">
              <a
                href={`${API_URL}/api/v1/stories/${story.id}/pdf`}
                target="_blank"
                rel="noopener"
                className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                <Download className="h-3 w-3" />
                Download PDF
              </a>
              {seriesNav && (
                <Link
                  href={`/series/${seriesNav.seriesId}`}
                  className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  <Film className="h-3 w-3" />
                  All {seriesNav.totalEpisodes} episodes
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
