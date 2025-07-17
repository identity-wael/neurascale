export interface HeroContent {
  _id: string;
  _type: 'hero';
  title: string;
  subtitle: string;
  ctaText: string;
  ctaLink: string;
}

export interface VisionContent {
  _id: string;
  _type: 'vision';
  sectionHeader: string;
  title: string;
  mainStat: string;
  mainStatDescription: string;
  stat1Value: string;
  stat1Label: string;
  stat2Value: string;
  stat2Label: string;
  solutionTitle: string;
  solutionPoints: Array<{
    _key: string;
    text: string;
    highlight: string;
  }>;
  solutionDescription: string;
}

export interface ProblemContent {
  _id: string;
  _type: 'problem';
  sectionHeader: string;
  title: string;
  subtitle: string;
  description: string;
  coreArchitecture: {
    title: string;
    description: string;
    layers: Array<{
      _key: string;
      name: string;
      description: string;
    }>;
  };
  processingSpecs: {
    title: string;
    specs: Array<{
      _key: string;
      label: string;
      value: string;
    }>;
  };
  computingPower: Array<{
    _key: string;
    spec: string;
    description: string;
  }>;
  aimlIntegration: string[];
  neuralIdentity: {
    title: string;
    description: string;
  };
  openSourceFeatures: string[];
}

export interface RoadmapPhase {
  _key: string;
  phase: string;
  title: string;
  timeline: string;
  status: 'Current' | 'In Progress' | 'Planned' | 'Future';
  colorClass: string;
  features: string[];
}

export interface RoadmapContent {
  _id: string;
  _type: 'roadmap';
  sectionTitle: string;
  timelinePhases: RoadmapPhase[];
  technologyStack: {
    title: string;
    description: string;
  };
}

export interface TeamMember {
  _key: string;
  name: string;
  role: string;
  company?: string;
  expertise?: string;
  bio: string;
}

export interface TeamContent {
  _id: string;
  _type: 'team';
  sectionTitle: string;
  introduction: string;
  teamMembers: TeamMember[];
  missionStatement: {
    title: string;
    content: string;
  };
}

export interface ResourcesContent {
  _id: string;
  _type: 'resources';
  sectionTitle: string;
  introduction: string;
  documentationSections: Array<{
    _key: string;
    title: string;
    description: string;
    iconType: 'rocket' | 'book' | 'code' | 'users';
    resources: string[];
  }>;
  researchPapers: Array<{
    _key: string;
    title: string;
    authors: string;
    summary: string;
    category?: string;
    pages?: string;
    date?: string;
    url?: string;
  }>;
  externalReferences: Array<{
    _key: string;
    title: string;
    description: string;
    url: string;
    displayUrl?: string;
    category?: string;
  }>;
}

export interface ContactContent {
  _id: string;
  _type: 'contact';
  sectionTitle: string;
  introduction: string;
  contactChannels: Array<{
    _key: string;
    title: string;
    email: string;
    description: string;
    iconType?: 'chat' | 'code' | 'academic' | 'document';
    responseTime?: string;
  }>;
  formSubjects: Array<{
    _key: string;
    value: string;
    label: string;
  }>;
  officeLocation: {
    city: string;
    address: string;
    focus: string;
    coordinates: {
      lat: number;
      lng: number;
    };
  };
}
