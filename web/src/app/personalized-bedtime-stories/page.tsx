import type { Metadata } from "next";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { ArtStyleShowcase } from "@/components/landing/ArtStyleShowcase";
import { Testimonials } from "@/components/landing/Testimonials";
import { Wand2, Palette, BookOpen, Heart, Sparkles } from "lucide-react";

const SITE_URL = "https://www.thestorymama.club";

export const metadata: Metadata = {
  title: "Personalized Bedtime Stories for Your Child | TheStoryMama",
  description:
    "Create a custom bedtime story starring your child. AI-powered personalized stories with your child's name, favorite characters, and beautiful illustrations. PDF download + shareable link.",
  alternates: { canonical: `${SITE_URL}/personalized-bedtime-stories` },
  openGraph: {
    title: "Personalized Bedtime Stories for Your Child | TheStoryMama",
    description:
      "Create a custom bedtime story starring your child — their name, their world, their adventure. Beautifully illustrated, free to read online.",
    url: `${SITE_URL}/personalized-bedtime-stories`,
    siteName: "TheStoryMama",
    type: "website",
  },
};

export default function PersonalizedBedtimeStoriesPage() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Service",
    name: "Personalized Bedtime Stories",
    serviceType: "Custom illustrated bedtime story generation for children",
    description:
      "AI-powered personalized bedtime stories starring your child. Choose characters, art style, and themes — receive a beautifully illustrated 10-15 scene storybook with PDF download.",
    provider: {
      "@type": "Organization",
      name: "TheStoryMama",
      url: SITE_URL,
    },
    areaServed: { "@type": "Country", name: "Worldwide" },
    audience: { "@type": "Audience", audienceType: "Parents of children ages 2-8" },
    offers: {
      "@type": "AggregateOffer",
      priceCurrency: "USD",
      lowPrice: "9.99",
      highPrice: "99",
      offerCount: "3",
    },
    url: `${SITE_URL}/personalized-bedtime-stories`,
  };

  return (
    <>
      <script
        id="personalized-jsonld"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-[var(--color-pastel-pink)]/40 via-[var(--color-pastel-lavender)]/30 to-[var(--color-pastel-sky)]/40">
        <div className="mx-auto max-w-4xl px-4 py-16 sm:py-24 text-center">
          <div className="inline-flex items-center gap-2 rounded-full bg-white/70 px-4 py-1.5 text-sm font-medium text-[var(--color-warm-brown)] shadow-sm mb-6">
            <Sparkles className="h-3.5 w-3.5 text-[var(--color-pastel-rose)]" />
            AI-Powered, Parent-Approved
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)] mb-6">
            Personalized Bedtime Stories<br />
            for Your Child
          </h1>
          <p className="mx-auto max-w-2xl text-lg text-foreground/80 leading-relaxed mb-8">
            Create a custom illustrated bedtime story starring your child — their
            name, their favorite adventure, their magical world. Read online,
            download as PDF, or share with grandparents across the world.
          </p>
          <Link href="/create">
            <Button
              size="lg"
              className="text-base px-8 py-6 rounded-2xl bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)] shadow-lg gap-2"
            >
              <Heart className="h-5 w-5" />
              Create Your Story
            </Button>
          </Link>
          <p className="mt-4 text-sm text-muted-foreground">
            First story from $9.99 • All 10 art styles included • PDF download
          </p>
        </div>
      </section>

      {/* How it Works */}
      <section className="bg-[var(--color-pastel-cream)]/50 py-16">
        <div className="mx-auto max-w-5xl px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-[var(--color-warm-brown)] mb-3">
              How It Works
            </h2>
            <p className="text-muted-foreground">
              From an idea to a finished storybook in under 5 minutes.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: Wand2,
                step: "1",
                title: "Describe your story",
                text: "Tell us your child's name, the characters, and the kind of adventure. Or pick from our curated prompts.",
              },
              {
                icon: Palette,
                step: "2",
                title: "Pick an art style",
                text: "Choose from 10 gorgeous illustration styles — from Pixar-like 3D animation to hand-felted plushies.",
              },
              {
                icon: BookOpen,
                step: "3",
                title: "Read, share, keep",
                text: "Get a 10-15 scene illustrated storybook you can read on any device, share, and download as PDF.",
              },
            ].map(({ icon: Icon, step, title, text }) => (
              <div
                key={step}
                className="relative bg-white rounded-2xl p-6 shadow-sm"
              >
                <div className="absolute -top-3 -left-3 h-8 w-8 rounded-full bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] font-bold text-sm flex items-center justify-center shadow-md">
                  {step}
                </div>
                <div className="mb-4 h-12 w-12 rounded-xl bg-[var(--color-pastel-lavender)] flex items-center justify-center">
                  <Icon className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="font-bold text-[var(--color-warm-brown)] mb-2">
                  {title}
                </h3>
                <p className="text-sm text-muted-foreground">{text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Art Styles */}
      <ArtStyleShowcase />

      {/* Testimonials */}
      <Testimonials />

      {/* Final CTA */}
      <section className="bg-gradient-to-r from-[var(--color-pastel-pink)] via-[var(--color-pastel-lavender)] to-[var(--color-pastel-sky)] py-16">
        <div className="mx-auto max-w-3xl px-4 text-center">
          <h2 className="text-3xl font-bold text-[var(--color-warm-brown)] mb-4">
            Ready to create a one-of-a-kind story?
          </h2>
          <p className="text-foreground/80 mb-8 text-lg">
            Your child deserves to be the hero of their own bedtime story.
          </p>
          <Link href="/create">
            <Button
              size="lg"
              className="text-base px-8 py-6 rounded-2xl bg-white text-[var(--color-warm-brown)] hover:bg-white/90 shadow-lg gap-2"
            >
              <Heart className="h-5 w-5" />
              Start Creating
            </Button>
          </Link>
        </div>
      </section>
    </>
  );
}
