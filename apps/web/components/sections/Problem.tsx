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



export default function Problem() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'end start'],
  })

  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0])
  const y = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [100, 0, 0, -100])

  return (
    <section id="specificity" ref={containerRef} className="min-h-screen flex items-center px-4 sm:px-6 md:px-12 lg:px-24 py-12 md:py-20 lg:py-24 relative">
      {/* 3D Attractor Particles Background */}
      <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1/2 h-full opacity-20 hidden lg:block">
        <AttractorParticles3D />
      </div>

      <motion.div
        style={{ opacity, y }}
        className="max-w-5xl relative z-10"
      >
        <div className="flex items-start mb-6 md:mb-8 lg:mb-12">
          <span className="text-white/40 text-sm font-mono mr-4">≡</span>
          <span className="text-white/40 text-sm uppercase tracking-wider">SPECIFICITY</span>
        </div>

        <AnimatedText
          text="Breakthrough Neural Computing Architecture"
          className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-light mb-6 md:mb-8 lg:mb-12"
          stagger={0.02}
        />

        <div className="grid md:grid-cols-2 gap-8 md:gap-12 lg:gap-16 items-start">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            viewport={{ once: true }}
          >
            <h3 className="text-xl sm:text-2xl font-light mb-4 md:mb-6 text-white/90">Unlocking Human Potential Through Advanced Neural Processing</h3>
            <p className="text-lg leading-relaxed text-white/70 mb-8">
              NeuraScale's Neural-Prosthetics Application Cloud represents a paradigm shift in brain-computer interface technology, designed to process petabytes of real-time neural data and bridge the gap between the human mind and the physical world.
            </p>

            <div className="space-y-6">
              <div>
                <h4 className="text-lg font-light mb-3 text-blue-400">Core Architecture: Modular Monolith Design</h4>
                <p className="text-white/60 text-sm leading-relaxed mb-4">
                  Built on our proprietary Modular Monolith Architecture, the system ensures stable, scalable development with controlled dependencies. At its heart, the Neural Management System (NMS) orchestrates all operations across specialized layers:
                </p>
                <div className="space-y-2 text-sm pl-4">
                  <div className="flex items-start">
                    <span className="text-blue-400 mr-3">•</span>
                    <span className="text-white/70"><strong>NIIL:</strong> Managing neural interfaces and mixed reality environments</span>
                  </div>
                  <div className="flex items-start">
                    <span className="text-blue-400 mr-3">•</span>
                    <span className="text-white/70"><strong>PICL:</strong> Controlling robotic systems and IoT devices</span>
                  </div>
                  <div className="flex items-start">
                    <span className="text-blue-400 mr-3">•</span>
                    <span className="text-white/70"><strong>ADAM:</strong> Housing our advanced AI/ML models for real-time processing</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-lg font-light mb-3 text-blue-400">Ultra-High-Speed Neural Data Processing</h4>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-white/60">Raw neural data acquisition:</span>
                    <span className="text-blue-400 font-mono">492Mb/s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/60">Per-channel sampling:</span>
                    <span className="text-blue-400 font-mono">30kS/s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/60">ADC resolution:</span>
                    <span className="text-blue-400 font-mono">16-bit</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/60">Wireless transmission:</span>
                    <span className="text-blue-400 font-mono">48Mb/s</span>
                  </div>
                </div>
              </div>
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
              <h4 className="text-lg font-light mb-4 text-white/90">Next-Generation Computing Power</h4>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between items-center p-3 rounded border border-white/10 bg-white/5">
                  <span className="text-white/70">640-core TPU</span>
                  <span className="text-blue-400">Neural signal processing</span>
                </div>
                <div className="flex justify-between items-center p-3 rounded border border-white/10 bg-white/5">
                  <span className="text-white/70">14,592-core GPU</span>
                  <span className="text-blue-400">Parallel computation</span>
                </div>
                <div className="flex justify-between items-center p-3 rounded border border-white/10 bg-white/5">
                  <span className="text-white/70">100 trillion ops/sec</span>
                  <span className="text-blue-400">3nm Neural Engine</span>
                </div>
                <div className="flex justify-between items-center p-3 rounded border border-blue-400/20 bg-blue-400/5">
                  <span className="text-white/70">10×–30× reduction</span>
                  <span className="text-blue-400">Energy consumption</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-lg font-light mb-3 text-white/90">Advanced AI/ML Integration</h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-start">
                  <span className="text-white/40 mr-3">•</span>
                  <span className="text-white/70">Movement Intention Classifiers (RNN/LSTM)</span>
                </div>
                <div className="flex items-start">
                  <span className="text-white/40 mr-3">•</span>
                  <span className="text-white/70">Seizure Prediction Models (CNN/LSTM)</span>
                </div>
                <div className="flex items-start">
                  <span className="text-white/40 mr-3">•</span>
                  <span className="text-white/70">Large Language Models for agentic applications</span>
                </div>
                <div className="flex items-start">
                  <span className="text-white/40 mr-3">•</span>
                  <span className="text-white/70">Adaptive Learning Agents</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-lg font-light mb-3 text-white/90">Secure Neural Identity</h4>
              <p className="text-white/60 text-sm leading-relaxed mb-3">
                Revolutionary passwordless Neural ID - authentication derived from your unique neural patterns, providing secure access to robotic prosthetics, virtual environments, and agentic applications.
              </p>
            </div>

            <div>
              <h4 className="text-lg font-light mb-3 text-white/90">Open-Source Innovation</h4>
              <div className="space-y-2 text-sm">
                <div className="flex items-start">
                  <span className="text-white/40 mr-3">•</span>
                  <span className="text-white/70">Tokenized reward system for contributions</span>
                </div>
                <div className="flex items-start">
                  <span className="text-white/40 mr-3">•</span>
                  <span className="text-white/70">Multi-cloud deployment options</span>
                </div>
                <div className="flex items-start">
                  <span className="text-white/40 mr-3">•</span>
                  <span className="text-white/70">Hardware-accelerated simulation engine</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

      </motion.div>

    </section>
  )
}