'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'
import dynamic from 'next/dynamic'

const AttractorParticles3D = dynamic(
  () => import('@/components/visuals/AttractorParticles3D'),
  { 
    ssr: false,
    loading: () => <div className="absolute inset-0 bg-black/50" />
  }
)

// AI Unit Icon Component
const AIUnitIcon = () => (
  <svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="20" y="20" width="80" height="80" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.3" />
    <rect x="30" y="30" width="60" height="60" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.5" />
    <rect x="40" y="40" width="40" height="40" fill="currentColor" opacity="0.1" />
    
    {/* Corner elements */}
    <path d="M20 20 L30 20 L30 30" stroke="currentColor" strokeWidth="2" fill="none" />
    <path d="M90 20 L100 20 L100 30" stroke="currentColor" strokeWidth="2" fill="none" />
    <path d="M100 90 L100 100 L90 100" stroke="currentColor" strokeWidth="2" fill="none" />
    <path d="M30 100 L20 100 L20 90" stroke="currentColor" strokeWidth="2" fill="none" />
    
    {/* Center cross */}
    <path d="M50 60 L70 60" stroke="currentColor" strokeWidth="1" opacity="0.8" />
    <path d="M60 50 L60 70" stroke="currentColor" strokeWidth="1" opacity="0.8" />
  </svg>
)

export default function Problem() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'end start'],
  })

  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0])
  const y = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [100, 0, 0, -100])

  return (
    <section ref={containerRef} className="min-h-screen flex items-center px-6 md:px-12 lg:px-24 py-24 relative">
      {/* 3D Attractor Particles Background */}
      <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1/2 h-full opacity-20 hidden lg:block">
        <AttractorParticles3D />
      </div>

      <motion.div
        style={{ opacity, y }}
        className="max-w-5xl relative z-10"
      >
        <div className="flex items-start mb-12">
          <span className="text-white/40 text-sm font-mono mr-4">≡</span>
          <span className="text-white/40 text-sm uppercase tracking-wider">SPECIFICITY</span>
        </div>

        <AnimatedText
          text="Architected to practically deliver 10×–30× reductions in energy consumption"
          className="text-4xl md:text-5xl lg:text-6xl font-light mb-12"
          stagger={0.02}
        />

        <div className="grid md:grid-cols-2 gap-16 items-start">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            viewport={{ once: true }}
          >
            <h3 className="text-2xl font-light mb-6 text-white/90">AI unit</h3>
            <p className="text-lg leading-relaxed text-white/70 mb-6">
              Built on NEURASCALE's proprietary multi-physics computing core, high-volume AI tasks with n³ complexity are accelerated and executed at ultra-low power consumption.
            </p>
            <div className="text-white/40 mt-8">
              <AIUnitIcon />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.7 }}
            viewport={{ once: true }}
            className="space-y-8"
          >
            <div>
              <h4 className="text-lg font-light mb-3 text-white/80">Control unit</h4>
              <p className="text-white/60 text-sm leading-relaxed">
                Its deterministic architecture maximizes memory transfer efficiency and speeds up pointwise operations, achieving optimal performance for tasks with n² complexity.
              </p>
            </div>
            <div className="space-y-3 text-sm">
              <div className="flex items-start">
                <span className="text-white/40 mr-3 font-mono">An</span>
                <span className="text-white/60">Higher computation capacity</span>
              </div>
              <div className="flex items-start">
                <span className="text-white/40 mr-3 font-mono">An</span>
                <span className="text-white/60">Higher throughput</span>
              </div>
              <div className="flex items-start">
                <span className="text-white/40 mr-3 font-mono">An</span>
                <span className="text-white/60">Lower energy consumption</span>
              </div>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </section>
  )
}