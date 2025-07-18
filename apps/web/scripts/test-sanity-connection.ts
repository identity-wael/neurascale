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

async function testSanityConnection() {
  console.log('Testing Sanity connection with Editor token...\n');

  try {
    // Test 1: Read operation
    console.log('1. Testing READ operation...');
    const heroDoc = await client.fetch('*[_id == "hero-main"][0]');

    if (heroDoc) {
      console.log('✅ Read successful! Found hero document:');
      console.log(`   Title: ${heroDoc.title}`);
      console.log(`   Subtitle: ${heroDoc.subtitle?.substring(0, 50)}...`);
    } else {
      console.log('❌ Read failed: No hero document found');
    }

    // Test 2: Update operation (safe - just updating timestamp)
    console.log('\n2. Testing UPDATE operation...');
    const testUpdate = await client
      .patch('hero-main')
      .set({ lastTestedAt: new Date().toISOString() })
      .commit();

    console.log('✅ Update successful! Document updated with test timestamp');
    console.log(`   Updated at: ${testUpdate._updatedAt}`);

    // Test 3: Query multiple documents
    console.log('\n3. Testing QUERY operation...');
    const allDocs = await client.fetch(
      '*[_type in ["hero", "vision", "problem", "roadmap", "team", "resources", "contact"]] | order(_type) { _id, _type }'
    );

    console.log(`✅ Query successful! Found ${allDocs.length} documents`);

    // Test 4: Create and delete a test document
    console.log('\n4. Testing CREATE/DELETE operations...');
    await client.create({
      _type: 'hero',
      _id: 'test-doc-temporary',
      title: 'Test Document',
      subtitle: 'This is a temporary test document',
      ctaText: 'Test',
      ctaLink: '#test',
    });

    console.log('✅ Create successful! Test document created');

    // Clean up - delete the test document
    await client.delete('test-doc-temporary');
    console.log('✅ Delete successful! Test document removed');

    console.log('\n🎉 All tests passed! Your Editor token is working correctly.');
  } catch (error: any) {
    console.error('\n❌ Error:', error.message);

    if (error.statusCode === 401) {
      console.error('\n⚠️  Authentication Error:');
      console.error('The token is invalid or has been revoked.');
      console.error('Please check your SANITY_API_TOKEN in .env.local');
    } else if (error.statusCode === 403) {
      console.error('\n⚠️  Permission Error:');
      console.error('The token does not have sufficient permissions.');
      console.error("Make sure you're using an Editor token with write access.");
    } else {
      console.error('\n⚠️  Unexpected Error:');
      console.error('Details:', error);
    }
  }
}

testSanityConnection();
