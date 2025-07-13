'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef, Suspense } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'
import ScrollIndicator from '@/components/ui/ScrollIndicator'
import dynamic from 'next/dynamic'

// Dynamic import for 3D component to avoid SSR issues
const NeuralProcessor3D = dynamic(
  () => import('@/components/visuals/NeuralProcessor3D'),
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
      {/* 3D Neural Processor Background */}
      <div className="absolute inset-0 opacity-30" style={{ zIndex: 1 }}>
        <Suspense fallback={<div className="absolute inset-0 bg-red-500/20 flex items-center justify-center text-white">Loading Neural Processor...</div>}>
          <NeuralProcessor3D />
        </Suspense>
      </div>

      <motion.div
        style={{ opacity, scale, y }}
        className="max-w-6xl relative z-10"
      >
        <AnimatedText
          text="Neural-Prosthetics Application Cloud"
          className="text-5xl md:text-7xl lg:text-8xl font-light mb-8"
          delay={0.5}
          stagger={0.02}
        />
        
        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 1 }}
          className="text-xl md:text-2xl lg:text-3xl font-light leading-relaxed text-white/80 max-w-4xl"
        >
          An open-source project designed to process petabytes of complex brain data, blurring the boundaries between the human mind and the real world.
        </motion.p>
        
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1.5 }}
          className="text-lg md:text-xl mt-8 text-white/60"
        >
          Enabling communication at the speed of thought through real-time neural signal processing and agentic applications.
        </motion.p>
      </motion.div>
      <ScrollIndicator />
    </section>
  )
}