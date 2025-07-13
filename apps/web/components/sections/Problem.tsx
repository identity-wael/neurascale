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


// Roadmap Timeline Component
const RoadmapTimeline = () => {
  const developmentPhases = [
    {
      phase: 'Phase 1',
      title: 'Foundation & Core Research',
      timeline: 'Q1-Q2 2024',
      status: 'Current',
      objectives: [
        'Establish neural signal processing infrastructure',
        'Develop initial AI/ML models for pattern recognition',
        'Create basic brain-computer interface protocols'
      ]
    },
    {
      phase: 'Phase 2',
      title: 'Platform Development',
      timeline: 'Q3-Q4 2024',
      status: 'In Progress',
      objectives: [
        'Complete Neural Management System architecture',
        'Deploy multi-cloud infrastructure',
        'Implement real-time data processing pipeline'
      ]
    },
    {
      phase: 'Phase 3',
      title: 'Feature Expansion',
      timeline: 'Q1-Q2 2025',
      status: 'Planned',
      objectives: [
        'Expand neural interface capabilities',
        'Integrate advanced robotics control',
        'Deploy immersive VR/XR applications'
      ]
    },
    {
      phase: 'Phase 4',
      title: 'Ecosystem Growth',
      timeline: 'Q3 2025+',
      status: 'Future',
      objectives: [
        'Global platform scaling',
        'Open-source community expansion',
        'Consumer market entry'
      ]
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Current':
        return 'text-green-400 bg-green-400/10 border-green-400/20'
      case 'In Progress':
        return 'text-blue-400 bg-blue-400/10 border-blue-400/20'
      case 'Planned':
        return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20'
      case 'Future':
        return 'text-purple-400 bg-purple-400/10 border-purple-400/20'
      default:
        return 'text-white/60 bg-white/5 border-white/10'
    }
  }

  return (
    <div className="mt-16 mb-8">
      <motion.h4
        initial={{ opacity: 0, x: -20 }}
        whileInView={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        viewport={{ once: true }}
        className="text-lg font-light mb-6 text-white/90"
      >
        Development Roadmap
      </motion.h4>
      
      {/* Horizontal Timeline */}
      <div className="relative">
        {/* Timeline line */}
        <motion.div
          initial={{ scaleX: 0 }}
          whileInView={{ scaleX: 1 }}
          transition={{ duration: 1.5, delay: 0.5 }}
          viewport={{ once: true }}
          className="absolute top-8 left-6 right-6 h-0.5 bg-gradient-to-r from-blue-400/20 via-blue-400/60 to-blue-400/20 origin-left"
        />
        
        {/* Timeline cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {developmentPhases.map((phase, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ 
                duration: 0.8, 
                delay: 0.6 + (index * 0.2),
                ease: "easeOut"
              }}
              viewport={{ once: true }}
              className="relative"
            >
              {/* Timeline node */}
              <motion.div
                initial={{ scale: 0 }}
                whileInView={{ scale: 1 }}
                transition={{ 
                  duration: 0.4, 
                  delay: 0.8 + (index * 0.2),
                  type: "spring",
                  stiffness: 200
                }}
                viewport={{ once: true }}
                className="absolute top-6 left-6 w-4 h-4 rounded-full bg-blue-400 border-2 border-blue-400/30 z-10"
              />
              
              {/* Card */}
              <div className="p-4 pt-16 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm hover:bg-white/10 transition-all duration-300">
                <div className="mb-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-blue-400 font-mono text-xs">{phase.phase}</span>
                    <span className={`text-xs px-2 py-1 rounded border ${getStatusColor(phase.status)}`}>
                      {phase.status}
                    </span>
                  </div>
                  <h5 className="text-sm font-light text-white/90 mb-1">{phase.title}</h5>
                  <p className="text-xs text-white/60">{phase.timeline}</p>
                </div>
                
                <ul className="space-y-1">
                  {phase.objectives.map((objective, objIndex) => (
                    <li key={objIndex} className="text-xs text-white/60 flex items-start">
                      <span className="text-blue-400/60 mr-1 mt-0.5">•</span>
                      <span className="leading-relaxed">{objective}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

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
          text="Breakthrough Neural Computing Architecture"
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
            <h3 className="text-2xl font-light mb-6 text-white/90">Unlocking Human Potential Through Advanced Neural Processing</h3>
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

            {/* Roadmap Timeline */}
            <RoadmapTimeline />
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