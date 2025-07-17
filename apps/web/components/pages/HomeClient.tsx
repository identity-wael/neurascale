'use client';

import { useState, useEffect } from 'react';
import Hero from '@/components/sections/Hero';
import Vision from '@/components/sections/Vision';
import Problem from '@/components/sections/Problem';
import Roadmap from '@/components/sections/Roadmap';
import Team from '@/components/sections/Team';
import Resources from '@/components/sections/Resources';
import Contact from '@/components/sections/Contact';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import LoadingScreen from '@/components/ui/LoadingScreen';
import SmoothScroll from '@/components/layout/SmoothScroll';
import { AnimatePresence } from 'framer-motion';

// Import new Sanity-enabled components
import HeroWithContent from '@/components/sections/HeroWithContent';
import VisionWithContent from '@/components/sections/VisionWithContent';
import ProblemWithContent from '@/components/sections/ProblemWithContent';
import RoadmapWithContent from '@/components/sections/RoadmapWithContent';
import TeamWithContent from '@/components/sections/TeamWithContent';
import ResourcesWithContent from '@/components/sections/ResourcesWithContent';
import ContactWithContent from '@/components/sections/ContactWithContent';

interface HomeClientProps {
  content: {
    hero: any;
    vision: any;
    problem: any;
    roadmap: any;
    team: any;
    resources: any;
    contact: any;
  };
}

export default function HomeClient({ content }: HomeClientProps) {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setLoading(false);
    }, 3000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <>
      <AnimatePresence mode="wait">{loading && <LoadingScreen key="loading" />}</AnimatePresence>

      {!loading && (
        <SmoothScroll>
          <Header />
          <main className="bg-black text-white relative">
            {content.hero ? <HeroWithContent content={content.hero} /> : <Hero />}
            {content.vision ? <VisionWithContent content={content.vision} /> : <Vision />}
            {content.problem ? <ProblemWithContent content={content.problem} /> : <Problem />}
            {content.roadmap ? <RoadmapWithContent content={content.roadmap} /> : <Roadmap />}
            {content.team ? <TeamWithContent content={content.team} /> : <Team />}
            {content.resources ? (
              <ResourcesWithContent content={content.resources} />
            ) : (
              <Resources />
            )}
            {content.contact ? <ContactWithContent content={content.contact} /> : <Contact />}
          </main>
          <Footer />
        </SmoothScroll>
      )}
    </>
  );
}
