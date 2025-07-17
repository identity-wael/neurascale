import { getPageContent } from '@/src/lib/sanity.queries';
import { ContentProvider } from '@/src/contexts/ContentContext';
import PageClient from './page-client';

export default async function Home() {
  const content = await getPageContent();

  return (
    <ContentProvider content={content}>
      <PageClient />
    </ContentProvider>
  );
}
