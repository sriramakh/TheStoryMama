import { Palette, Wand2, BookOpen } from "lucide-react";

const steps = [
  {
    icon: Wand2,
    title: "Describe Your Story",
    description:
      "Tell us about the adventure you'd like — a brave penguin, a magical forest, a sleepy bunny. Or let our AI surprise you!",
    color: "bg-[var(--color-pastel-lavender)]",
    iconColor: "text-purple-500",
  },
  {
    icon: Palette,
    title: "We Create the Magic",
    description:
      "Our AI crafts a beautiful illustrated story with 10-15 scenes in your chosen art style — from Pixar 3D to Studio Ghibli.",
    color: "bg-[var(--color-pastel-pink)]",
    iconColor: "text-pink-500",
  },
  {
    icon: BookOpen,
    title: "Read Together",
    description:
      "Enjoy the story online, download the PDF storybook, or watch the video version. Perfect for bedtime!",
    color: "bg-[var(--color-pastel-mint)]",
    iconColor: "text-emerald-500",
  },
];

export function HowItWorks() {
  return (
    <section className="py-16 sm:py-20 bg-[var(--color-pastel-cream)]/50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-14">
          <h2 className="text-3xl font-bold text-[var(--color-warm-brown)] font-[family-name:var(--font-quicksand)] sm:text-4xl">
            How It Works
          </h2>
          <p className="mt-3 text-muted-foreground text-lg">
            Creating a personalized story is as easy as 1-2-3
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12">
          {steps.map((step, index) => (
            <div key={step.title} className="text-center">
              <div className="relative inline-flex">
                <div
                  className={`${step.color} h-20 w-20 rounded-3xl flex items-center justify-center shadow-sm`}
                >
                  <step.icon className={`h-9 w-9 ${step.iconColor}`} />
                </div>
                <div className="absolute -top-2 -right-2 h-7 w-7 rounded-full bg-white shadow-sm flex items-center justify-center text-sm font-bold text-[var(--color-warm-brown)]">
                  {index + 1}
                </div>
              </div>
              <h3 className="mt-5 text-xl font-semibold text-[var(--color-warm-brown)]">
                {step.title}
              </h3>
              <p className="mt-2 text-muted-foreground leading-relaxed">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
