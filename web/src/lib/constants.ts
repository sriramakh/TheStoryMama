export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const FASTSPRING_STOREFRONT = "thestorymama.test.onfastspring.com";

export const STORY_CATEGORIES = [
  { id: "animals", label: "Animals", emoji: "🐻" },
  { id: "adventure", label: "Adventure", emoji: "🗺️" },
  { id: "friendship", label: "Friendship", emoji: "🤝" },
  { id: "fantasy", label: "Fantasy", emoji: "✨" },
  { id: "nature", label: "Nature", emoji: "🌿" },
  { id: "family", label: "Family", emoji: "👨‍👩‍👧" },
  { id: "seasons", label: "Seasons", emoji: "🍂" },
  { id: "bedtime", label: "Bedtime", emoji: "🌙" },
  { id: "funny", label: "Funny", emoji: "😄" },
  { id: "learning", label: "Learning", emoji: "📚" },
] as const;

export const PRICING_PLANS = [
  {
    id: "pack_5",
    name: "Starter Pack",
    price: 9.99,
    period: "one-time",
    credits: 5,
    description: "Perfect for trying it out",
    features: [
      "5 custom stories",
      "All 10 art styles",
      "PDF downloads",
      "Never expires",
    ],
  },
  {
    id: "monthly_10",
    name: "Monthly",
    price: 12.99,
    period: "month",
    credits: 10,
    description: "For regular bedtime readers",
    features: [
      "10 stories per month",
      "All 10 art styles",
      "PDF downloads",
      "Video storybooks",
      "Cancel anytime",
    ],
    popular: true,
  },
  {
    id: "yearly_15",
    name: "Annual",
    price: 99,
    period: "year",
    credits: 15,
    description: "Best value for story lovers",
    features: [
      "15 stories per month",
      "All 10 art styles",
      "PDF downloads",
      "Video storybooks",
      "Priority generation",
      "Save 37%",
    ],
    bestValue: true,
  },
] as const;

export const ANIMATION_STYLES = [
  { id: "animation_movie", name: "Animation Movie", preview: "🎬" },
  { id: "claymation", name: "Claymation", preview: "🧸" },
  { id: "paper_cutout", name: "Paper Cutout", preview: "✂️" },
  { id: "glowlight_fantasy", name: "Glowlight Fantasy", preview: "🌟" },
  { id: "felt_plushie", name: "Felt & Plushie", preview: "🧵" },
  { id: "stained_glass", name: "Stained Glass", preview: "🪟" },
  { id: "toy_diorama", name: "Toy Diorama", preview: "🏠" },
  { id: "crochet_amigurumi", name: "Crochet Amigurumi", preview: "🧶" },
  { id: "candy_clay", name: "Candy Clay", preview: "🍬" },
  { id: "picture_book_collage", name: "Picture Book Collage", preview: "🎨" },
] as const;
