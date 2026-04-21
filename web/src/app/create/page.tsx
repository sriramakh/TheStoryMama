import type { Metadata } from "next";
import { StoryWizard } from "@/components/create/StoryWizard";

export const metadata: Metadata = {
  title: "Create a Personalized Bedtime Story",
  description:
    "Create a personalized illustrated bedtime story starring your child. Upload avatars, choose from 10 art styles, get a beautiful PDF storybook.",
};

export default function CreatePage() {
  return (
    <div className="min-h-screen bg-[var(--color-pastel-cream)]/30">
      <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
            Create Your Story
          </h1>
          <p className="mt-2 text-muted-foreground">
            Star your child, parents, or grandparents — we&apos;ll bring the
            adventure to life with beautiful illustrations.
          </p>
        </div>
        <StoryWizard />
      </div>
    </div>
  );
}
