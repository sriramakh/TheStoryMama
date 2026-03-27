import { Card, CardContent } from "@/components/ui/card";
import { Star } from "lucide-react";

const testimonials = [
  {
    name: "Sarah M.",
    role: "Mom of 2",
    text: "My daughter asks for a new story every single night now. The illustrations are absolutely gorgeous — she thinks they're real picture books!",
    rating: 5,
    avatar: "bg-[var(--color-pastel-pink)]",
  },
  {
    name: "David K.",
    role: "Dad of 1",
    text: "We created a story with our son as the main character. He was SO excited seeing himself in a Pixar-style adventure. Worth every penny.",
    rating: 5,
    avatar: "bg-[var(--color-pastel-sky)]",
  },
  {
    name: "Priya R.",
    role: "Mom of 3",
    text: "The free story library is incredible. We've read dozens already and the quality is consistently amazing. My kids love the animal stories!",
    rating: 5,
    avatar: "bg-[var(--color-pastel-mint)]",
  },
  {
    name: "Emily T.",
    role: "Grandma",
    text: "I create custom stories for each of my grandchildren as birthday gifts. The PDF storybooks print beautifully — they treasure them!",
    rating: 5,
    avatar: "bg-[var(--color-pastel-lavender)]",
  },
];

export function Testimonials() {
  return (
    <section className="py-16 sm:py-20 bg-[var(--color-pastel-cream)]/50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)] sm:text-4xl">
            Loved by Parents
          </h2>
          <p className="mt-3 text-muted-foreground text-lg">
            See what families are saying about TheStoryMama
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {testimonials.map((t) => (
            <Card
              key={t.name}
              className="border-0 shadow-sm hover:shadow-md transition-shadow"
            >
              <CardContent className="p-6">
                <div className="flex gap-0.5 mb-3">
                  {[...Array(t.rating)].map((_, i) => (
                    <Star
                      key={i}
                      className="h-4 w-4 fill-[var(--color-pastel-yellow)] text-[var(--color-pastel-yellow)]"
                    />
                  ))}
                </div>
                <p className="text-sm text-foreground/80 leading-relaxed mb-4">
                  &ldquo;{t.text}&rdquo;
                </p>
                <div className="flex items-center gap-3">
                  <div
                    className={`h-8 w-8 rounded-full ${t.avatar} flex items-center justify-center text-xs font-bold text-[var(--color-warm-brown)]`}
                  >
                    {t.name[0]}
                  </div>
                  <div>
                    <p className="text-sm font-semibold">{t.name}</p>
                    <p className="text-xs text-muted-foreground">{t.role}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
