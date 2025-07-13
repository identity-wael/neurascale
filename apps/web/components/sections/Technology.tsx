'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'

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
      icon: '🧠',
      tech: 'Modular Monolith Architecture'
    },
    {
      title: 'Neural Interaction & Immersion Layer (NIIL)',
      description: 'Direct interface for neural signal acquisition and real-time processing, providing the foundation for brain-computer communication.',
      icon: '🔗',
      tech: 'Real-time Signal Processing'
    },
    {
      title: 'Emulation Layer',
      description: 'Translates neural patterns into actionable commands across diverse platforms and devices with minimal latency.',
      icon: '⚡',
      tech: 'Pattern Recognition & Encoding'
    },
    {
      title: 'Physical Integration & Control Layer (PICL)',
      description: 'Manages direct control of external devices, robotics, and prosthetics through precise command execution.',
      icon: '🤖',
      tech: 'Device Control & Feedback'
    },
    {
      title: 'AI Domain Agnostic Models (ADAM)',
      description: 'Advanced machine learning models that interpret neural patterns across multiple domains and applications.',
      icon: '🧮',
      tech: 'Multi-Domain AI/ML'
    }
  ]

  const keyTechnologies = [
    'NVIDIA Holoscan',
    'DGX Cloud',
    'AI Enterprise Stack', 
    'AWS IoT (GreenGrass, Core, Device Management)',
    'AWS FleetWise & RoboRunner',
    'NVIDIA ROS',
    'Multi-Cloud Architecture'
  ]

  return (
    <section ref={containerRef} className="min-h-screen px-6 md:px-12 lg:px-24 py-24 relative">
      <motion.div style={{ scale }} className="relative z-10">
        <AnimatedText
          text="Technology that powers human potential"
          className="text-3xl md:text-4xl lg:text-5xl font-light mb-16 max-w-4xl"
        />
        
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
                  <span className="text-2xl mr-3">{component.icon}</span>
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

        {/* Data Processing Flow */}
        <div className="mb-20">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            Real-Time Data Processing
          </motion.h3>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { step: '01', title: 'Signal Acquisition', desc: 'Capture neural signals at 492Mb/s' },
              { step: '02', title: 'Pattern Recognition', desc: 'AI models decode intentions' },
              { step: '03', title: 'Action Encoding', desc: 'Transform to device commands' },
              { step: '04', title: 'Execution', desc: 'Real-time device control' }
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.15 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="w-16 h-16 mx-auto mb-4 rounded-full border-2 border-blue-400/60 flex items-center justify-center">
                  <span className="text-blue-400 font-mono text-sm">{item.step}</span>
                </div>
                <h4 className="text-lg font-light text-white/90 mb-2">{item.title}</h4>
                <p className="text-white/60 text-sm">{item.desc}</p>
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

        {/* Key Technologies */}
        <div className="mb-16">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            Technology Stack
          </motion.h3>
          
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="flex flex-wrap gap-3"
          >
            {keyTechnologies.map((tech, index) => (
              <span
                key={index}
                className="px-4 py-2 rounded-full border border-white/20 text-white/70 text-sm bg-white/5 backdrop-blur-sm"
              >
                {tech}
              </span>
            ))}
          </motion.div>
        </div>

        {/* Open Source Commitment */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="p-8 rounded-lg border border-blue-400/30 bg-blue-400/5 backdrop-blur-sm"
        >
          <h3 className="text-xl font-light text-white/90 mb-4">Open-Source Foundation</h3>
          <p className="text-white/70 leading-relaxed">
            Built on open standards and collaborative development principles, NEURASCALE ensures transparency, 
            innovation, and community-driven advancement in neural interface technology. Our multi-cloud approach 
            provides scalability and flexibility while maintaining compatibility across diverse hardware and software ecosystems.
          </p>
        </motion.div>
      </motion.div>
    </section>
  )
}