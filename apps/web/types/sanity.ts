// Sanity content types

export interface HeroContent {
  title?: string;
  subtitle?: string;
  description?: string;
  cta?: {
    text: string;
    href: string;
  };
  backgroundImage?: {
    url: string;
    alt: string;
  };
}

export interface VisionContent {
  title?: string;
  description?: string;
  sectionHeader?: string;
  solutionTitle?: string;
  solutionPoints?: Array<{
    _key: string;
    highlight: string;
    description: string;
  }>;
  mainStat?: string;
  mainStatDescription?: string;
  stat1Value?: string;
  stat1Label?: string;
  stat2Value?: string;
  stat2Label?: string;
  highlights?: Array<{
    stat: string;
    label: string;
  }>;
  features?: Array<{
    title: string;
    description: string;
    icon?: string;
  }>;
}

export interface ProblemContent {
  title?: string;
  description?: string;
  problems?: Array<{
    title: string;
    description: string;
  }>;
}

export interface RoadmapContent {
  title?: string;
  description?: string;
  milestones?: Array<{
    date: string;
    title: string;
    description: string;
    status?: 'completed' | 'in-progress' | 'planned';
  }>;
}

export interface TeamContent {
  title?: string;
  description?: string;
  members?: Array<{
    name: string;
    role: string;
    bio?: string;
    image?: {
      url: string;
      alt: string;
    };
    social?: {
      twitter?: string;
      linkedin?: string;
      github?: string;
    };
  }>;
}

export interface ResourcesContent {
  title?: string;
  description?: string;
  categories?: Array<{
    name: string;
    resources: Array<{
      title: string;
      description: string;
      link: string;
      type?: 'article' | 'video' | 'documentation' | 'github';
    }>;
  }>;
}

export interface ContactContent {
  title?: string;
  description?: string;
  email?: string;
  phone?: string;
  address?: string;
  social?: {
    twitter?: string;
    linkedin?: string;
    github?: string;
  };
}
