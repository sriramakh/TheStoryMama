"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Slider } from "@/components/ui/slider";
import { ANIMATION_STYLES } from "@/lib/constants";
import {
  Sparkles,
  ChevronRight,
  ChevronLeft,
  Wand2,
  Palette,
  Settings,
  Check,
  Users,
} from "lucide-react";
import { GenerationProgress } from "./GenerationProgress";
import { AvatarManager } from "@/components/avatars/AvatarManager";
import { generateStory, listAvatars, type Avatar } from "@/lib/api";
// Backend auth is handled server-side by Next.js proxy routes under
// /api/stories/* and /api/avatars/*. The session is used only to gate the UI.

const STEPS = [
  { label: "Describe", icon: Wand2 },
  { label: "Characters", icon: Users },
  { label: "Art Style", icon: Palette },
  { label: "Settings", icon: Settings },
  { label: "Review", icon: Check },
];

const styleColors = [
  "bg-[var(--color-pastel-pink)]/50",
  "bg-[var(--color-pastel-lavender)]/50",
  "bg-[var(--color-pastel-sky)]/50",
  "bg-[var(--color-pastel-mint)]/50",
  "bg-[var(--color-pastel-yellow)]/50",
  "bg-[var(--color-pastel-peach)]/50",
  "bg-[var(--color-pastel-pink)]/50",
  "bg-[var(--color-pastel-lavender)]/50",
  "bg-[var(--color-pastel-sky)]/50",
  "bg-[var(--color-pastel-mint)]/50",
];

export function StoryWizard() {
  const { data: session } = useSession();
  const signedIn = !!session?.user?.email;

  const [step, setStep] = useState(0);
  const [description, setDescription] = useState("");
  const [selectedAvatarIds, setSelectedAvatarIds] = useState<string[]>([]);
  const [availableAvatars, setAvailableAvatars] = useState<Avatar[]>([]);
  const [selectedStyle, setSelectedStyle] = useState("animation_movie");
  const [sceneCount, setSceneCount] = useState([12]);
  const [jobId, setJobId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Pre-load avatars so we know if user has any (affects copy on the Characters step)
  useEffect(() => {
    if (!signedIn) return;
    listAvatars()
      .then((d) => setAvailableAvatars(d.avatars))
      .catch(() => {});
  }, [signedIn]);

  function toggleAvatar(id: string) {
    setSelectedAvatarIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  async function handleGenerate() {
    if (!signedIn) {
      setError("Please sign in first.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const result = await generateStory({
        description: description || undefined,
        num_scenes: sceneCount[0],
        animation_style: selectedStyle,
        avatar_ids:
          selectedAvatarIds.length > 0 ? selectedAvatarIds : undefined,
      });
      setJobId(result.job_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start generation");
      setSubmitting(false);
    }
  }

  if (jobId) {
    return <GenerationProgress jobId={jobId} />;
  }

  const selectedAvatars = availableAvatars.filter((a) =>
    selectedAvatarIds.includes(a.id)
  );

  return (
    <div>
      {/* Step indicator */}
      <div className="flex items-center justify-center gap-1 sm:gap-2 mb-8 flex-wrap">
        {STEPS.map((s, i) => (
          <div key={s.label} className="flex items-center">
            <button
              onClick={() => i < step && setStep(i)}
              className={`flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-full text-xs sm:text-sm font-medium transition-colors ${
                i === step
                  ? "bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)]"
                  : i < step
                    ? "bg-[var(--color-pastel-mint)] text-emerald-700"
                    : "bg-muted text-muted-foreground"
              }`}
            >
              <s.icon className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">{s.label}</span>
            </button>
            {i < STEPS.length - 1 && (
              <ChevronRight className="h-3 w-3 sm:h-4 sm:w-4 text-muted-foreground mx-0.5 sm:mx-1" />
            )}
          </div>
        ))}
      </div>

      <Card className="border-0 shadow-sm">
        <CardContent className="p-6 sm:p-8">
          {/* Step 0: Description */}
          {step === 0 && (
            <div>
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
              <div className="flex items-center justify-between mt-2">
                <p className="text-xs text-muted-foreground">
                  Leave empty for a surprise story!
                </p>
                <p className="text-xs text-muted-foreground">
                  {description.length}/500
                </p>
              </div>

              <div className="mt-6">
                <p className="text-sm font-medium text-muted-foreground mb-3">
                  Need inspiration?
                </p>
                <div className="flex flex-wrap gap-2">
                  {[
                    "A magical garden adventure with grandma",
                    "Best friends find a hidden treasure at the park",
                    "A rainy day fort that becomes a spaceship",
                  ].map((prompt) => (
                    <button
                      key={prompt}
                      onClick={() => setDescription(prompt)}
                      className="text-xs px-3 py-1.5 rounded-full bg-[var(--color-pastel-cream)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-yellow)] transition-colors"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 1: Characters (Avatars) */}
          {step === 1 && (
            <div>
              <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mb-2">
                Star your loved ones
              </h2>
              <p className="text-sm text-muted-foreground mb-6">
                Pick which avatars should appear in this story. Or skip — we&apos;ll
                invent characters for you.
              </p>
              <AvatarManager
                selectable
                selectedIds={selectedAvatarIds}
                onSelect={toggleAvatar}
                onAvatarsChange={setAvailableAvatars}
              />
            </div>
          )}

          {/* Step 2: Art Style */}
          {step === 2 && (
            <div>
              <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mb-4">
                Choose an art style
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                {ANIMATION_STYLES.map((style, i) => (
                  <button
                    key={style.id}
                    onClick={() => setSelectedStyle(style.id)}
                    className={`${styleColors[i]} rounded-2xl p-4 text-center transition-all ${
                      selectedStyle === style.id
                        ? "ring-2 ring-[var(--color-pastel-pink)] shadow-md scale-105"
                        : "hover:shadow-sm hover:-translate-y-0.5"
                    }`}
                  >
                    <span className="text-2xl">{style.preview}</span>
                    <p className="mt-1.5 text-xs font-semibold text-[var(--color-warm-brown)]">
                      {style.name}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 3: Settings */}
          {step === 3 && (
            <div>
              <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mb-6">
                Story settings
              </h2>
              <div className="max-w-sm mx-auto">
                <label className="text-sm font-medium text-foreground">
                  Number of scenes
                </label>
                <div className="mt-3">
                  <Slider
                    value={sceneCount}
                    onValueChange={(value) =>
                      setSceneCount(Array.isArray(value) ? value : [value])
                    }
                    min={10}
                    max={15}
                    step={1}
                    className="py-4"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground mt-1">
                    <span>10 (shorter)</span>
                    <span className="font-semibold text-[var(--color-warm-brown)] text-sm">
                      {sceneCount[0]} scenes
                    </span>
                    <span>15 (longer)</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Review */}
          {step === 4 && (
            <div>
              <h2 className="text-xl font-semibold text-[var(--color-warm-brown)] mb-6">
                Review your story
              </h2>
              <div className="space-y-4">
                <div className="bg-[var(--color-pastel-cream)] rounded-xl p-4">
                  <p className="text-xs font-medium text-muted-foreground mb-1">
                    Story Description
                  </p>
                  <p className="text-sm text-[var(--color-warm-brown)]">
                    {description || "Surprise me with a random story!"}
                  </p>
                </div>

                {selectedAvatars.length > 0 && (
                  <div className="bg-[var(--color-pastel-cream)] rounded-xl p-4">
                    <p className="text-xs font-medium text-muted-foreground mb-2">
                      Characters
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {selectedAvatars.map((a) => (
                        <div
                          key={a.id}
                          className="flex items-center gap-2 bg-white rounded-full pl-1 pr-3 py-1"
                        >
                          <img
                            src={a.image_url}
                            alt={a.name}
                            className="h-7 w-7 rounded-full object-cover"
                          />
                          <span className="text-xs font-medium text-[var(--color-warm-brown)]">
                            {a.name}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex gap-4">
                  <div className="bg-[var(--color-pastel-cream)] rounded-xl p-4 flex-1">
                    <p className="text-xs font-medium text-muted-foreground mb-1">
                      Art Style
                    </p>
                    <p className="text-sm text-[var(--color-warm-brown)]">
                      {ANIMATION_STYLES.find((s) => s.id === selectedStyle)?.preview}{" "}
                      {ANIMATION_STYLES.find((s) => s.id === selectedStyle)?.name}
                    </p>
                  </div>
                  <div className="bg-[var(--color-pastel-cream)] rounded-xl p-4 flex-1">
                    <p className="text-xs font-medium text-muted-foreground mb-1">
                      Scenes
                    </p>
                    <p className="text-sm text-[var(--color-warm-brown)]">
                      {sceneCount[0]} scenes
                    </p>
                  </div>
                </div>

                <div className="bg-[var(--color-pastel-yellow)]/50 rounded-xl p-4 text-center">
                  <p className="text-sm text-[var(--color-warm-brown)]">
                    This will use <strong>1 story credit</strong>
                    {selectedAvatars.length > 0 &&
                      ` · Featuring ${selectedAvatars.length} of your avatars`}
                  </p>
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-3 rounded-lg">
                    {error}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Navigation buttons */}
          <div className="flex items-center justify-between mt-8 pt-6 border-t border-border">
            {step > 0 ? (
              <Button
                variant="outline"
                onClick={() => setStep(step - 1)}
                className="rounded-xl gap-1"
                disabled={submitting}
              >
                <ChevronLeft className="h-4 w-4" />
                Back
              </Button>
            ) : (
              <div />
            )}

            {step < STEPS.length - 1 ? (
              <Button
                onClick={() => setStep(step + 1)}
                className="rounded-xl gap-1 bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)]"
              >
                Continue
                <ChevronRight className="h-4 w-4" />
              </Button>
            ) : (
              <Button
                onClick={handleGenerate}
                disabled={submitting}
                className="rounded-xl gap-2 bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)] px-8"
              >
                <Sparkles className="h-4 w-4" />
                {submitting ? "Starting..." : "Create My Story"}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
