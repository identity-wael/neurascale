// This script outlines the changes needed for each component to use Sanity content

const componentUpdates = {
  Vision: {
    imports: `import { useContent } from '@/src/contexts/ContentContext';`,
    hookUsage: `const { vision } = useContent();`,
    contentMapping: {
      sectionHeader: `vision?.sectionHeader || 'VISION'`,
      title: `vision?.title || 'Bridging minds and reality'`,
      mainStat: `vision?.mainStat || '20M'`,
      mainStatDescription: `vision?.mainStatDescription || 'people worldwide live with paralysis from spinal cord injury and stroke—their minds fully capable but physically separated from the world.'`,
      stat1Value: `vision?.stat1Value || '5.4M'`,
      stat1Label: `vision?.stat1Label || 'New injuries annually'`,
      stat2Value: `vision?.stat2Value || '100%'`,
      stat2Label: `vision?.stat2Label || 'Mental capacity intact'`,
      solutionTitle: `vision?.solutionTitle || 'NEURASCALE breaks down these barriers'`,
      solutionPoints: `vision?.solutionPoints || []`,
      solutionDescription: `vision?.solutionDescription || 'Through real-time neural signal processing at unprecedented scale and precision'`,
    },
  },

  Problem: {
    imports: `import { useContent } from '@/src/contexts/ContentContext';`,
    hookUsage: `const { problem } = useContent();`,
    contentMapping: {
      sectionHeader: `problem?.sectionHeader || 'SPECIFICITY'`,
      title: `problem?.title || 'Breakthrough Neural Computing Architecture'`,
      subtitle: `problem?.subtitle || 'Unlocking Human Potential Through Advanced Neural Processing'`,
      description: `problem?.description || ''`,
      coreArchitecture: `problem?.coreArchitecture || {}`,
      processingSpecs: `problem?.processingSpecs || {}`,
      computingPower: `problem?.computingPower || []`,
      aimlIntegration: `problem?.aimlIntegration || []`,
      neuralIdentity: `problem?.neuralIdentity || {}`,
      openSourceFeatures: `problem?.openSourceFeatures || []`,
    },
  },

  Roadmap: {
    imports: `import { useContent } from '@/src/contexts/ContentContext';`,
    hookUsage: `const { roadmap } = useContent();`,
    contentMapping: {
      sectionTitle: `roadmap?.sectionTitle || 'Development Timeline'`,
      timelinePhases: `roadmap?.timelinePhases || []`,
      technologyStack: `roadmap?.technologyStack || {}`,
    },
  },

  Team: {
    imports: `import { useContent } from '@/src/contexts/ContentContext';`,
    hookUsage: `const { team } = useContent();`,
    contentMapping: {
      sectionTitle: `team?.sectionTitle || 'Meet the Team'`,
      introduction: `team?.introduction || ''`,
      teamMembers: `team?.teamMembers || []`,
      missionStatement: `team?.missionStatement || {}`,
    },
  },

  Resources: {
    imports: `import { useContent } from '@/src/contexts/ContentContext';`,
    hookUsage: `const { resources } = useContent();`,
    contentMapping: {
      sectionTitle: `resources?.sectionTitle || 'Knowledge hub for neural interface innovation'`,
      introduction: `resources?.introduction || ''`,
      documentationSections: `resources?.documentationSections || []`,
      researchPapers: `resources?.researchPapers || []`,
      externalReferences: `resources?.externalReferences || []`,
    },
  },

  Contact: {
    imports: `import { useContent } from '@/src/contexts/ContentContext';`,
    hookUsage: `const { contact } = useContent();`,
    contentMapping: {
      sectionTitle: `contact?.sectionTitle || 'Let\\'s Connect'`,
      introduction: `contact?.introduction || ''`,
      contactChannels: `contact?.contactChannels || []`,
      formSubjects: `contact?.formSubjects || []`,
      officeLocation: `contact?.officeLocation || {}`,
    },
  },
};

console.log('Component update mappings generated. Apply these changes to each component file.');
export default componentUpdates;
