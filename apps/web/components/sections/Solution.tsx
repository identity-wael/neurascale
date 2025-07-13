'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'

// SVG Icons matching the professional style
const MobilityIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M15 8 C18 8, 20 10, 20 13 C20 16, 18 18, 15 18" stroke="currentColor" strokeWidth="1.5" fill="none" opacity="0.8" />
    <path d="M15 18 L15 25" stroke="currentColor" strokeWidth="2" opacity="0.8" />
    <path d="M12 25 L18 25" stroke="currentColor" strokeWidth="2" opacity="0.8" />
    <path d="M15 25 L15 32" stroke="currentColor" strokeWidth="2" opacity="0.8" />
    <circle cx="25" cy="15" r="3" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <path d="M25 18 L25 25" stroke="currentColor" strokeWidth="1.5" opacity="0.6" />
    <path d="M22 25 L28 25" stroke="currentColor" strokeWidth="1.5" opacity="0.6" />
  </svg>
)

const RoboticsIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="12" y="12" width="16" height="12" rx="2" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <circle cx="16" cy="16" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="24" cy="16" r="1.5" fill="currentColor" opacity="0.8" />
    <path d="M16 20 L24 20" stroke="currentColor" strokeWidth="1" opacity="0.6" />
    <path d="M20 8 L20 12" stroke="currentColor" strokeWidth="2" opacity="0.6" />
    <path d="M8 18 L12 18" stroke="currentColor" strokeWidth="1.5" opacity="0.6" />
    <path d="M28 18 L32 18" stroke="currentColor" strokeWidth="1.5" opacity="0.6" />
    <path d="M15 24 L15 28" stroke="currentColor" strokeWidth="1.5" opacity="0.6" />
    <path d="M25 24 L25 28" stroke="currentColor" strokeWidth="1.5" opacity="0.6" />
  </svg>
)

const VRIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="8" y="14" width="24" height="12" rx="6" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <circle cx="15" cy="20" r="3" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <circle cx="25" cy="20" r="3" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <path d="M6 20 L8 20" stroke="currentColor" strokeWidth="2" opacity="0.6" />
    <path d="M32 20 L34 20" stroke="currentColor" strokeWidth="2" opacity="0.6" />
    <path d="M20 12 L20 14" stroke="currentColor" strokeWidth="1" opacity="0.4" />
    <circle cx="15" cy="20" r="1" fill="currentColor" opacity="0.8" />
    <circle cx="25" cy="20" r="1" fill="currentColor" opacity="0.8" />
  </svg>
)

const SecurityIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 6 L28 10 L28 20 C28 26, 24 30, 20 32 C16 30, 12 26, 12 20 L12 10 Z" 
          stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <circle cx="20" cy="18" r="3" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <rect x="18" y="20" width="4" height="6" rx="1" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
  </svg>
)

const AnalysisIcon = () => (
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

const MemoryIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 20 C12 12, 20 8, 28 12 C32 14, 32 18, 30 22 C28 26, 24 28, 20 26 C16 24, 12 22, 12 20 Z" 
          stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <circle cx="18" cy="18" r="1" fill="currentColor" />
    <circle cx="24" cy="16" r="1" fill="currentColor" />
    <circle cx="22" cy="22" r="1" fill="currentColor" />
    <path d="M15 22 Q18 24 21 22" stroke="currentColor" strokeWidth="0.5" fill="none" opacity="0.6" />
    <path d="M16 12 Q20 10 24 12" stroke="currentColor" strokeWidth="0.5" fill="none" opacity="0.4" />
  </svg>
)

export default function Solution() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'center center'],
  })

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1])

  const features = [
    {
      title: 'Restored Mobility',
      description: 'Translates brain signals into commands for external devices, enabling individuals with paralysis to regain control over prosthetic limbs, exoskeletons, and assistive technologies.',
      icon: <MobilityIcon />,
      details: 'Dramatically improves quality of life through direct neural control of mobility devices.'
    },
    {
      title: 'Advanced Robotic Control',
      description: 'Sophisticated, intuitive control over advanced robotics including prosthetic limbs, industrial robots, and drone swarms through direct brain-to-machine communication.',
      icon: <RoboticsIcon />,
      details: 'Precision control with unprecedented speed and accuracy for complex robotic systems.'
    },
    {
      title: 'Immersive Realities',
      description: '"Full-Dive" virtual reality experiences seamlessly integrated with neural intent, allowing direct thought-based interaction within virtual environments.',
      icon: <VRIcon />,
      details: 'Revolutionary VR/XR/AR applications for entertainment, training, and therapeutic use.'
    },
    {
      title: 'Neural Identity Security',
      description: 'Passwordless "Neural ID" authentication using unique brain data patterns for enhanced security and convenience across all digital platforms.',
      icon: <SecurityIcon />,
      details: 'Unbreakable biometric security that cannot be stolen, forgotten, or replicated.'
    },
    {
      title: 'Brain State Analysis',
      description: 'Real-time identification of cognitive conditions like focus, fatigue, seizures, and emotional states from neural patterns for proactive care.',
      icon: <AnalysisIcon />,
      details: 'Advanced ML models enable predictive healthcare and cognitive enhancement.'
    },
    {
      title: 'Memory Preservation',
      description: 'Neural stimulation reinforces memory-related brain signals, restoring memory function and fighting cognitive decline through targeted interventions.',
      icon: <MemoryIcon />,
      details: 'Breakthrough treatments for Alzheimer\'s, dementia, and age-related memory loss.'
    },
  ]

  return (
    <section ref={containerRef} className="min-h-screen px-6 md:px-12 lg:px-24 py-24 relative">
      <motion.div style={{ scale }} className="relative z-10">
        {/* Infographic Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
          className="mb-20 flex justify-center"
        >
          <div className="w-full max-w-6xl relative">
            <img 
              src="/infograph.svg" 
              alt="NEURASCALE Neural-Prosthetics Application Cloud Infographic" 
              className="w-full h-auto"
            />
            {/* Transparent overlay to prevent SVG interaction */}
            <div className="absolute inset-0 bg-transparent pointer-events-none" />
          </div>
        </motion.div>

        <AnimatedText
          text="Core capabilities that unlock human potential"
          className="text-3xl md:text-4xl lg:text-5xl font-light mb-16 max-w-4xl"
        />
        
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
          className="text-lg md:text-xl text-white/80 mb-16 max-w-3xl"
        >
          NEURASCALE processes up to 492Mb/s of raw neural data through advanced AI models running on 640-core TPUs and 14592-core GPUs, achieving 100 trillion ops/sec.
        </motion.p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 lg:gap-12">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="text-left group"
            >
              <div className="flex items-start mb-6">
                <span className="text-white/40 text-sm font-mono mr-4">0{index + 1}</span>
                <div className="w-12 h-[1px] bg-white/20 mt-3" />
              </div>
              
              <div className="flex items-center mb-4">
                <div className="text-white/60 mr-3">{feature.icon}</div>
                <h3 className="text-xl font-light text-white/90">
                  {feature.title}
                </h3>
              </div>
              
              <p className="text-white/60 leading-relaxed mb-4">
                {feature.description}
              </p>
              
              <p className="text-blue-400/80 text-sm leading-relaxed">
                {feature.details}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </section>
  )
}