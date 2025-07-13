'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'


export default function Technology() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'center center'],
  })

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1])



  return (
    <section id="technology" ref={containerRef} className="px-6 md:px-12 lg:px-24 py-8 relative">
      <motion.div style={{ scale }} className="relative z-10">
        


      </motion.div>
    </section>
  )
}