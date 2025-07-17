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
  token: process.env.SANITY_API_TOKEN,
  useCdn: false,
});

// All website content
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

  problem: {
    _type: 'problem',
    sectionHeader: 'SPECIFICITY',
    title: 'Breakthrough Neural Computing Architecture',
    subtitle: 'Unlocking Human Potential Through Advanced Neural Processing',
    description:
      "NeuraScale's Neural-Prosthetics Application Cloud represents a paradigm shift in brain-computer interface technology, designed to process petabytes of real-time neural data and bridge the gap between the human mind and the physical world.",
    coreArchitecture: {
      title: 'Core Architecture: Modular Monolith Design',
      description:
        'Built on our proprietary Modular Monolith Architecture, the system ensures stable, scalable development with controlled dependencies. At its heart, the Neural Management System (NMS) orchestrates all operations across specialized layers:',
      layers: [
        {
          _key: 'layer1',
          name: 'NIIL',
          description: 'Managing neural interfaces and mixed reality environments',
        },
        {
          _key: 'layer2',
          name: 'PICL',
          description: 'Controlling robotic systems and IoT devices',
        },
        {
          _key: 'layer3',
          name: 'ADAM',
          description: 'Housing our advanced AI/ML models for real-time processing',
        },
      ],
    },
    processingSpecs: {
      title: 'Ultra-High-Speed Neural Data Processing',
      specs: [
        {
          _key: 'spec1',
          label: 'Raw neural data acquisition',
          value: '492Mb/s',
        },
        {
          _key: 'spec2',
          label: 'Per-channel sampling',
          value: '30kS/s',
        },
        {
          _key: 'spec3',
          label: 'ADC resolution',
          value: '16-bit',
        },
        {
          _key: 'spec4',
          label: 'Wireless transmission',
          value: '48Mb/s',
        },
      ],
    },
    computingPower: [
      {
        _key: 'compute1',
        spec: '640-core TPU',
        description: 'Neural signal processing',
      },
      {
        _key: 'compute2',
        spec: '14,592-core GPU',
        description: 'Parallel computation',
      },
      {
        _key: 'compute3',
        spec: '100 trillion ops/sec',
        description: '3nm Neural Engine',
      },
      {
        _key: 'compute4',
        spec: '10×–30× reduction',
        description: 'Energy consumption',
      },
    ],
    aimlIntegration: [
      'Movement Intention Classifiers (RNN/LSTM)',
      'Seizure Prediction Models (CNN/LSTM)',
      'Large Language Models for agentic applications',
      'Adaptive Learning Agents',
    ],
    neuralIdentity: {
      title: 'Secure Neural Identity',
      description:
        'Revolutionary passwordless Neural ID - authentication derived from your unique neural patterns, providing secure access to robotic prosthetics, virtual environments, and agentic applications.',
    },
    openSourceFeatures: [
      'Tokenized reward system for contributions',
      'Multi-cloud deployment options',
      'Hardware-accelerated simulation engine',
    ],
  },

  roadmap: {
    _type: 'roadmap',
    sectionTitle: 'Development Timeline',
    timelinePhases: [
      {
        _key: 'phase1',
        phase: 'Phase 1',
        title: 'Foundation & Core Research',
        timeline: 'Q1-Q2 2025',
        status: 'Current',
        colorClass: 'border-green-400/20 bg-green-400/5',
        features: [
          'Complete neural data acquisition systems testing',
          'Finalize real-time processing algorithms',
          'Establish baseline performance metrics',
          'Initial prototype demonstrations',
        ],
      },
      {
        _key: 'phase2',
        phase: 'Phase 2',
        title: 'Platform Development',
        timeline: 'Q3-Q4 2025',
        status: 'In Progress',
        colorClass: 'border-blue-400/20 bg-blue-400/5',
        features: [
          'Launch beta version of Neural Management System',
          'Integrate AI/ML models for movement prediction',
          'Deploy initial cloud infrastructure',
          'Begin closed beta testing with research partners',
        ],
      },
      {
        _key: 'phase3',
        phase: 'Phase 3',
        title: 'Feature Expansion',
        timeline: 'Q1-Q2 2026',
        status: 'Planned',
        colorClass: 'border-purple-400/20 bg-purple-400/5',
        features: [
          'Release SDK for third-party developers',
          'Implement advanced neural pattern recognition',
          'Expand robotic control capabilities',
          'Launch developer community platform',
        ],
      },
      {
        _key: 'phase4',
        phase: 'Phase 4',
        title: 'Ecosystem Growth',
        timeline: 'Q3 2026+',
        status: 'Future',
        colorClass: 'border-orange-400/20 bg-orange-400/5',
        features: [
          'Full commercial deployment',
          'Global research network integration',
          'Advanced VR/AR neural interfaces',
          'Next-generation hardware rollout',
        ],
      },
    ],
    technologyStack: {
      title: 'DSM Technology Stack',
      description:
        'Explore our comprehensive technology ecosystem through an interactive periodic table and dependency matrix. Each element represents a core component of the NEURASCALE platform, from neural interfaces to cloud infrastructure and AI frameworks.',
    },
  },

  team: {
    _type: 'team',
    sectionTitle: 'Meet the Team',
    introduction:
      "Our multidisciplinary team brings together decades of experience in brain-computer interfaces, artificial intelligence, cloud computing, and data systems. United by a shared vision to revolutionize human potential, we're building the future of neural interface technology.",
    teamMembers: [
      {
        _key: 'member1',
        name: 'Wael El Ghazzawi',
        role: 'CTO, Financial Technology',
        company: 'Brain Finance',
        expertise: 'ML/AI',
        bio: 'Visionary technologist specializing in machine learning and artificial intelligence applications in financial systems.',
      },
      {
        _key: 'member2',
        name: 'Alex Elghazawi',
        role: 'Engineering Manager',
        company: 'Microsoft',
        expertise: 'Cloud Architecture',
        bio: 'Leading engineering teams at Microsoft with deep expertise in scalable cloud infrastructure and distributed systems.',
      },
      {
        _key: 'member3',
        name: 'Lina El-Ghazzawi',
        role: 'Wellness Lead',
        company: 'Wellness Focus',
        expertise: 'User Experience',
        bio: 'Passionate about human-centered design and the intersection of technology and wellbeing. Ensuring our technologies enhance quality of life.',
      },
      {
        _key: 'member4',
        name: 'Azizah Javed',
        role: 'Research Scientist',
        company: 'NVIDIA',
        expertise: 'Computer Vision',
        bio: 'Advancing the frontiers of computer vision and neural processing at NVIDIA, bringing cutting-edge GPU acceleration to brain-computer interfaces.',
      },
      {
        _key: 'member5',
        name: 'Nicholas Kurzawa',
        role: 'Data Architect',
        company: 'Data Systems Expert',
        expertise: 'Big Data',
        bio: 'Architecting systems that handle petabyte-scale neural data with real-time processing capabilities and robust security.',
      },
    ],
    missionStatement: {
      title: 'Our Mission',
      content:
        'We are united by a shared vision to revolutionize human potential through advanced neural interfaces. Our team combines deep technical expertise with a commitment to ethical development, ensuring that brain-computer interface technology enhances human capabilities while respecting individual autonomy and privacy.',
    },
  },

  resources: {
    _type: 'resources',
    sectionTitle: 'Knowledge hub for neural interface innovation',
    introduction:
      'Access comprehensive documentation, research papers, tutorials, and community resources to accelerate your journey in neural interface development.',
    documentationSections: [
      {
        _key: 'doc1',
        title: 'Getting Started',
        description:
          'Quick setup guides, installation instructions, and your first neural interface project',
        iconType: 'rocket',
        resources: [
          'Quick Start Guide',
          'Installation Manual',
          'First Project Tutorial',
          'System Requirements',
        ],
      },
      {
        _key: 'doc2',
        title: 'Technical Documentation',
        description: 'In-depth technical references, API documentation, and architecture guides',
        iconType: 'book',
        resources: [
          'API Reference',
          'Architecture Overview',
          'Neural Signal Processing',
          'Cloud Infrastructure',
        ],
      },
      {
        _key: 'doc3',
        title: 'Developer Resources',
        description: 'SDKs, code examples, best practices, and integration guides',
        iconType: 'code',
        resources: ['SDK Documentation', 'Code Examples', 'Integration Guides', 'Best Practices'],
      },
      {
        _key: 'doc4',
        title: 'Community',
        description: 'Join our community, contribute to the project, and get support',
        iconType: 'users',
        resources: ['Discord Server', 'GitHub Repository', 'Contributing Guide', 'Community Forum'],
      },
    ],
    researchPapers: [
      {
        _key: 'paper1',
        title: 'Demonstration of a portable intracortical brain-computer interface',
        authors: 'J.D. Collinger, R.A. Gaunt, J.E. Downey, D.J. Weber, M.L. Boninger',
        summary:
          'Development and testing of a self-contained, wireless BCI system enabling real-time neural control in naturalistic settings.',
        category: 'BCI / Computing',
        pages: '16 pages',
        date: '2019',
        url: 'https://www.researchgate.net/publication/337089099',
      },
      {
        _key: 'paper2',
        title: 'A brain-computer interface for control of mediated reality',
        authors: 'D.H. Robinson, C.K. Lee, M.J. Anderson, P.R. Martinez',
        summary:
          'Novel approaches to integrating BCIs with augmented and virtual reality systems for enhanced human-computer interaction.',
        category: 'XR / Interface',
        pages: '22 pages',
        date: '2021',
        url: 'https://www.researchgate.net/publication/349812345',
      },
      // Add more papers as needed...
    ],
    externalReferences: [
      {
        _key: 'ref1',
        title: 'NVIDIA Holoscan Platform',
        description:
          'High-performance computing platform for AI applications at the edge, optimized for real-time processing.',
        url: 'https://developer.nvidia.com/holoscan-sdk',
        displayUrl: 'developer.nvidia.com/holoscan-sdk',
        category: 'Platform',
      },
      {
        _key: 'ref2',
        title: 'AWS Neuron SDK',
        description:
          'Deep learning inference and training SDK for AWS Inferentia and Trainium chips.',
        url: 'https://awsdocs-neuron.readthedocs-hosted.com/',
        displayUrl: 'awsdocs-neuron.readthedocs-hosted.com',
        category: 'ML/AI',
      },
      {
        _key: 'ref3',
        title: 'OpenBCI Documentation',
        description:
          'Open-source brain-computer interface technologies for research and education.',
        url: 'https://docs.openbci.com/',
        displayUrl: 'docs.openbci.com',
        category: 'Hardware',
      },
      {
        _key: 'ref4',
        title: 'MNE-Python',
        description:
          'Open-source Python software for exploring, visualizing, and analyzing human neurophysiological data.',
        url: 'https://mne.tools/stable/index.html',
        displayUrl: 'mne.tools',
        category: 'Software',
      },
    ],
  },

  contact: {
    _type: 'contact',
    sectionTitle: "Let's Connect",
    introduction:
      'Ready to explore neural interface technology? Get in touch for partnerships, demos, research collaboration, or technical support.',
    contactChannels: [
      {
        _key: 'channel1',
        title: 'General Inquiries',
        email: 'hello@neurascale.io',
        description:
          'Questions about NEURASCALE, partnership opportunities, or general information',
        iconType: 'chat',
        responseTime: '24-48 hours',
      },
      {
        _key: 'channel2',
        title: 'Technical Support',
        email: 'support@neurascale.io',
        description: 'Technical assistance, bug reports, or implementation questions',
        iconType: 'code',
        responseTime: '12-24 hours',
      },
      {
        _key: 'channel3',
        title: 'Research Collaboration',
        email: 'research@neurascale.io',
        description: 'Academic partnerships, research proposals, or data sharing requests',
        iconType: 'academic',
        responseTime: '3-5 business days',
      },
      {
        _key: 'channel4',
        title: 'Media & Press',
        email: 'press@neurascale.io',
        description: 'Press inquiries, media kits, or interview requests',
        iconType: 'document',
        responseTime: '24 hours',
      },
    ],
    formSubjects: [
      { _key: 'subject1', value: 'general', label: 'General Inquiry' },
      { _key: 'subject2', value: 'partnership', label: 'Partnership Opportunity' },
      { _key: 'subject3', value: 'demo', label: 'Request a Demo' },
      { _key: 'subject4', value: 'research', label: 'Research Collaboration' },
      { _key: 'subject5', value: 'support', label: 'Technical Support' },
      { _key: 'subject6', value: 'press', label: 'Media Inquiry' },
    ],
    officeLocation: {
      city: 'Boston',
      address: 'MIT Campus\nCambridge, MA 02139',
      focus: 'Research & Development',
      coordinates: {
        lat: 42.3601,
        lng: -71.0942,
      },
    },
  },
};

async function migrateContent() {
  console.log('Starting comprehensive content migration to Sanity...');
  console.log('Using token:', process.env.SANITY_API_TOKEN ? 'Token found' : 'No token found');

  try {
    // Test permissions first
    console.log('\nTesting API permissions...');
    const testQuery = await client.fetch('*[_type == "hero"][0]');
    console.log('✅ Read permission confirmed');

    // Migrate Hero content
    console.log('\nMigrating Hero content...');
    const heroResult = await client.createOrReplace({
      _id: 'hero-main',
      ...websiteContent.hero,
    });
    console.log('✅ Hero content created/updated:', heroResult._id);

    // Migrate Vision content
    console.log('\nMigrating Vision content...');
    const visionResult = await client.createOrReplace({
      _id: 'vision-main',
      ...websiteContent.vision,
    });
    console.log('✅ Vision content created/updated:', visionResult._id);

    // Migrate Problem content
    console.log('\nMigrating Problem content...');
    const problemResult = await client.createOrReplace({
      _id: 'problem-main',
      ...websiteContent.problem,
    });
    console.log('✅ Problem content created/updated:', problemResult._id);

    // Migrate Roadmap content
    console.log('\nMigrating Roadmap content...');
    const roadmapResult = await client.createOrReplace({
      _id: 'roadmap-main',
      ...websiteContent.roadmap,
    });
    console.log('✅ Roadmap content created/updated:', roadmapResult._id);

    // Migrate Team content
    console.log('\nMigrating Team content...');
    const teamResult = await client.createOrReplace({
      _id: 'team-main',
      ...websiteContent.team,
    });
    console.log('✅ Team content created/updated:', teamResult._id);

    // Migrate Resources content
    console.log('\nMigrating Resources content...');
    const resourcesResult = await client.createOrReplace({
      _id: 'resources-main',
      ...websiteContent.resources,
    });
    console.log('✅ Resources content created/updated:', resourcesResult._id);

    // Migrate Contact content
    console.log('\nMigrating Contact content...');
    const contactResult = await client.createOrReplace({
      _id: 'contact-main',
      ...websiteContent.contact,
    });
    console.log('✅ Contact content created/updated:', contactResult._id);

    console.log('\n🎉 All content migration completed successfully!');
    console.log('\nNext steps:');
    console.log('1. Visit http://localhost:3000/studio');
    console.log('2. You should see all sections populated with content');
    console.log('3. Update your Next.js pages to fetch content from Sanity');
    console.log('4. Consider adding image assets and additional content types');
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

// Run the migration
console.log('NeuraScale Content Migration Tool');
console.log('=================================');
migrateContent();
