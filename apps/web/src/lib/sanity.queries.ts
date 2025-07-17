import { sanityFetch } from './sanity.client';
import type {
  HeroContent,
  VisionContent,
  ProblemContent,
  RoadmapContent,
  TeamContent,
  ResourcesContent,
  ContactContent,
} from '@/types/sanity';

// Define all queries
export const queries = {
  hero: `*[_type == "hero" && _id == "hero-main"][0]`,
  vision: `*[_type == "vision" && _id == "vision-main"][0]`,
  problem: `*[_type == "problem" && _id == "problem-main"][0]`,
  roadmap: `*[_type == "roadmap" && _id == "roadmap-main"][0]`,
  team: `*[_type == "team" && _id == "team-main"][0]`,
  resources: `*[_type == "resources" && _id == "resources-main"][0]`,
  contact: `*[_type == "contact" && _id == "contact-main"][0]`,
};

// Fetch all page content
export async function getPageContent() {
  try {
    const [hero, vision, problem, roadmap, team, resources, contact] = await Promise.all([
      sanityFetch<HeroContent>(queries.hero),
      sanityFetch<VisionContent>(queries.vision),
      sanityFetch<ProblemContent>(queries.problem),
      sanityFetch<RoadmapContent>(queries.roadmap),
      sanityFetch<TeamContent>(queries.team),
      sanityFetch<ResourcesContent>(queries.resources),
      sanityFetch<ContactContent>(queries.contact),
    ]);

    return {
      hero,
      vision,
      problem,
      roadmap,
      team,
      resources,
      contact,
    };
  } catch (error) {
    console.error('Error fetching content from Sanity:', error);
    // Return null to use fallback content
    return {
      hero: null,
      vision: null,
      problem: null,
      roadmap: null,
      team: null,
      resources: null,
      contact: null,
    };
  }
}
