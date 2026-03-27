import Link from "next/link";
import { Button } from "@/components/ui/button";
import { BookOpen, Sparkles, Star } from "lucide-react";

export function Hero() {
  return (
    <section className="relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-[var(--color-pastel-pink)]/30 via-[var(--color-pastel-lavender)]/20 to-[var(--color-pastel-sky)]/30" />

      {/* Floating decorations */}
      <div className="absolute top-20 left-10 w-16 h-16 rounded-full bg-[var(--color-pastel-yellow)]/40 blur-xl" />
      <div className="absolute top-40 right-20 w-24 h-24 rounded-full bg-[var(--color-pastel-mint)]/40 blur-xl" />
      <div className="absolute bottom-20 left-1/4 w-20 h-20 rounded-full bg-[var(--color-pastel-lavender)]/40 blur-xl" />
      <div className="absolute bottom-10 right-1/3 w-14 h-14 rounded-full bg-[var(--color-pastel-peach)]/40 blur-xl" />

      <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-28 lg:px-8 lg:py-36">
        <div className="text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 rounded-full bg-white/60 px-4 py-1.5 text-sm font-medium text-[var(--color-warm-brown)] shadow-sm backdrop-blur-sm mb-6">
            <Star className="h-3.5 w-3.5 fill-[var(--color-pastel-yellow)] text-[var(--color-pastel-yellow)]" />
            1000+ Free Bedtime Stories
            <Star className="h-3.5 w-3.5 fill-[var(--color-pastel-yellow)] text-[var(--color-pastel-yellow)]" />
          </div>

          {/* Heading */}
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl lg:text-6xl font-[family-name:var(--font-quicksand)]">
            <span className="text-[var(--color-warm-brown)]">
              Magical Bedtime Stories,
            </span>
            <br />
            <span className="bg-gradient-to-r from-[#E8829A] via-[#B8A9D4] to-[#7EC8D8] bg-clip-text text-transparent">
              Made Just for Your Little One
            </span>
          </h1>

          {/* Subtitle */}
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground sm:text-xl">
            Beautiful illustrated storybooks crafted with AI magic. Browse our
            free library or create personalized adventures starring your child&apos;s
            favorite characters.
          </p>

          {/* CTA Buttons */}
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/library">
              <Button
                size="lg"
                className="text-base px-8 py-6 rounded-2xl bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)] shadow-lg shadow-[var(--color-pastel-pink)]/30 transition-all hover:shadow-xl hover:-translate-y-0.5 gap-2"
              >
                <BookOpen className="h-5 w-5" />
                Browse Free Stories
              </Button>
            </Link>
            <Link href="/create">
              <Button
                size="lg"
                variant="outline"
                className="text-base px-8 py-6 rounded-2xl border-2 border-[var(--color-pastel-lavender)] hover:bg-[var(--color-pastel-lavender)]/30 shadow-sm gap-2"
              >
                <Sparkles className="h-5 w-5" />
                Create a Custom Story
              </Button>
            </Link>
          </div>

          {/* Trust signals */}
          <div className="mt-12 flex flex-wrap items-center justify-center gap-6 text-sm text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <div className="flex -space-x-1">
                {["bg-[var(--color-pastel-pink)]", "bg-[var(--color-pastel-lavender)]", "bg-[var(--color-pastel-mint)]", "bg-[var(--color-pastel-peach)]"].map((bg, i) => (
                  <div key={i} className={`h-6 w-6 rounded-full ${bg} border-2 border-white`} />
                ))}
              </div>
              <span>Loved by 2,000+ parents</span>
            </div>
            <div className="flex items-center gap-1">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="h-4 w-4 fill-[var(--color-pastel-yellow)] text-[var(--color-pastel-yellow)]" />
              ))}
              <span className="ml-1">4.9/5 rating</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
