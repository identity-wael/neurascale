import { sanityFetch } from '@/lib/sanity.client';
import { HeroContent } from '@/types/sanity';
import HeroClient from './HeroClient';

const HERO_QUERY = `*[_type == "hero" && _id == "hero-main"][0]`;

export default async function HeroWithSanity() {
  const content = await sanityFetch<HeroContent>({
    query: HERO_QUERY,
  });

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
      title={content.title || 'Neural-Prosthetics Application Cloud'}
      subtitle={
        content.subtitle ||
        'An open-source project designed to process petabytes of complex brain data, blurring the boundaries between the human mind and the real world.'
      }
      ctaText={content.cta?.text || 'Get Started'}
      ctaLink={content.cta?.href || '#contact'}
    />
  );
}
