"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, Download, X } from "lucide-react";
import { API_URL } from "@/lib/constants";
import type { Story } from "@/types/story";

export function StoryReader({ story }: { story: Story }) {
  const [currentScene, setCurrentScene] = useState(0);
  const totalScenes = story.scenes.length;
  const scene = story.scenes[currentScene];
  const router = useRouter();
  const touchStartX = useRef(0);
  const touchEndX = useRef(0);

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
          <h1 className="text-sm sm:text-lg font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)] truncate flex-1 mr-2">
            {story.title}
          </h1>
          <span className="text-xs sm:text-sm text-muted-foreground whitespace-nowrap">
            {currentScene + 1}/{totalScenes}
          </span>
        </div>
      </div>

      {/* Scene content: image + text — fills remaining viewport */}
      <div className="flex-1 flex flex-col min-h-0 px-2 sm:px-6 pb-2 sm:pb-4">
        {/* Image — takes most of the space */}
        <div className="flex-1 min-h-0 flex items-center justify-center">
          <div className="relative w-full h-full max-w-2xl mx-auto flex items-center justify-center">
            <img
              src={`${API_URL}/api/v1/stories/${story.id}/scenes/${scene.scene_number}/image`}
              alt={`Scene ${scene.scene_number}`}
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

        {/* Download PDF — small link, not prominent */}
        {isLast && (
          <div className="text-center mt-2">
            <a
              href={`${API_URL}/api/v1/stories/${story.id}/pdf`}
              target="_blank"
              rel="noopener"
              className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              <Download className="h-3 w-3" />
              Download PDF
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
