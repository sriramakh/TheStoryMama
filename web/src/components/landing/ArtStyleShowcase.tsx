import { ANIMATION_STYLES } from "@/lib/constants";

const styleColors = [
  "bg-[var(--color-pastel-pink)]",
  "bg-[var(--color-pastel-lavender)]",
  "bg-[var(--color-pastel-sky)]",
  "bg-[var(--color-pastel-mint)]",
  "bg-[var(--color-pastel-yellow)]",
  "bg-[var(--color-pastel-peach)]",
  "bg-[var(--color-pastel-pink)]",
  "bg-[var(--color-pastel-lavender)]",
  "bg-[var(--color-pastel-sky)]",
  "bg-[var(--color-pastel-mint)]",
];

export function ArtStyleShowcase() {
  return (
    <section className="py-16 sm:py-20">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)] sm:text-4xl">
            10 Beautiful Art Styles
          </h2>
          <p className="mt-3 text-muted-foreground text-lg">
            Every story is a unique work of art in the style you choose
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {ANIMATION_STYLES.map((style, i) => (
            <div
              key={style.id}
              className={`${styleColors[i]} rounded-2xl p-6 text-center transition-transform hover:-translate-y-1 hover:shadow-md cursor-default`}
            >
              <span className="text-3xl">{style.preview}</span>
              <p className="mt-2 text-sm font-semibold text-[var(--color-warm-brown)]">
                {style.name}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
