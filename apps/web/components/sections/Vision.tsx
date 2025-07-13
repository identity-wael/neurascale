'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'

export default function Vision() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'center center'],
  })

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1])

  return (
    <section ref={containerRef} className="min-h-screen px-6 md:px-12 lg:px-24 py-24 relative">
      <motion.div style={{ scale }} className="relative z-10">
        <div className="flex items-start mb-12">
          <span className="text-white/40 text-sm font-mono mr-4">≡</span>
          <span className="text-white/40 text-sm uppercase tracking-wider">VISION</span>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
          className="max-w-5xl"
        >
          <p className="text-lg md:text-xl leading-relaxed text-white/70 mb-8">
            Over <span className="text-blue-400 font-medium">20 million people worldwide</span> live with paralysis from spinal cord injury and stroke—their minds fully capable but physically separated from the world.
          </p>
          
          <p className="text-lg md:text-xl leading-relaxed text-white/70">
            NEURASCALE breaks down these barriers, enabling <span className="text-blue-400 font-medium">restored mobility</span>, <span className="text-blue-400 font-medium">advanced robotics control</span>, and <span className="text-blue-400 font-medium">immersive reality experiences</span> through real-time neural signal processing.
          </p>
        </motion.div>
      </motion.div>
    </section>
  )
}