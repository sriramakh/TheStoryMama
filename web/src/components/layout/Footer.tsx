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
            <div className="flex items-center gap-3 mt-4">
              <a
                href="https://www.instagram.com/thestorymama/"
                target="_blank"
                rel="noopener noreferrer"
                className="h-9 w-9 rounded-full bg-white flex items-center justify-center hover:bg-[var(--color-pastel-pink)] transition-colors"
                aria-label="Instagram"
              >
                <svg className="h-4.5 w-4.5 text-[var(--color-warm-brown)]" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/>
                </svg>
              </a>
              <a
                href="https://www.youtube.com/@Thestorymamaofficial"
                target="_blank"
                rel="noopener noreferrer"
                className="h-9 w-9 rounded-full bg-white flex items-center justify-center hover:bg-[var(--color-pastel-pink)] transition-colors"
                aria-label="YouTube"
              >
                <svg className="h-4.5 w-4.5 text-[var(--color-warm-brown)]" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
              </a>
            </div>
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
                  href="/bedtime-stories-for-kids"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Bedtime Stories
                </Link>
              </li>
              <li>
                <Link
                  href="/animal-stories-for-children"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Animal Stories
                </Link>
              </li>
              <li>
                <Link
                  href="/adventure-stories-for-kids"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Adventure Stories
                </Link>
              </li>
              <li>
                <Link
                  href="/fantasy-stories-for-children"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Fantasy Stories
                </Link>
              </li>
              <li>
                <Link
                  href="/friendship-stories-for-kids"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Friendship Stories
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
