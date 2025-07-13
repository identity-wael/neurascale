'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef, Suspense } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'
import ScrollIndicator from '@/components/ui/ScrollIndicator'
import dynamic from 'next/dynamic'

// Dynamic import for 3D component to avoid SSR issues
const DataUniverse3D = dynamic(
  () => import('@/components/visuals/DataUniverse3D'),
  { 
    ssr: false,
    loading: () => <div className="absolute inset-0 bg-black/50" />
  }
)

// Simple test for debugging
const SimpleTest3D = dynamic(
  () => import('@/components/visuals/SimpleTest3D'),
  { 
    ssr: false,
    loading: () => <div className="absolute inset-0 bg-red-500/20">Loading 3D...</div>
  }
)

export default function Hero() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end start'],
  })

  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 0.95])
  const y = useTransform(scrollYProgress, [0, 0.5], [0, -50])

  return (
    <section ref={containerRef} className="relative min-h-screen flex flex-col justify-center px-6 md:px-12 lg:px-24 overflow-hidden">
      {/* 3D Data Universe Background */}
      <div className="absolute inset-0 opacity-30" style={{ zIndex: 1 }}>
        <Suspense fallback={<div className="absolute inset-0 bg-red-500/20 flex items-center justify-center text-white">Loading Data Universe...</div>}>
          <DataUniverse3D />
        </Suspense>
      </div>

      <motion.div
        style={{ opacity, scale, y }}
        className="max-w-6xl relative z-10"
      >
        <AnimatedText
          text="Bridging the Mind and the Physical World"
          className="text-5xl md:text-7xl lg:text-8xl font-light mb-8"
          delay={0.5}
          stagger={0.02}
        />
        
        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 1 }}
          className="text-xl md:text-2xl lg:text-3xl font-light leading-relaxed text-white/80 max-w-4xl mb-8"
        >
          An open-source platform designed to process petabytes of real-time neural data, unlocking human potential through seamless brain-computer interaction.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 1.3 }}
          className="text-lg md:text-xl leading-relaxed text-white/70 max-w-5xl"
        >
          <p className="mb-6">
            Over <span className="text-blue-400 font-medium">20 million people worldwide</span> live with paralysis from spinal cord injury and stroke—their minds fully capable but physically separated from the world. 
          </p>
          <p>
            NEURASCALE breaks down these barriers, enabling <span className="text-blue-400 font-medium">restored mobility</span>, <span className="text-blue-400 font-medium">advanced robotics control</span>, and <span className="text-blue-400 font-medium">immersive reality experiences</span> through real-time neural signal processing.
          </p>
        </motion.div>
        
      </motion.div>
      <ScrollIndicator />
    </section>
  )
}