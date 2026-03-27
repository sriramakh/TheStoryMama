import Link from "next/link";
import Image from "next/image";
import { Heart } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border/40 bg-[var(--color-pastel-cream)]">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div className="col-span-1 sm:col-span-2 lg:col-span-1">
            <Link href="/" className="flex items-center gap-2">
              <Image
                src="/logo.png"
                alt="TheStoryMama"
                width={32}
                height={32}
                className="rounded-lg"
              />
              <span className="text-lg font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
                TheStoryMama
              </span>
            </Link>
            <p className="mt-3 text-sm text-muted-foreground max-w-xs">
              Magical bedtime stories crafted with love for your little ones.
              Browse free stories or create personalized adventures.
            </p>
          </div>

          {/* Stories */}
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-3">
              Stories
            </h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/library"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Story Library
                </Link>
              </li>
              <li>
                <Link
                  href="/library?category=bedtime"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Bedtime Stories
                </Link>
              </li>
              <li>
                <Link
                  href="/library?category=animals"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Animal Stories
                </Link>
              </li>
              <li>
                <Link
                  href="/library?category=adventure"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Adventure Stories
                </Link>
              </li>
            </ul>
          </div>

          {/* Create */}
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-3">
              Create
            </h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/create"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Create a Story
                </Link>
              </li>
              <li>
                <Link
                  href="/pricing"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Pricing
                </Link>
              </li>
              <li>
                <Link
                  href="/dashboard"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  My Stories
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-3">
              Support
            </h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/about"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  About Us
                </Link>
              </li>
              <li>
                <Link
                  href="/contact"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Contact
                </Link>
              </li>
              <li>
                <Link
                  href="/privacy"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link
                  href="/terms"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-10 border-t border-border/40 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} TheStoryMama. All rights reserved.
          </p>
          <p className="text-sm text-muted-foreground flex items-center gap-1">
            Made with{" "}
            <Heart className="h-3.5 w-3.5 fill-[var(--color-pastel-rose)] text-[var(--color-pastel-rose)]" />{" "}
            for little dreamers everywhere
          </p>
        </div>
      </div>
    </footer>
  );
}
