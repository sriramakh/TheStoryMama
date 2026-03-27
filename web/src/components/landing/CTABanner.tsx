import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Heart, BookOpen } from "lucide-react";

export function CTABanner() {
  return (
    <section className="py-16 sm:py-20">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[var(--color-pastel-pink)] via-[var(--color-pastel-lavender)] to-[var(--color-pastel-sky)] p-10 sm:p-14 text-center">
          {/* Decorative blobs */}
          <div className="absolute top-4 left-8 w-20 h-20 rounded-full bg-white/20 blur-xl" />
          <div className="absolute bottom-4 right-8 w-24 h-24 rounded-full bg-white/20 blur-xl" />

          <h2 className="relative text-3xl sm:text-4xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
            Make Bedtime the Best Part of the Day
          </h2>
          <p className="relative mt-4 text-lg text-[var(--color-warm-brown)]/80 max-w-xl mx-auto">
            Whether it&apos;s a cozy story before sleep or a rainy afternoon
            adventure, every story becomes a memory you share together.
          </p>
          <div className="relative mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/library">
              <Button
                size="lg"
                className="text-base px-8 py-6 rounded-2xl bg-white text-[var(--color-warm-brown)] hover:bg-white/90 shadow-lg gap-2"
              >
                <BookOpen className="h-5 w-5" />
                Browse Stories
              </Button>
            </Link>
            <Link href="/create">
              <Button
                size="lg"
                variant="ghost"
                className="text-base px-8 py-6 rounded-2xl text-[var(--color-warm-brown)] hover:bg-white/20 gap-2"
              >
                <Heart className="h-5 w-5" />
                Create One for Your Child
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
