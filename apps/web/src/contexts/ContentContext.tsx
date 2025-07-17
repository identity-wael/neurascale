'use client';

import React, { createContext, useContext } from 'react';
import type {
  HeroContent,
  VisionContent,
  ProblemContent,
  RoadmapContent,
  TeamContent,
  ResourcesContent,
  ContactContent,
} from '@/types/sanity';

interface ContentContextType {
  hero: HeroContent | null;
  vision: VisionContent | null;
  problem: ProblemContent | null;
  roadmap: RoadmapContent | null;
  team: TeamContent | null;
  resources: ResourcesContent | null;
  contact: ContactContent | null;
}

const ContentContext = createContext<ContentContextType>({
  hero: null,
  vision: null,
  problem: null,
  roadmap: null,
  team: null,
  resources: null,
  contact: null,
});

export function ContentProvider({
  children,
  content,
}: {
  children: React.ReactNode;
  content: ContentContextType;
}) {
  return <ContentContext.Provider value={content}>{children}</ContentContext.Provider>;
}

export function useContent() {
  return useContext(ContentContext);
}
