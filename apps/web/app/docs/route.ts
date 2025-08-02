import { redirect } from 'next/navigation';

export function GET() {
  // Redirect to docs subdomain
  // Update this URL once docs.neurascale.io is configured
  redirect('https://docs-nextra-neurascale.vercel.app');
}
