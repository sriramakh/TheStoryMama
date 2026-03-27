import Link from "next/link";
import { Button } from "@/components/ui/button";
import { BookOpen, Heart } from "lucide-react";

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
            <Heart className="h-3.5 w-3.5 fill-[var(--color-pastel-rose)] text-[var(--color-pastel-rose)]" />
            100+ Free Bedtime Stories
            <Heart className="h-3.5 w-3.5 fill-[var(--color-pastel-rose)] text-[var(--color-pastel-rose)]" />
          </div>

          {/* Heading */}
          <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl lg:text-6xl font-[family-name:var(--font-quicksand)]">
            <span className="text-[var(--color-warm-brown)]">
              Magical Bedtime Stories,
            </span>
            <br />
            <span className="text-[var(--color-warm-brown)]">
              From Mom &amp; Dad,{" "}
            </span>
            <span className="bg-gradient-to-r from-[#E8829A] via-[#B8A9D4] to-[#7EC8D8] bg-clip-text text-transparent">
              With Love
            </span>
          </h1>

          {/* Subtitle */}
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground sm:text-xl leading-relaxed">
            Beautiful illustrated storybooks made just for your little one.
            Browse our free library of bedtime favorites or create a personalized
            adventure starring characters your child will love.
          </p>

          {/* CTA Buttons */}
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/library">
              <Button
                size="lg"
                className="text-base px-8 py-6 rounded-2xl bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] hover:bg-[var(--color-pastel-rose)] shadow-lg shadow-[var(--color-pastel-pink)]/30 transition-all hover:shadow-xl hover:-translate-y-0.5 gap-2"
              >
                <BookOpen className="h-5 w-5" />
                Read Free Stories
              </Button>
            </Link>
            <Link href="/create">
              <Button
                size="lg"
                variant="outline"
                className="text-base px-8 py-6 rounded-2xl border-2 border-[var(--color-pastel-lavender)] hover:bg-[var(--color-pastel-lavender)]/30 shadow-sm gap-2"
              >
                <Heart className="h-5 w-5" />
                Create a Story for Your Child
              </Button>
            </Link>
          </div>

          {/* Warm trust signal — personal, not corporate */}
          <p className="mt-12 text-sm text-muted-foreground italic">
            Bedtime stories that bring families closer, one page at a time.
          </p>
        </div>
      </div>
    </section>
  );
}
