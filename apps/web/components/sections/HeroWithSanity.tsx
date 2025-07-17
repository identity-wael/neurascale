import { sanityFetch } from '@/lib/sanity.client';
import { HeroContent } from '@/types/sanity';
import HeroClient from './HeroClient';

const HERO_QUERY = `*[_type == "hero" && _id == "hero-main"][0]`;

export default async function HeroWithSanity() {
  const content = await sanityFetch<HeroContent>(HERO_QUERY);

  if (!content) {
    // Fallback content in case Sanity is not available
    return (
      <HeroClient
        title="Neural-Prosthetics Application Cloud"
        subtitle="An open-source project designed to process petabytes of complex brain data, blurring the boundaries between the human mind and the real world."
        ctaText="Get Started"
        ctaLink="#contact"
      />
    );
  }

  return (
    <HeroClient
      title={content.title}
      subtitle={content.subtitle}
      ctaText={content.ctaText}
      ctaLink={content.ctaLink}
    />
  );
}
