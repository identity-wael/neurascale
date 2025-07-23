import { getHomePageContent } from '@/lib/sanity.queries';
import HomeClient from '@/components/pages/HomeClient';

export default async function Home() {
  const content = await getHomePageContent();

  return <HomeClient content={content} />;
}
