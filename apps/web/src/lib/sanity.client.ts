import { createClient } from '@sanity/client';

// Ensure environment variables are defined
const projectId = process.env.NEXT_PUBLIC_SANITY_PROJECT_ID || 'vvsy01fb';
const dataset = process.env.NEXT_PUBLIC_SANITY_DATASET || 'production';
const apiVersion = process.env.NEXT_PUBLIC_SANITY_API_VERSION || '2024-01-01';

export const client = createClient({
  projectId,
  dataset,
  apiVersion,
  useCdn: process.env.NODE_ENV === 'production',
});

// Helper function to fetch content
export async function sanityFetch<T = any>(
  query: string,
  params: Record<string, any> = {}
): Promise<T> {
  return client.fetch(query, params);
}
