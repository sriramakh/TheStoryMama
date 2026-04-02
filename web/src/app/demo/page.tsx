"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import {
  Sparkles,
  BookOpen,
  Download,
  Play,
  ChevronLeft,
  ChevronRight,
  Palette,
  Wand2,
  FileText,
  Video,
  Check,
} from "lucide-react";
import { API_URL } from "@/lib/constants";

const DEMO_STORY_ID = "demo_story";

const PROGRESS_STEPS = [
  { label: "Understanding your story idea...", duration: 3000, icon: Wand2 },
  { label: "Crafting characters and plot...", duration: 3000, icon: Wand2 },
  { label: "Writing 12 illustrated scenes...", duration: 3000, icon: FileText },
  { label: "Choosing the perfect art style...", duration: 2000, icon: Palette },
  { label: "Painting scene 1 of 12...", duration: 1500, icon: Sparkles },
  { label: "Painting scene 2 of 12...", duration: 1000, icon: Sparkles },
  { label: "Painting scene 3 of 12...", duration: 1000, icon: Sparkles },
  { label: "Painting scene 4 of 12...", duration: 800, icon: Sparkles },
  { label: "Painting scenes 5-8...", duration: 1500, icon: Sparkles },
  { label: "Painting scenes 9-12...", duration: 1500, icon: Sparkles },
  { label: "Adding story text overlays...", duration: 1500, icon: FileText },
  { label: "Compiling PDF storybook...", duration: 1000, icon: BookOpen },
  { label: "Creating video with narration...", duration: 1500, icon: Video },
  { label: "Almost ready...", duration: 1000, icon: Check },
];

interface Scene {
  scene_number: number;
  text: string;
}

interface StoryData {
  title: string;
  moral?: string;
  characters: { name: string; type: string; description: string }[];
  scenes: Scene[];
}

export default function DemoPage() {
  const [phase, setPhase] = useState<"input" | "generating" | "result">("input");
  const [description, setDescription] = useState("");
  const [progressStep, setProgressStep] = useState(0);
  const [progressPct, setProgressPct] = useState(0);
  const [story, setStory] = useState<StoryData | null>(null);
  const [currentScene, setCurrentScene] = useState(0);
  const [showVideo, setShowVideo] = useState(false);

  // Run fake progress animation
  useEffect(() => {
    if (phase !== "generating") return;

    let step = 0;
    let elapsed = 0;
    const totalDuration = PROGRESS_STEPS.reduce((a, s) => a + s.duration, 0);

    function nextStep() {
      if (step >= PROGRESS_STEPS.length) {
        // Load the pre-generated story
        fetch(`${API_URL}/api/v1/stories/${DEMO_STORY_ID}`)
          .then((r) => r.json())
          .then((data) => {
            setStory(data);
            setPhase("result");
          });
        return;
      }

      setProgressStep(step);
      elapsed += PROGRESS_STEPS[step].duration;
      setProgressPct(Math.min(99, Math.round((elapsed / totalDuration) * 100)));
      step++;
      setTimeout(nextStep, PROGRESS_STEPS[step - 1].duration);
    }

    nextStep();
  }, [phase]);

  function handleGenerate() {
    if (!description.trim()) return;
    setPhase("generating");
  }

  const StepIcon = phase === "generating" && progressStep < PROGRESS_STEPS.length
    ? PROGRESS_STEPS[progressStep].icon
    : Sparkles;

  // ── INPUT PHASE ────────────────────────────────────────────────────────────
  if (phase === "input") {
    return (
      <div className="min-h-screen bg-[var(--color-pastel-cream)]/30">
        <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h1 className="text-3xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
              Create Your Story
            </h1>
            <p className="mt-2 text-muted-foreground">
              Describe the story you&apos;d like and we&apos;ll bring it to life
              with beautiful illustrations
            </p>
          </div>

          <Card className="border-0 shadow-sm">
            <CardContent className="p-6 sm:p-8">
              <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mb-4">
                What&apos;s your story about?
              </h2>
              <Textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="A brave little penguin who dreams of flying and discovers that flapping her tiny wings can create beautiful snow flurries..."
                className="min-h-[160px] rounded-xl border-border text-base resize-none"
                maxLength={500}
              />
              <div className="flex justify-between mt-2">
                <p className="text-xs text-muted-foreground">
                  Describe characters, setting, and what happens
                </p>
                <p className="text-xs text-muted-foreground">
                  {description.length}/500
                </p>
              </div>

              <div className="mt-6 bg-[var(--color-pastel-cream)] rounded-xl p-4">
                <p className="text-sm font-medium text-[var(--color-warm-brown)] mb-2">
                  Art Style
                </p>
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-[var(--color-pastel-pink)] flex items-center justify-center">
                    <span className="text-lg">🎬</span>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-[var(--color-warm-brown)]">
                      Animation Movie
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Modern 3D animated style with expressive characters
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-6 bg-[var(--color-pastel-cream)] rounded-xl p-4">
                <div className="flex justify-between text-sm">
                  <span className="text-[var(--color-warm-brown)] font-medium">Scenes</span>
                  <span className="text-[var(--color-warm-brown)] font-semibold">12 illustrated scenes</span>
                </div>
              </div>

              <Button
                onClick={handleGenerate}
                disabled={!description.trim()}
                className="w-full mt-6 rounded-xl py-6 text-base gap-2 bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)]"
              >
                <Sparkles className="h-5 w-5" />
                Create My Story
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // ── GENERATING PHASE ───────────────────────────────────────────────────────
  if (phase === "generating") {
    return (
      <div className="min-h-screen bg-[var(--color-pastel-cream)]/30 flex items-center justify-center px-4">
        <Card className="border-0 shadow-lg max-w-lg w-full">
          <CardContent className="p-8 text-center">
            <div className="h-20 w-20 mx-auto rounded-full bg-[var(--color-pastel-lavender)] flex items-center justify-center animate-pulse mb-6">
              <StepIcon className="h-10 w-10 text-purple-500" />
            </div>

            <h3 className="text-xl font-bold text-[var(--color-warm-brown)] mb-2">
              Creating Your Story
            </h3>

            <p className="text-sm text-muted-foreground mb-6">
              {progressStep < PROGRESS_STEPS.length
                ? PROGRESS_STEPS[progressStep].label
                : "Finishing up..."}
            </p>

            {/* Progress bar */}
            <div className="h-3 rounded-full bg-[var(--color-pastel-cream)] overflow-hidden mb-2">
              <div
                className="h-full rounded-full bg-gradient-to-r from-[var(--color-pastel-pink)] to-[var(--color-pastel-lavender)] transition-all duration-500 ease-out"
                style={{ width: `${progressPct}%` }}
              />
            </div>
            <p className="text-sm text-muted-foreground">{progressPct}% complete</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // ── RESULT PHASE ───────────────────────────────────────────────────────────
  if (!story) return null;
  const scene = story.scenes[currentScene];

  return (
    <div className="min-h-screen bg-[var(--color-pastel-cream)]/30">
      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Success header */}
        <div className="text-center mb-8">
          <div className="inline-flex h-14 w-14 items-center justify-center rounded-full bg-[var(--color-pastel-mint)] mb-3">
            <Check className="h-7 w-7 text-emerald-600" />
          </div>
          <h1 className="text-3xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
            {story.title}
          </h1>
          <p className="mt-2 text-muted-foreground">
            Your story is ready! 12 illustrated scenes, PDF storybook, and narrated video.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left: Story Reader */}
          <div>
            <Card className="border-0 shadow-sm overflow-hidden">
              <div className="bg-white">
                <img
                  src={`${API_URL}/api/v1/stories/${DEMO_STORY_ID}/scenes/${scene.scene_number}/image`}
                  alt={`Scene ${scene.scene_number}`}
                  className="w-full h-auto"
                />
              </div>
              <CardContent className="p-5">
                <p className="text-base leading-relaxed text-[var(--color-warm-brown)] text-center">
                  {scene.text}
                </p>

                {currentScene === story.scenes.length - 1 && story.moral && (
                  <p className="mt-3 pt-3 border-t border-[var(--color-pastel-cream)] text-center text-sm text-[var(--color-soft-brown)] italic">
                    {story.moral}
                  </p>
                )}

                {/* Navigation */}
                <div className="flex items-center justify-between mt-4">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setCurrentScene(Math.max(0, currentScene - 1))}
                    disabled={currentScene === 0}
                    className="rounded-xl gap-1"
                  >
                    <ChevronLeft className="h-4 w-4" />
                    Previous
                  </Button>
                  <span className="text-sm text-muted-foreground">
                    {currentScene + 1} of {story.scenes.length}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setCurrentScene(Math.min(story.scenes.length - 1, currentScene + 1))}
                    disabled={currentScene === story.scenes.length - 1}
                    className="rounded-xl gap-1"
                  >
                    Next
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>

                {/* Scene dots */}
                <div className="flex justify-center gap-1.5 mt-3">
                  {story.scenes.map((_, i) => (
                    <button
                      key={i}
                      onClick={() => setCurrentScene(i)}
                      className={`h-2 rounded-full transition-all ${
                        i === currentScene
                          ? "w-5 bg-[var(--color-pastel-pink)]"
                          : i < currentScene
                            ? "w-2 bg-[var(--color-pastel-rose)]"
                            : "w-2 bg-[var(--color-pastel-cream)] border border-border/50"
                      }`}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right: Downloads + Video */}
          <div className="space-y-4">
            {/* Characters */}
            <Card className="border-0 shadow-sm">
              <CardContent className="p-5">
                <h3 className="text-sm font-semibold text-[var(--color-warm-brown)] mb-3">
                  Characters
                </h3>
                <div className="space-y-2">
                  {story.characters.map((c) => (
                    <div key={c.name} className="flex items-start gap-2">
                      <div className="h-6 w-6 rounded-full bg-[var(--color-pastel-pink)] flex items-center justify-center flex-shrink-0 text-xs font-bold text-[var(--color-warm-brown)]">
                        {c.name[0]}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-[var(--color-warm-brown)]">
                          {c.name}
                        </p>
                        <p className="text-xs text-muted-foreground">{c.type}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Downloads */}
            <Card className="border-0 shadow-sm">
              <CardContent className="p-5">
                <h3 className="text-sm font-semibold text-[var(--color-warm-brown)] mb-3">
                  Your Storybook
                </h3>
                <div className="space-y-3">
                  <a
                    href={`${API_URL}/api/v1/stories/${DEMO_STORY_ID}/pdf`}
                    target="_blank"
                    rel="noopener"
                  >
                    <Button
                      variant="outline"
                      className="w-full rounded-xl gap-2 justify-start border-[var(--color-pastel-mint)] hover:bg-[var(--color-pastel-mint)]/30"
                    >
                      <Download className="h-4 w-4" />
                      Download PDF Storybook
                    </Button>
                  </a>

                  <Button
                    variant="outline"
                    className="w-full rounded-xl gap-2 justify-start border-[var(--color-pastel-lavender)] hover:bg-[var(--color-pastel-lavender)]/30"
                    onClick={() => setShowVideo(!showVideo)}
                  >
                    <Play className="h-4 w-4" />
                    {showVideo ? "Hide Video" : "Watch Narrated Video"}
                  </Button>

                  {showVideo && (
                    <div className="rounded-xl overflow-hidden bg-black">
                      <video
                        controls
                        className="w-full"
                        src={`${API_URL}/api/v1/stories/${DEMO_STORY_ID}/video`}
                      />
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Story info */}
            <Card className="border-0 shadow-sm bg-gradient-to-br from-[var(--color-pastel-pink)]/20 to-[var(--color-pastel-lavender)]/20">
              <CardContent className="p-5">
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-[var(--color-warm-brown)]">12</p>
                    <p className="text-xs text-muted-foreground">Scenes</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-[var(--color-warm-brown)]">1</p>
                    <p className="text-xs text-muted-foreground">PDF</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-[var(--color-warm-brown)]">1</p>
                    <p className="text-xs text-muted-foreground">Video</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
