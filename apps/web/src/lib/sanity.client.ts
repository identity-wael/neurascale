import { createClient } from '@sanity/client';

export const client = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID!,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET!,
  apiVersion: process.env.NEXT_PUBLIC_SANITY_API_VERSION!,
  useCdn: process.env.NODE_ENV === 'production',
});

// Helper function to fetch content
export async function sanityFetch<T = any>(
  query: string,
  params: Record<string, any> = {}
): Promise<T> {
  return client.fetch(query, params);
}
