'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'
import dynamic from 'next/dynamic'

// Dynamic import for Architecture Layers to avoid SSR issues
const ArchitectureLayers = dynamic(
  () => import('@/components/visuals/ArchitectureLayers'),
  { 
    ssr: false,
    loading: () => <div className="w-full h-96 bg-black/50 flex items-center justify-center text-white/60">Loading Architecture Layers...</div>
  }
)

export default function Architecture() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'end start'],
  })

  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0])
  const y = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [100, 0, 0, -100])

  return (
    <section id="architecture" ref={containerRef} className="px-6 py-16 relative">
      <motion.div
        style={{ opacity, y }}
        className="relative z-10 w-full"
      >
        <div className="flex items-start mb-8">
          <span className="text-white/40 text-sm font-mono mr-4">≡</span>
          <span className="text-white/40 text-sm uppercase tracking-wider">ARCHITECTURE</span>
        </div>

        <AnimatedText
          text="Technology Stack"
          className="text-4xl md:text-5xl lg:text-6xl font-light mb-6"
          stagger={0.02}
        />

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          viewport={{ once: true }}
          className="mb-12"
        >
          <p className="text-white/70 text-lg max-w-4xl mb-8">
            Explore the multi-layered architecture that powers NEURASCALE. Our modular monolith design 
            ensures scalability, maintainability, and seamless integration across all neural interface technologies.
          </p>
          
          <div className="grid md:grid-cols-2 gap-8 mb-12">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
              viewport={{ once: true }}
              className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6"
            >
              <h3 className="text-xl font-light text-white/90 mb-4">Modular Architecture</h3>
              <p className="text-white/70 leading-relaxed mb-4">
                The Neural Management System orchestrates operations and communication between different modules 
                including the Neural Interaction & Immersion Layer (NIIL), Physical Integration & Control Layer (PICL), 
                and AI Domain Agnostic Models (ADAM).
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-cyan-500/20 text-cyan-300 rounded-full text-sm">NIIL</span>
                <span className="px-3 py-1 bg-green-500/20 text-green-300 rounded-full text-sm">PICL</span>
                <span className="px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full text-sm">ADAM</span>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              viewport={{ once: true }}
              className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-6"
            >
              <h3 className="text-xl font-light text-white/90 mb-4">Technology Foundation</h3>
              <p className="text-white/70 leading-relaxed mb-4">
                Built on a foundation of cutting-edge technologies including generative AI, machine learning, 
                and multi-cloud infrastructure. Our application layer abstracts underlying technologies while 
                reusing existing open standards and technology whenever possible.
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-orange-500/20 text-orange-300 rounded-full text-sm">GenAI</span>
                <span className="px-3 py-1 bg-yellow-500/20 text-yellow-300 rounded-full text-sm">ML</span>
                <span className="px-3 py-1 bg-indigo-500/20 text-indigo-300 rounded-full text-sm">Multi-Cloud</span>
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* Interactive Architecture Layers */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.7 }}
          viewport={{ once: true }}
          className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg overflow-hidden"
        >
          <div className="p-6 border-b border-white/10">
            <h3 className="text-2xl font-light text-white/90 mb-2">Interactive Layer Explorer</h3>
            <p className="text-white/60">
              Navigate through each architectural layer to discover the technologies and components that power our neural interface platform.
            </p>
          </div>
          
          <div className="h-[600px]">
            <ArchitectureLayers />
          </div>
        </motion.div>

        {/* Key Benefits */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.9 }}
          viewport={{ once: true }}
          className="mt-16 grid md:grid-cols-3 gap-6"
        >
          <div className="text-center">
            <div className="w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h4 className="text-lg font-light text-white/90 mb-2">High Performance</h4>
            <p className="text-white/60 text-sm">Optimized for real-time neural signal processing with minimal latency</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
            </div>
            <h4 className="text-lg font-light text-white/90 mb-2">Modular Design</h4>
            <p className="text-white/60 text-sm">Flexible architecture enabling rapid development and deployment</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h4 className="text-lg font-light text-white/90 mb-2">Enterprise Security</h4>
            <p className="text-white/60 text-sm">Medical-grade security and compliance for sensitive neural data</p>
          </div>
        </motion.div>
      </motion.div>
    </section>
  )
}