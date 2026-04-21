import type { Metadata } from "next";
import { AvatarManager } from "@/components/avatars/AvatarManager";

export const metadata: Metadata = {
  title: "My Avatars",
  description:
    "Create animated avatars from photos of your kids, parents, or grandparents to star in your custom bedtime stories.",
};

export default function AvatarsPage() {
  return (
    <div className="min-h-screen bg-[var(--color-pastel-cream)]/30">
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
            My Avatars
          </h1>
          <p className="text-base text-muted-foreground mt-2 max-w-2xl">
            Upload a photo of someone you love and we&apos;ll turn them into an
            animated character. Use these avatars when creating personalized
            bedtime stories — your child becomes the hero.
          </p>
        </div>
        <AvatarManager />
      </div>
    </div>
  );
}
