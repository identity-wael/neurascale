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
      <div className="grid lg:grid-cols-3 gap-12 w-full max-w-7xl mx-auto">
        {/* Main Content - Left Side */}
        <motion.div
          style={{ opacity, y }}
          className="lg:col-span-2 relative z-10"
        >
        <div className="flex items-start mb-12">
          <span className="text-white/40 text-sm font-mono mr-4">≡</span>
          <span className="text-white/40 text-sm uppercase tracking-wider">SPECIFICITY</span>
        </div>

        <AnimatedText
          text="Breakthrough Neural Computing Architecture"
          className="text-4xl md:text-5xl lg:text-6xl font-light mb-8"
          stagger={0.02}
        />
        
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          viewport={{ once: true }}
          className="text-xl text-white/70 mb-16 max-w-4xl"
        >
          NEURASCALE's next-generation platform delivers unprecedented performance for brain-computer interface applications through revolutionary hardware design.
        </motion.p>

        {/* Core Processing Power */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          viewport={{ once: true }}
          className="mb-12"
        >
          <h3 className="text-2xl font-light mb-6 text-white/90">Core Processing Power</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-4 rounded-lg border border-white/10 bg-white/5">
              <div className="text-2xl font-light text-blue-400 mb-2">640-core</div>
              <p className="text-white/60 text-sm">TPU optimized for neural signal processing</p>
            </div>
            <div className="p-4 rounded-lg border border-white/10 bg-white/5">
              <div className="text-2xl font-light text-blue-400 mb-2">14592-core</div>
              <p className="text-white/60 text-sm">GPU for parallel computation tasks</p>
            </div>
            <div className="p-4 rounded-lg border border-white/10 bg-white/5">
              <div className="text-2xl font-light text-blue-400 mb-2">100 trillion</div>
              <p className="text-white/60 text-sm">operations per second neural engine capability</p>
            </div>
          </div>
        </motion.div>

        {/* Ultra-High-Speed Data Handling */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          viewport={{ once: true }}
          className="mb-12"
        >
          <h3 className="text-2xl font-light mb-6 text-white/90">Ultra-High-Speed Data Handling</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 rounded-lg border border-white/10 bg-white/5 text-center">
              <div className="text-xl font-light text-purple-400 mb-1">492Mb/s</div>
              <p className="text-white/60 text-xs">raw neural data acquisition</p>
            </div>
            <div className="p-4 rounded-lg border border-white/10 bg-white/5 text-center">
              <div className="text-xl font-light text-purple-400 mb-1">48Mb/s</div>
              <p className="text-white/60 text-xs">wireless transmission</p>
            </div>
            <div className="p-4 rounded-lg border border-white/10 bg-white/5 text-center">
              <div className="text-xl font-light text-purple-400 mb-1">30kS/s</div>
              <p className="text-white/60 text-xs">per-channel sampling rate</p>
            </div>
            <div className="p-4 rounded-lg border border-white/10 bg-white/5 text-center">
              <div className="text-xl font-light text-purple-400 mb-1">16-bit</div>
              <p className="text-white/60 text-xs">ADC resolution</p>
            </div>
          </div>
        </motion.div>

        {/* Advanced System Architecture */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          viewport={{ once: true }}
          className="mb-12"
        >
          <h3 className="text-2xl font-light mb-8 text-white/90">Advanced System Architecture</h3>
          <div className="space-y-6">
            <div className="p-6 rounded-lg border border-blue-400/20 bg-blue-400/5">
              <h4 className="text-lg font-medium text-blue-400 mb-3">AI Processing Unit</h4>
              <p className="text-white/70 leading-relaxed">
                Leveraging NEURASCALE's proprietary multi-physics computing core, our AI unit accelerates complex neural decoding tasks while achieving 10×–30× reduction in power consumption compared to traditional architectures.
              </p>
            </div>
            <div className="p-6 rounded-lg border border-white/20 bg-white/5">
              <h4 className="text-lg font-medium text-white/90 mb-3">Deterministic Control Unit</h4>
              <p className="text-white/70 leading-relaxed">
                Purpose-built for real-time neural applications, maximizing memory bandwidth efficiency and accelerating critical signal processing operations.
              </p>
            </div>
            <div className="p-6 rounded-lg border border-white/20 bg-white/5">
              <h4 className="text-lg font-medium text-white/90 mb-3">Extended Reality™ Engine</h4>
              <p className="text-white/70 leading-relaxed">
                Seamlessly integrates with both ADK-P and ADK-XR development platforms, enabling immersive neural interface applications.
              </p>
            </div>
          </div>
        </motion.div>

        {/* Third-Generation 3nm Technology */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.7 }}
          viewport={{ once: true }}
          className="mb-12"
        >
          <h3 className="text-2xl font-light mb-6 text-white/90">Third-Generation 3nm Technology</h3>
          <div className="p-6 rounded-lg border border-green-400/20 bg-green-400/5 mb-6">
            <p className="text-white/70 mb-4">Built on cutting-edge 3nm fabrication process, delivering:</p>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 rounded-full bg-green-400"></div>
                <span className="text-white/80">Higher computational density</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 rounded-full bg-green-400"></div>
                <span className="text-white/80">Superior energy efficiency</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 rounded-full bg-green-400"></div>
                <span className="text-white/80">Enhanced thermal management</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 rounded-full bg-green-400"></div>
                <span className="text-white/80">Compact form factor suitable for wearable and implantable devices</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Complete Development Ecosystem */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          viewport={{ once: true }}
        >
          <h3 className="text-2xl font-light mb-6 text-white/90">Complete Development Ecosystem</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="p-4 rounded-lg border border-white/10 bg-white/5">
              <h4 className="text-white/90 font-medium mb-2">Hardware-accelerated simulation</h4>
              <p className="text-white/60 text-sm">Rapid prototyping engine</p>
            </div>
            <div className="p-4 rounded-lg border border-white/10 bg-white/5">
              <h4 className="text-white/90 font-medium mb-2">Neural Implant ADK</h4>
              <p className="text-white/60 text-sm">A2A support included</p>
            </div>
            <div className="p-4 rounded-lg border border-white/10 bg-white/5">
              <h4 className="text-white/90 font-medium mb-2">API Gateway</h4>
              <p className="text-white/60 text-sm">Agentic applications ready</p>
            </div>
            <div className="p-4 rounded-lg border border-white/10 bg-white/5">
              <h4 className="text-white/90 font-medium mb-2">Neural Ledger</h4>
              <p className="text-white/60 text-sm">Secure data management</p>
            </div>
            <div className="p-4 rounded-lg border border-white/10 bg-white/5">
              <h4 className="text-white/90 font-medium mb-2">Event-driven Architecture</h4>
              <p className="text-white/60 text-sm">Up to 76 targets per minute</p>
            </div>
            <div className="p-4 rounded-lg border border-white/10 bg-white/5">
              <h4 className="text-white/90 font-medium mb-2">Real-time Processing</h4>
              <p className="text-white/60 text-sm">Ultra-low latency execution</p>
            </div>
          </div>
        </motion.div>
        </motion.div>

        {/* Right Side - SVG Icon and Animation */}
        <motion.div
          style={{ opacity, y }}
          className="lg:col-span-1 flex flex-col items-center justify-center space-y-8 relative z-10"
        >
          {/* AI Unit SVG Icon */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.5 }}
            viewport={{ once: true }}
            className="text-white/40"
          >
            <AIUnitIcon />
          </motion.div>

          {/* 3D Attractor Particles Animation */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.7 }}
            viewport={{ once: true }}
            className="w-full h-96 opacity-60"
          >
            <AttractorParticles3D />
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}