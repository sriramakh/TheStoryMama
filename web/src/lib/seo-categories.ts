// SEO-optimized category landing page configs.
// Each entry maps a URL slug to an API category id and the copy/meta shown on the page.

export interface CategoryPageConfig {
  /** URL path segment (e.g. "/animal-stories-for-children") */
  slug: string;
  /** API `category` filter value sent to /api/v1/library */
  categoryId: string;
  /** <h1> and page heading */
  h1: string;
  /** <title> tag */
  metaTitle: string;
  /** <meta description> */
  metaDescription: string;
  /** Intro paragraph rendered above the grid (150-200 words) */
  introCopy: string;
  /** CTA label for /create link */
  ctaLabel: string;
}

export const CATEGORY_PAGES: CategoryPageConfig[] = [
  {
    slug: "bedtime-stories-for-kids",
    categoryId: "bedtime",
    h1: "Free Bedtime Stories for Kids",
    metaTitle: "Free Bedtime Stories for Kids | TheStoryMama",
    metaDescription:
      "Read 100+ free illustrated bedtime stories for kids online. Soothing, gentle, screen-friendly stories perfect for toddlers, preschoolers, and early readers.",
    introCopy:
      "Looking for calm, gentle bedtime stories your little one will actually settle down for? TheStoryMama has a growing library of free, beautifully illustrated bedtime stories written specifically for children aged 2–5. Each story is hand-crafted with warm characters, soothing themes, and a soft emotional arc that helps wind down the day. Every illustration is made to feel cozy and safe — the perfect last thing your child sees before lights out. Browse the full collection below, tap any story, and read it together on your phone, tablet, or laptop. If you'd prefer a physical keepsake, every story is downloadable as a PDF to print at home. Bedtime reading has been shown to support language development, emotional regulation, and the parent-child bond — and at TheStoryMama, we believe that magic should be free. Want an even more special bedtime experience? Create a personalized bedtime story starring your own child — with their name, favorite colors, and the adventures they dream about.",
    ctaLabel: "Create a personalized bedtime story for your child",
  },
  {
    slug: "animal-stories-for-children",
    categoryId: "animals",
    h1: "Free Animal Stories for Children",
    metaTitle: "Free Animal Stories for Children | TheStoryMama",
    metaDescription:
      "Browse 50+ free illustrated animal bedtime stories for kids. Featuring bunnies, puppies, bees, foxes, and more — read online or download as PDF.",
    introCopy:
      "Kids love animals — and there's no better way to spark curiosity, empathy, and imagination than through a beautifully illustrated animal story. TheStoryMama has gathered dozens of free animal stories for children aged 2–5, featuring friendly bunnies, clever foxes, busy bees, loyal puppies, wise owls, and more. Each tale is gentle, age-appropriate, and designed to be read aloud at bedtime or quiet time. The vivid Pixar-inspired illustrations help your child connect names to creatures, recognize habitats, and learn how animals live and work together. Every story is free to read on any device and downloadable as a printable PDF. If your child has a favorite animal — whether it's a horse, a whale, a kitten, or a dragon — you can also create a personalized animal story starring them and their animal friend. Perfect for screen-free evenings, classroom read-alouds, and quiet-time wind-downs.",
    ctaLabel: "Want a personalized animal story? Create one for your child",
  },
  {
    slug: "adventure-stories-for-kids",
    categoryId: "adventure",
    h1: "Free Adventure Stories for Kids",
    metaTitle: "Free Adventure Stories for Kids | TheStoryMama",
    metaDescription:
      "Explore 50+ free illustrated adventure stories for kids. Treasure hunts, hidden maps, brave journeys, and happy endings — online or as printable PDF.",
    introCopy:
      "Every child dreams of an adventure — discovering a hidden map, climbing a secret hill, chasing a mystery through the woods. TheStoryMama's adventure stories deliver that thrill at a gentle, age-appropriate pace for children 2–5. Our library is filled with free, fully illustrated stories about brave little explorers, treasure hunts, magical journeys, and wonderful discoveries. Adventure stories help children build confidence, practice problem-solving, and learn that courage and kindness travel together. Each story is crafted to be read aloud in under 10 minutes, making it ideal for bedtime, rainy afternoons, or a cozy quiet-time. Download any story as a PDF, or keep reading in the browser — no signup needed. Want your child to be the hero of their own adventure? Create a personalized adventure story starring them, their friends, and the places they dream of exploring.",
    ctaLabel: "Want a personalized adventure story? Create one for your child",
  },
  {
    slug: "fantasy-stories-for-children",
    categoryId: "fantasy",
    h1: "Free Fantasy Stories for Children",
    metaTitle: "Free Fantasy Stories for Children | TheStoryMama",
    metaDescription:
      "Discover 40+ free illustrated fantasy stories for children. Dragons, fairies, magical gardens, wish-granting stars — read free or download PDF.",
    introCopy:
      "Every magical kingdom begins with a single story. TheStoryMama's fantasy story collection brings together gentle, imaginative worlds designed for children aged 2–5 — tiny fairies tending moonflower gardens, friendly dragons baking cloud bread, wish-granting stars, talking teacups, and enchanted forests where kindness is the strongest magic of all. Every story is free, fully illustrated in a warm Pixar-inspired 3D style, and written to be calming rather than scary. Fantasy stories help children stretch their imagination, explore feelings safely, and believe in the power of kindness and wonder. Read any story online on phone or tablet, or download as a PDF to print or save for later. Want to make the magic even more personal? Create a fantasy story starring your own child — they can be the hero, the fairy, or the dragon's best friend.",
    ctaLabel: "Want a personalized fantasy story? Create one for your child",
  },
  {
    slug: "friendship-stories-for-kids",
    categoryId: "friendship",
    h1: "Free Friendship Stories for Kids",
    metaTitle: "Free Friendship Stories for Kids | TheStoryMama",
    metaDescription:
      "Read 40+ free illustrated friendship stories for kids. Sharing, kindness, teamwork, and unlikely pairs — perfect bedtime stories about friendship.",
    introCopy:
      "Making a friend, keeping a friend, and learning to be one — these are some of the most important lessons a young child navigates. TheStoryMama's friendship story collection is filled with warm, free, illustrated bedtime stories about kindness, sharing, teamwork, and the unexpected magic of unlikely pairs. Perfect for children aged 2–5, each story models the small moments that make friendship bloom — inviting someone new to play, saying sorry, helping when a friend is sad, or laughing together at a silly accident. Every story is free to read online or download as a printable PDF, beautifully illustrated in a warm Pixar-style 3D look. Stories about friendship are shown to help children build empathy, communication skills, and social confidence. And if you'd like your own child to star alongside their best friend or imaginary pal, you can create a personalized friendship story with their names and the adventures you choose together.",
    ctaLabel: "Want a personalized friendship story? Create one for your child",
  },
];

export function getCategoryPageBySlug(slug: string) {
  return CATEGORY_PAGES.find((c) => c.slug === slug);
}
