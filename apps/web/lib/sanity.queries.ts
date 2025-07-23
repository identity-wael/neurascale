import { groq } from 'next-sanity';
import { sanityFetch } from './sanity.fetch';

// Page content query
export const pageContentQuery = groq`
  *[_type == "page" && slug.current == $slug][0] {
    _id,
    title,
    slug,
    content,
    seo {
      title,
      description,
      image
    }
  }
`;

// Get page content by slug
export async function getPageContent(slug: string) {
  return sanityFetch({
    query: pageContentQuery,
    params: { slug },
    tags: [`page:${slug}`],
  });
}

// Home page content query
export const homePageQuery = groq`
  *[_type == "homePage"][0] {
    _id,
    title,
    hero {
      title,
      subtitle,
      cta {
        text,
        link
      }
    },
    sections[] {
      _type,
      _key,
      title,
      content,
      // Add more section fields as needed
    },
    seo {
      title,
      description,
      image
    }
  }
`;

// Get home page content
export async function getHomePageContent() {
  // For now, return mock data that matches the expected structure
  // TODO: Update this to fetch real data from Sanity once content types are set up
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
