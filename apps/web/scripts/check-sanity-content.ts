import { createClient } from '@sanity/client';
import dotenv from 'dotenv';
import path from 'path';

// Load environment variables
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

const client = createClient({
  projectId: 'vvsy01fb',
  dataset: 'production',
  apiVersion: '2024-01-01',
  token: process.env.SANITY_API_TOKEN,
  useCdn: false,
});

async function checkSanityContent() {
  console.log('Checking Sanity content...\n');

  try {
    // Get all document types
    const query = `*[_type in ["hero", "vision", "problem", "roadmap", "team", "resources", "contact"]] {
      _id,
      _type,
      _createdAt,
      _updatedAt,
      title
    }`;

    const documents = await client.fetch(query);

    console.log(`Found ${documents.length} documents in Sanity:\n`);

    // Group by type
    const byType = documents.reduce((acc: any, doc: any) => {
      if (!acc[doc._type]) acc[doc._type] = [];
      acc[doc._type].push(doc);
      return acc;
    }, {});

    // Display summary
    Object.entries(byType).forEach(([type, docs]: [string, any]) => {
      console.log(`${type}: ${docs.length} document(s)`);
      docs.forEach((doc: any) => {
        console.log(`  - ${doc._id} (${doc.title || 'No title'})`);
        console.log(`    Created: ${new Date(doc._createdAt).toLocaleString()}`);
        console.log(`    Updated: ${new Date(doc._updatedAt).toLocaleString()}`);
      });
      console.log('');
    });

    // Check for specific main documents
    console.log('Checking main documents:');
    const mainDocs = [
      'hero-main',
      'vision-main',
      'problem-main',
      'roadmap-main',
      'team-main',
      'resources-main',
      'contact-main',
    ];

    for (const docId of mainDocs) {
      const doc = await client.fetch(`*[_id == "${docId}"][0]`);
      console.log(`${docId}: ${doc ? '✅ Exists' : '❌ Missing'}`);
    }
  } catch (error: any) {
    console.error('Error checking content:', error.message);
  }
}

checkSanityContent();
