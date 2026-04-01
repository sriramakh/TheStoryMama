import type { Metadata } from "next";
import { Mail } from "lucide-react";

export const metadata: Metadata = {
  title: "Contact Us",
  description: "Get in touch with TheStoryMama",
};

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-[var(--color-pastel-cream)]/30">
      <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)]">
            Get in Touch
          </h1>
          <p className="mt-3 text-muted-foreground text-lg">
            We&apos;d love to hear from you
          </p>
        </div>

        <div className="space-y-6">
          {/* Email */}
          <a
            href="mailto:hello@thestorymama.club"
            className="block bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-xl bg-[var(--color-pastel-pink)] flex items-center justify-center flex-shrink-0">
                <Mail className="h-6 w-6 text-[var(--color-warm-brown)]" />
              </div>
              <div>
                <h3 className="font-semibold text-[var(--color-warm-brown)]">
                  Email Us
                </h3>
                <p className="text-primary text-sm mt-0.5">
                  hello@thestorymama.club
                </p>
              </div>
            </div>
          </a>

          {/* Instagram */}
          <a
            href="https://www.instagram.com/thestorymama/"
            target="_blank"
            rel="noopener noreferrer"
            className="block bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-xl bg-[var(--color-pastel-lavender)] flex items-center justify-center flex-shrink-0">
                <svg className="h-6 w-6 text-[var(--color-warm-brown)]" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-[var(--color-warm-brown)]">
                  Message Us on Instagram
                </h3>
                <p className="text-primary text-sm mt-0.5">
                  @thestorymama
                </p>
              </div>
            </div>
          </a>
        </div>

        <p className="text-center text-sm text-muted-foreground mt-12">
          We typically respond within 24 hours.
        </p>
      </div>
    </div>
  );
}
