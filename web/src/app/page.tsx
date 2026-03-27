import { Hero } from "@/components/landing/Hero";
import { FeaturedStories } from "@/components/landing/FeaturedStories";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { ArtStyleShowcase } from "@/components/landing/ArtStyleShowcase";
import { Testimonials } from "@/components/landing/Testimonials";
import { CTABanner } from "@/components/landing/CTABanner";

export default function HomePage() {
  return (
    <>
      <Hero />
      <FeaturedStories />
      <HowItWorks />
      <ArtStyleShowcase />
      <Testimonials />
      <CTABanner />
    </>
  );
}
