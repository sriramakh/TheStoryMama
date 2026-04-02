"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { STORY_CATEGORIES } from "@/lib/constants";

export function CategoryPills() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const activeCategory = searchParams.get("category");
  const activeOrientation = searchParams.get("orientation");

  function handleCategory(categoryId: string | null) {
    const params = new URLSearchParams(searchParams.toString());
    if (categoryId) {
      params.set("category", categoryId);
    } else {
      params.delete("category");
    }
    params.delete("page");
    router.push(`/library?${params.toString()}`);
  }

  function handleOrientation(orientation: string | null) {
    const params = new URLSearchParams(searchParams.toString());
    if (orientation) {
      params.set("orientation", orientation);
    } else {
      params.delete("orientation");
    }
    params.delete("page");
    router.push(`/library?${params.toString()}`);
  }

  return (
    <div className="space-y-3">
      {/* Orientation filter */}
      <div className="flex gap-2">
        <button
          onClick={() => handleOrientation(null)}
          className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
            !activeOrientation
              ? "bg-[var(--color-pastel-lavender)] text-[var(--color-warm-brown)] shadow-sm"
              : "bg-white text-muted-foreground hover:bg-[var(--color-pastel-cream)]"
          }`}
        >
          All Formats
        </button>
        <button
          onClick={() => handleOrientation("portrait")}
          className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
            activeOrientation === "portrait"
              ? "bg-[var(--color-pastel-lavender)] text-[var(--color-warm-brown)] shadow-sm"
              : "bg-white text-muted-foreground hover:bg-[var(--color-pastel-cream)]"
          }`}
        >
          Portrait
        </button>
        <button
          onClick={() => handleOrientation("landscape")}
          className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
            activeOrientation === "landscape"
              ? "bg-[var(--color-pastel-lavender)] text-[var(--color-warm-brown)] shadow-sm"
              : "bg-white text-muted-foreground hover:bg-[var(--color-pastel-cream)]"
          }`}
        >
          Landscape
        </button>
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => handleCategory(null)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            !activeCategory
              ? "bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] shadow-sm"
              : "bg-white text-muted-foreground hover:bg-[var(--color-pastel-cream)]"
          }`}
        >
          All Stories
        </button>
        {STORY_CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => handleCategory(cat.id)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              activeCategory === cat.id
                ? "bg-[var(--color-pastel-pink)] text-[var(--color-warm-brown)] shadow-sm"
                : "bg-white text-muted-foreground hover:bg-[var(--color-pastel-cream)]"
            }`}
          >
            {cat.emoji} {cat.label}
          </button>
        ))}
      </div>
    </div>
  );
}
