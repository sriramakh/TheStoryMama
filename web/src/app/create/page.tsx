import type { Metadata } from "next";
import { StoryWizard } from "@/components/create/StoryWizard";

export const metadata: Metadata = {
  title: "Create a Story",
  description:
    "Create a personalized illustrated bedtime story for your child. Choose from 10 art styles and get a beautiful PDF storybook.",
};

export default function CreatePage() {
  return (
    <div className="min-h-screen bg-[var(--color-pastel-cream)]/30">
      <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
            Create Your Story
          </h1>
          <p className="mt-2 text-muted-foreground">
            Tell us about the adventure and we&apos;ll bring it to life with
            beautiful illustrations
          </p>
        </div>
        <StoryWizard />
      </div>
    </div>
  );
}
