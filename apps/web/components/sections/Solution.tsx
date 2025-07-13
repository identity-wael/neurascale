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
      title: 'Real-Time Movement Decoding',
      description: 'Instantly translates brain signals into commands to control external devices, restoring the direct link between intent and action.',
    },
    {
      title: 'Brain State Analysis',
      description: 'Machine learning identifies conditions like focus, fatigue, or seizures from patterns in neural data for proactive care.',
    },
    {
      title: 'Memory Preservation',
      description: 'Stimulation reinforces memory-related brain signals, restoring memory and fighting cognitive decline.',
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

        <div className="grid md:grid-cols-3 gap-12">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: index * 0.2 }}
              viewport={{ once: true }}
              className="text-left"
            >
              <div className="flex items-start mb-6">
                <span className="text-white/40 text-sm font-mono mr-4">0{index + 1}</span>
                <div className="w-12 h-[1px] bg-white/20 mt-3" />
              </div>
              <h3 className="text-xl font-light mb-4 text-white/90">
                {feature.title}
              </h3>
              <p className="text-white/60 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </section>
  )
}