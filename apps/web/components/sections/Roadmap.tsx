'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'
import dynamic from 'next/dynamic'

// Dynamic import for DSM Periodic Table to avoid SSR issues
const DSMPeriodicTable = dynamic(
  () => import('@/components/visuals/DSMPeriodicTable'),
  { 
    ssr: false,
    loading: () => <div className="w-full h-96 bg-black/50 flex items-center justify-center text-white/60">Loading DSM Periodic Table...</div>
  }
)

export default function Roadmap() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'end start'],
  })

  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0])
  const y = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [100, 0, 0, -100])

  return (
    <section id="roadmap" ref={containerRef} className="px-6 md:px-12 lg:px-24 py-8 relative">
      <motion.div
        style={{ opacity, y }}
        className="max-w-5xl relative z-10 w-full"
      >
        <div className="flex items-start mb-6">
          <span className="text-white/40 text-sm font-mono mr-4">≡</span>
          <span className="text-white/40 text-sm uppercase tracking-wider">ROADMAP</span>
        </div>

        <AnimatedText
          text="Development Timeline"
          className="text-4xl md:text-5xl lg:text-6xl font-light mb-6"
          stagger={0.02}
        />

        {/* Full Width Roadmap Timeline */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          viewport={{ once: true }}
        >
          {/* Timeline line */}
          <motion.div
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            transition={{ duration: 1.5, delay: 0.5 }}
            viewport={{ once: true }}
            className="relative h-0.5 bg-gradient-to-r from-blue-400/20 via-blue-400/60 to-blue-400/20 mb-4 origin-left"
          />
          
          {/* Timeline cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                phase: 'Phase 1',
                title: 'Foundation & Core Research',
                timeline: 'Q1-Q2 2025',
                status: 'Current',
                color: 'border-green-400/20 bg-green-400/5'
              },
              {
                phase: 'Phase 2', 
                title: 'Platform Development',
                timeline: 'Q3-Q4 2025',
                status: 'In Progress',
                color: 'border-blue-400/20 bg-blue-400/5'
              },
              {
                phase: 'Phase 3',
                title: 'Feature Expansion', 
                timeline: 'Q1-Q2 2026',
                status: 'Planned',
                color: 'border-yellow-400/20 bg-yellow-400/5'
              },
              {
                phase: 'Phase 4',
                title: 'Ecosystem Growth',
                timeline: 'Q3 2026+',
                status: 'Future', 
                color: 'border-purple-400/20 bg-purple-400/5'
              }
            ].map((phase, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ 
                  duration: 0.6, 
                  delay: 0.7 + (index * 0.1)
                }}
                viewport={{ once: true }}
                className={`p-4 rounded-lg border ${phase.color} backdrop-blur-sm`}
              >
                <div className="text-center">
                  <span className="text-blue-400 font-mono text-xs">{phase.phase}</span>
                  <h5 className="text-sm font-light text-white/90 mt-1 mb-2">{phase.title}</h5>
                  <p className="text-xs text-white/60 mb-2">{phase.timeline}</p>
                  <span className="text-xs px-2 py-1 rounded bg-white/10 text-white/70">
                    {phase.status}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
        
        {/* DSM Periodic Table */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.5 }}
          viewport={{ once: true }}
          className="mt-16"
        >
          <div className="mb-8">
            <h3 className="text-2xl md:text-3xl font-light text-white/90 mb-4">
              DSM Technology Stack
            </h3>
            <p className="text-white/70 max-w-3xl">
              Explore our comprehensive technology ecosystem through an interactive periodic table. 
              Each element represents a core component of the NEURASCALE platform, from neural interfaces 
              to cloud infrastructure and AI frameworks.
            </p>
          </div>
          <div className="h-96 rounded-lg overflow-hidden border border-white/10">
            <DSMPeriodicTable />
          </div>
        </motion.div>
      </motion.div>
    </section>
  )
}