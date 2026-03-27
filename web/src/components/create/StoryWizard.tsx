"use client";

import { useState } from "react";
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
} from "lucide-react";
import { GenerationProgress } from "./GenerationProgress";

const STEPS = [
  { label: "Describe", icon: Wand2 },
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
  const [step, setStep] = useState(0);
  const [description, setDescription] = useState("");
  const [selectedStyle, setSelectedStyle] = useState("pixar_3d");
  const [sceneCount, setSceneCount] = useState([12]);
  const [jobId, setJobId] = useState<string | null>(null);

  async function handleGenerate() {
    // TODO: Call API with auth token
    // For now, show the progress component
    setJobId("demo-job-id");
  }

  if (jobId) {
    return <GenerationProgress jobId={jobId} />;
  }

  return (
    <div>
      {/* Step indicator */}
      <div className="flex items-center justify-center gap-2 mb-8">
        {STEPS.map((s, i) => (
          <div key={s.label} className="flex items-center">
            <button
              onClick={() => i < step && setStep(i)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
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
              <ChevronRight className="h-4 w-4 text-muted-foreground mx-1" />
            )}
          </div>
        ))}
      </div>

      <Card className="border-0 shadow-sm">
        <CardContent className="p-6 sm:p-8">
          {/* Step 1: Description */}
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
                    "A bunny who finds a magical garden",
                    "Two kittens on a rainy day adventure",
                    "A little owl learning to be brave at night",
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

          {/* Step 2: Art Style */}
          {step === 1 && (
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
          {step === 2 && (
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
                    onValueChange={(value) => setSceneCount(Array.isArray(value) ? value : [value])}
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
          {step === 3 && (
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
                <div className="flex gap-4">
                  <div className="bg-[var(--color-pastel-cream)] rounded-xl p-4 flex-1">
                    <p className="text-xs font-medium text-muted-foreground mb-1">
                      Art Style
                    </p>
                    <p className="text-sm text-[var(--color-warm-brown)]">
                      {ANIMATION_STYLES.find((s) => s.id === selectedStyle)
                        ?.preview}{" "}
                      {ANIMATION_STYLES.find((s) => s.id === selectedStyle)
                        ?.name}
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
                  </p>
                </div>
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
              >
                <ChevronLeft className="h-4 w-4" />
                Back
              </Button>
            ) : (
              <div />
            )}

            {step < 3 ? (
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
                className="rounded-xl gap-2 bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)] px-8"
              >
                <Sparkles className="h-4 w-4" />
                Create My Story
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
