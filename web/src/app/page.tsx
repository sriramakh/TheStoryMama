
import { Hero } from "@/components/landing/Hero";
import { PersonalizedSections } from "@/components/landing/PersonalizedSections";
import { FeaturedStories } from "@/components/landing/FeaturedStories";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { ArtStyleShowcase } from "@/components/landing/ArtStyleShowcase";
import { Testimonials } from "@/components/landing/Testimonials";
import { CTABanner } from "@/components/landing/CTABanner";

const homepageJsonLd = [
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "TheStoryMama",
    url: "https://www.thestorymama.club",
    logo: "https://www.thestorymama.club/og-logo.png",
    description:
      "Free & personalized illustrated bedtime stories for children aged 2-8.",
    sameAs: [],
  },
  {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "TheStoryMama",
    url: "https://www.thestorymama.club",
    potentialAction: {
      "@type": "SearchAction",
      target:
        "https://www.thestorymama.club/library?search={search_term_string}",
      "query-input": "required name=search_term_string",
    },
  },
];

export default function HomePage() {
  return (
    <>
      <script
        id="homepage-jsonld"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(homepageJsonLd) }}
      />
      <Hero />
      <PersonalizedSections />
      <FeaturedStories />
      <HowItWorks />
      <ArtStyleShowcase />
      <Testimonials />
      <CTABanner />
    </>
  );
}
