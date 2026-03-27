"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { STORY_CATEGORIES } from "@/lib/constants";

export function CategoryPills() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const activeCategory = searchParams.get("category");

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

  return (
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
  );
}
