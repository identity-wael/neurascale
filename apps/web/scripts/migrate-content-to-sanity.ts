import { createClient } from '@sanity/client';
import dotenv from 'dotenv';
import path from 'path';

// Load environment variables from .env.local
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

// Initialize Sanity client
const client = createClient({
  projectId: 'vvsy01fb',
  dataset: 'production',
  apiVersion: '2024-01-01',
  token: process.env.SANITY_API_TOKEN, // You'll need to create this
  useCdn: false,
});

// Content extracted from your website
const websiteContent = {
  hero: {
    _type: 'hero',
    title: 'Neural-Prosthetics Application Cloud',
    subtitle:
      'An open-source project designed to process petabytes of complex brain data, blurring the boundaries between the human mind and the real world.',
    ctaText: 'Get Started',
    ctaLink: '#contact',
  },
  vision: {
    _type: 'vision',
    sectionHeader: 'VISION',
    title: 'Bridging minds and reality',
    mainStat: '20M',
    mainStatDescription:
      'people worldwide live with paralysis from spinal cord injury and stroke—their minds fully capable but physically separated from the world.',
    stat1Value: '5.4M',
    stat1Label: 'New injuries annually',
    stat2Value: '100%',
    stat2Label: 'Mental capacity intact',
    solutionTitle: 'NEURASCALE breaks down these barriers',
    solutionPoints: [
      {
        _key: 'point1',
        text: 'Restored mobility through neural prosthetics',
        highlight: 'Restored mobility',
      },
      {
        _key: 'point2',
        text: 'Advanced robotics control with thought',
        highlight: 'Advanced robotics control',
      },
      {
        _key: 'point3',
        text: 'Immersive reality experiences beyond physical limits',
        highlight: 'Immersive reality experiences',
      },
    ],
    solutionDescription:
      'Through real-time neural signal processing at unprecedented scale and precision',
  },
};

async function migrateContent() {
  console.log('Starting content migration to Sanity...');
  console.log('Using token:', process.env.SANITY_API_TOKEN ? 'Token found' : 'No token found');

  try {
    // Test permissions first
    console.log('\nTesting API permissions...');
    await client.fetch('*[_type == "hero"][0]');
    console.log('✅ Read permission confirmed');

    // Create or update Hero content
    console.log('\nMigrating Hero content...');
    const heroResult = await client.createOrReplace({
      _id: 'hero-main', // Fixed ID so we can update it
      ...websiteContent.hero,
    });
    console.log('✅ Hero content created/updated:', heroResult._id);

    // Create or update Vision content
    console.log('\nMigrating Vision content...');
    const visionResult = await client.createOrReplace({
      _id: 'vision-main',
      ...websiteContent.vision,
    });
    console.log('✅ Vision content created/updated:', visionResult._id);

    console.log('\n🎉 Content migration completed!');
    console.log('\nNext steps:');
    console.log('1. Visit http://localhost:3000/studio');
    console.log('2. You should see the Hero and Vision content populated');
    console.log('3. Add more schemas to migrate Problem, Team, and other sections');
  } catch (error: any) {
    console.error('\n❌ Migration failed:', error.message);

    if (error.statusCode === 403) {
      console.error('\n⚠️  Permission Error Details:');
      console.error('The token does not have sufficient permissions.');
      console.error('\nTo fix this:');
      console.error('1. Go to https://sanity.io/manage/project/vvsy01fb/api');
      console.error('2. Create a new token with "Editor" or "Write" permissions');
      console.error('3. Make sure to select the "production" dataset');
      console.error('4. Replace the token in .env.local');
      console.error(
        '\nCurrent token appears to be:',
        process.env.SANITY_API_TOKEN?.substring(0, 10) + '...'
      );
    }
  }
}

// Instructions to run
console.log('To run this migration:');
console.log('1. First, create a Sanity API token:');
console.log('   - Go to https://sanity.io/manage/project/vvsy01fb/api');
console.log('   - Create a token with "Editor" or "Write" permissions');
console.log('   - Add to .env.local: SANITY_API_TOKEN=your-token');
console.log('2. Then run: npx tsx scripts/migrate-content-to-sanity.ts');
console.log('\nPress Ctrl+C to exit or uncomment the line below to run migration\n');

// Run the migration
migrateContent();
