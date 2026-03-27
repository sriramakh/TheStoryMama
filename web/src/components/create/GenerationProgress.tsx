"use client";

import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { BookOpen, Sparkles } from "lucide-react";
import Link from "next/link";

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
  const [storyId, setStoryId] = useState<string | null>(null);

  // TODO: Replace with actual API polling via useGenerationStatus hook
  useEffect(() => {
    // Simulate progress for demo
    const stages = [
      { status: "generating_story", progress: 10, delay: 1000 },
      { status: "generating_story", progress: 15, delay: 2000 },
      { status: "generating_images", progress: 30, delay: 3000 },
      { status: "generating_images", progress: 50, delay: 5000 },
      { status: "generating_images", progress: 70, delay: 7000 },
      { status: "overlaying_text", progress: 80, delay: 8000 },
      { status: "compiling_pdf", progress: 90, delay: 9000 },
      { status: "completed", progress: 100, delay: 10000 },
    ];

    const timers = stages.map((stage) =>
      setTimeout(() => {
        setStatus(stage.status);
        setProgress(stage.progress);
        if (stage.status === "completed") {
          setStoryId("demo-story");
        }
      }, stage.delay)
    );

    return () => timers.forEach(clearTimeout);
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
          {STATUS_MESSAGES[status] || "Working on your story..."}
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
              We couldn&apos;t generate your story. Your credit has been
              refunded.
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
