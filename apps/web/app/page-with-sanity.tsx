import { getPageContent } from '@/lib/sanity.queries';
import HomeClient from '@/components/pages/HomeClient';

export default async function Home() {
  const content = await getPageContent();

  return <HomeClient content={content} />;
}
