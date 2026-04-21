"use client";

import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { BookOpen, Sparkles } from "lucide-react";
import Link from "next/link";
import { getJobStatus } from "@/lib/api";

const STATUS_MESSAGES: Record<string, string> = {
  queued: "Getting everything ready...",
  generating_story: "Writing your magical story...",
  generating_images: "Painting beautiful illustrations...",
  overlaying_text: "Adding story text to scenes...",
  compiling_video: "Creating your video storybook...",
  compiling_pdf: "Compiling your PDF storybook...",
  completed: "Your story is ready!",
  failed: "Something went wrong",
};

export function GenerationProgress({ jobId }: { jobId: string }) {
  const [status, setStatus] = useState("queued");
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState<string | null>(null);
  const [storyId, setStoryId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | null = null;

    async function tick() {
      try {
        const s = await getJobStatus(jobId);
        if (cancelled) return;
        setStatus(s.status);
        setProgress(s.progress ?? 0);
        setMessage(s.message ?? null);
        if (s.status === "completed" && s.story_id) {
          setStoryId(s.story_id);
          return; // stop polling
        }
        if (s.status === "failed") return;
        timer = setTimeout(tick, 3000);
      } catch {
        if (!cancelled) timer = setTimeout(tick, 5000);
      }
    }

    tick();
    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [jobId]);

  const isComplete = status === "completed";
  const isFailed = status === "failed";

  return (
    <Card className="border-0 shadow-sm max-w-lg mx-auto">
      <CardContent className="p-8 text-center">
        {/* Animated icon */}
        <div className="mb-6">
          {isComplete ? (
            <div className="h-20 w-20 mx-auto rounded-full bg-[var(--color-pastel-mint)] flex items-center justify-center">
              <BookOpen className="h-10 w-10 text-emerald-600" />
            </div>
          ) : (
            <div className="h-20 w-20 mx-auto rounded-full bg-[var(--color-pastel-lavender)] flex items-center justify-center animate-pulse">
              <Sparkles className="h-10 w-10 text-purple-500" />
            </div>
          )}
        </div>

        {/* Status message */}
        <h3 className="text-xl font-bold text-[var(--color-warm-brown)] mb-2">
          {message || STATUS_MESSAGES[status] || "Working on your story..."}
        </h3>

        {!isComplete && !isFailed && (
          <p className="text-sm text-muted-foreground mb-6">
            This usually takes 3-5 minutes. Feel free to stay or come back
            later!
          </p>
        )}

        {/* Progress bar */}
        {!isComplete && !isFailed && (
          <div className="mb-6">
            <Progress value={progress} className="h-3 rounded-full" />
            <p className="text-sm text-muted-foreground mt-2">
              {Math.round(progress)}% complete
            </p>
          </div>
        )}

        {/* Completion actions */}
        {isComplete && storyId && (
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mt-6">
            <Link href={`/stories/${storyId}`}>
              <Button
                size="lg"
                className="rounded-xl gap-2 bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)]"
              >
                <BookOpen className="h-5 w-5" />
                Read Your Story
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="outline" size="lg" className="rounded-xl">
                Go to Dashboard
              </Button>
            </Link>
          </div>
        )}

        {/* Error state */}
        {isFailed && (
          <div className="mt-6">
            <p className="text-sm text-destructive mb-4">
              {message || "We couldn't generate your story. Your credit has been refunded."}
            </p>
            <Button
              variant="outline"
              className="rounded-xl"
              onClick={() => window.location.reload()}
            >
              Try Again
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
