'use client'

import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'

export default function Compatibility() {
  const { ref, inView } = useInView({
    threshold: 0.3,
    triggerOnce: true,
  })

  return (
    <section ref={ref} className="min-h-screen flex items-center px-6 md:px-12 lg:px-24 py-24">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={inView ? { opacity: 1, scale: 1 } : {}}
        transition={{ duration: 1 }}
        className="max-w-5xl"
      >
        <h2 className="text-3xl md:text-4xl lg:text-5xl font-light mb-12">
          Built on proven technologies, designed for scale
        </h2>
        
        <p className="text-lg md:text-xl text-white/80 mb-8">
          NEURASCALE leverages industry-standard frameworks and cloud-native architecture to ensure seamless integration with existing healthcare and research infrastructure.
        </p>

        <div className="grid md:grid-cols-2 gap-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="p-6 bg-white/5 rounded-xl backdrop-blur-sm"
          >
            <h3 className="text-xl font-medium mb-3">Neural Management System</h3>
            <p className="text-white/70">
              Orchestrates operations between Neural Interaction Layer, Emulation Layer, and Physical Integration Layer using modular monolith architecture.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="p-6 bg-white/5 rounded-xl backdrop-blur-sm"
          >
            <h3 className="text-xl font-medium mb-3">Open Standards</h3>
            <p className="text-white/70">
              Compatible with PyTorch, TensorFlow, and major cloud providers. Supports Lab Streaming Layer (LSL) and industry-standard neural data formats.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="p-6 bg-white/5 rounded-xl backdrop-blur-sm"
          >
            <h3 className="text-xl font-medium mb-3">Extended Reality Engine</h3>
            <p className="text-white/70">
              Full-Dive VR capabilities with Nvidia OmniVerse integration, enabling seamless neural-to-virtual interaction with under 20ns latency.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="p-6 bg-white/5 rounded-xl backdrop-blur-sm"
          >
            <h3 className="text-xl font-medium mb-3">Agentic Applications</h3>
            <p className="text-white/70">
              AI-powered applications that generate actions directly from movement intents and brain states using LLMs and reinforcement learning.
            </p>
          </motion.div>
        </div>
      </motion.div>
    </section>
  )
}