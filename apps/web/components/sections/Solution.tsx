'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'


export default function Solution() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'center center'],
  })

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1])


  return (
    <section id="solution" ref={containerRef} className="min-h-screen px-6 md:px-12 lg:px-24 py-24 relative">
      <motion.div style={{ scale }} className="relative z-10">
        
      </motion.div>
    </section>
  )
}