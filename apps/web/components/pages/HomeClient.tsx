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

// TODO: Import Sanity-enabled components when they are created

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
            {/* TODO: Use Sanity content when components are ready */}
            <Hero />
            <Vision />
            <Problem />
            <Roadmap />
            <Team />
            <Resources />
            <Contact />
          </main>
          <Footer />
        </SmoothScroll>
      )}
    </>
  );
}
