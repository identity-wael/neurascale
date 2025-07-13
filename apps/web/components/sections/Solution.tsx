'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'

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
      icon: '🦾',
      details: 'Dramatically improves quality of life through direct neural control of mobility devices.'
    },
    {
      title: 'Advanced Robotic Control',
      description: 'Sophisticated, intuitive control over advanced robotics including prosthetic limbs, industrial robots, and drone swarms through direct brain-to-machine communication.',
      icon: '🤖',
      details: 'Precision control with unprecedented speed and accuracy for complex robotic systems.'
    },
    {
      title: 'Immersive Realities',
      description: '"Full-Dive" virtual reality experiences seamlessly integrated with neural intent, allowing direct thought-based interaction within virtual environments.',
      icon: '🥽',
      details: 'Revolutionary VR/XR/AR applications for entertainment, training, and therapeutic use.'
    },
    {
      title: 'Neural Identity Security',
      description: 'Passwordless "Neural ID" authentication using unique brain data patterns for enhanced security and convenience across all digital platforms.',
      icon: '🧠',
      details: 'Unbreakable biometric security that cannot be stolen, forgotten, or replicated.'
    },
    {
      title: 'Brain State Analysis',
      description: 'Real-time identification of cognitive conditions like focus, fatigue, seizures, and emotional states from neural patterns for proactive care.',
      icon: '📊',
      details: 'Advanced ML models enable predictive healthcare and cognitive enhancement.'
    },
    {
      title: 'Memory Preservation',
      description: 'Neural stimulation reinforces memory-related brain signals, restoring memory function and fighting cognitive decline through targeted interventions.',
      icon: '💭',
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
                <span className="text-3xl mr-3">{feature.icon}</span>
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