import type { Metadata } from "next";
import { PricingCards } from "@/components/pricing/PricingCards";
import { Check, Sparkles } from "lucide-react";

export const metadata: Metadata = {
  title: "Pricing - Create Custom Stories",
  description:
    "Create personalized AI-generated storybooks for your children. Starting at $9.99 for 5 stories.",
};

export default function PricingPage() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="bg-gradient-to-b from-[var(--color-pastel-pink)]/20 to-transparent">
        <div className="mx-auto max-w-5xl px-4 pt-12 pb-8 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 rounded-full bg-white/60 px-4 py-1.5 text-sm font-medium text-[var(--color-warm-brown)] shadow-sm backdrop-blur-sm mb-6">
            <Sparkles className="h-3.5 w-3.5" />
            Simple, transparent pricing
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
            Create Stories Your Child Will Treasure
          </h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Every custom story features 10-15 beautifully illustrated scenes,
            downloadable as a PDF storybook. Choose the plan that fits your
            family.
          </p>
        </div>
      </div>

      {/* Pricing cards */}
      <div className="mx-auto max-w-5xl px-4 pb-16 sm:px-6 lg:px-8">
        <PricingCards />

        {/* What's included */}
        <div className="mt-16 bg-white rounded-2xl p-8 shadow-sm">
          <h3 className="text-xl font-bold text-[var(--color-warm-brown)] mb-6 text-center">
            Every Story Includes
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              "10-15 illustrated scenes",
              "10 beautiful art styles",
              "Downloadable PDF storybook",
              "High-resolution images",
              "Personalized characters",
              "Age-appropriate content",
              "Gentle moral lessons",
              "Read online anytime",
              "Share with family",
            ].map((feature) => (
              <div key={feature} className="flex items-center gap-2.5">
                <div className="h-5 w-5 rounded-full bg-[var(--color-pastel-mint)] flex items-center justify-center flex-shrink-0">
                  <Check className="h-3 w-3 text-emerald-600" />
                </div>
                <span className="text-sm text-foreground/80">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
