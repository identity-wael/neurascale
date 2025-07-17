import { sanityFetch } from '@/lib/sanity.client';
import { VisionContent } from '@/types/sanity';
import VisionClient from './VisionClient';

const VISION_QUERY = `*[_type == "vision" && _id == "vision-main"][0]`;

export default async function VisionWithSanity() {
  const content = await sanityFetch<VisionContent>(VISION_QUERY);

  if (!content) {
    return null; // Or return a fallback component
  }

  return <VisionClient content={content} />;
}
