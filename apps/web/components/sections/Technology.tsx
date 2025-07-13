'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'

// SVG Icons for technology components
const NeuralIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 20 C12 12, 20 8, 28 12 C32 14, 32 18, 30 22 C28 26, 24 28, 20 26 C16 24, 12 22, 12 20 Z" 
          stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <circle cx="18" cy="18" r="1" fill="currentColor" />
    <circle cx="24" cy="16" r="1" fill="currentColor" />
    <circle cx="22" cy="22" r="1" fill="currentColor" />
    <path d="M15 22 Q18 24 21 22" stroke="currentColor" strokeWidth="0.5" fill="none" opacity="0.6" />
  </svg>
)

const NetworkIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="20" cy="20" r="12" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <circle cx="20" cy="20" r="8" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <circle cx="20" cy="20" r="4" fill="currentColor" opacity="0.8" />
    <path d="M8 20 L32 20" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
    <path d="M20 8 L20 32" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
  </svg>
)

const ProcessingIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M10 15 L15 20 L10 25" stroke="currentColor" strokeWidth="1.5" fill="none" opacity="0.8" />
    <path d="M30 15 L25 20 L30 25" stroke="currentColor" strokeWidth="1.5" fill="none" opacity="0.8" />
    <circle cx="20" cy="20" r="3" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <path d="M15 8 L25 8" stroke="currentColor" strokeWidth="2" opacity="0.6" />
    <path d="M15 32 L25 32" stroke="currentColor" strokeWidth="2" opacity="0.6" />
  </svg>
)

const IntegrationIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="8" y="12" width="24" height="16" rx="2" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <circle cx="12" cy="16" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="16" cy="16" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="20" cy="16" r="1.5" fill="currentColor" opacity="0.8" />
    <path d="M10 20 L30 20" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
    <path d="M10 24 L30 24" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
  </svg>
)

const AIIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="6" y="8" width="28" height="20" rx="2" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <path d="M10 24 L14 20 L18 22 L22 16 L26 18 L30 14" stroke="currentColor" strokeWidth="1.5" fill="none" opacity="0.8" />
    <circle cx="14" cy="20" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="18" cy="22" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="22" cy="16" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="26" cy="18" r="1.5" fill="currentColor" opacity="0.8" />
    <path d="M10 32 L30 32" stroke="currentColor" strokeWidth="1" opacity="0.4" />
  </svg>
)

export default function Technology() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'center center'],
  })

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1])

  const architectureComponents = [
    {
      title: 'Neural Management System',
      description: 'Orchestrates operations and communication between all key modules, ensuring seamless data flow and system coordination.',
      icon: <NeuralIcon />,
      tech: 'Modular Monolith Architecture'
    },
    {
      title: 'Neural Interaction & Immersion Layer (NIIL)',
      description: 'Direct interface for neural signal acquisition and real-time processing, providing the foundation for brain-computer communication.',
      icon: <NetworkIcon />,
      tech: 'Real-time Signal Processing'
    },
    {
      title: 'Emulation Layer',
      description: 'Translates neural patterns into actionable commands across diverse platforms and devices with minimal latency.',
      icon: <ProcessingIcon />,
      tech: 'Pattern Recognition & Encoding'
    },
    {
      title: 'Physical Integration & Control Layer (PICL)',
      description: 'Manages direct control of external devices, robotics, and prosthetics through precise command execution.',
      icon: <IntegrationIcon />,
      tech: 'Device Control & Feedback'
    },
    {
      title: 'AI Domain Agnostic Models (ADAM)',
      description: 'Advanced machine learning models that interpret neural patterns across multiple domains and applications.',
      icon: <AIIcon />,
      tech: 'Multi-Domain AI/ML'
    }
  ]


  return (
    <section id="technology" ref={containerRef} className="min-h-screen px-6 md:px-12 lg:px-24 py-24 relative">
      <motion.div style={{ scale }} className="relative z-10">
        
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
          className="text-lg md:text-xl text-white/80 mb-16 max-w-4xl"
        >
          Our neural processing architecture handles petabytes of real-time data through advanced AI models, 
          enabling instantaneous translation of brain signals into meaningful actions across the physical and digital worlds.
        </motion.p>

        {/* Architectural Overview */}
        <div className="mb-20">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            Core Architecture
          </motion.h3>
          
          <div className="grid lg:grid-cols-2 xl:grid-cols-3 gap-8">
            {architectureComponents.map((component, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
              >
                <div className="flex items-center mb-4">
                  <div className="text-white/60 mr-3">{component.icon}</div>
                  <h4 className="text-lg font-light text-white/90">
                    {component.title}
                  </h4>
                </div>
                
                <p className="text-white/70 leading-relaxed mb-4">
                  {component.description}
                </p>
                
                <span className="text-blue-400/80 text-sm font-mono">
                  {component.tech}
                </span>
              </motion.div>
            ))}
          </div>
        </div>


        {/* Performance Metrics */}
        <div className="mb-20">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="grid md:grid-cols-3 gap-8 p-8 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
          >
            <div className="text-center">
              <div className="text-3xl font-light text-blue-400 mb-2">492Mb/s</div>
              <div className="text-white/60">Neural Data Processing</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-light text-blue-400 mb-2">100T ops/sec</div>
              <div className="text-white/60">Computational Throughput</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-light text-blue-400 mb-2">&lt;1ms</div>
              <div className="text-white/60">Signal-to-Action Latency</div>
            </div>
          </motion.div>
        </div>

      </motion.div>
    </section>
  )
}