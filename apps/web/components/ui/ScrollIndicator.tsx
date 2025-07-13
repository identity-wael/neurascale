'use client'

import { motion } from 'framer-motion'

export default function ScrollIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 2, duration: 0.8 }}
      className="absolute bottom-12 left-1/2 -translate-x-1/2"
    >
      <motion.p
        animate={{ opacity: [0.4, 1, 0.4] }}
        transition={{ repeat: Infinity, duration: 2 }}
        className="text-white/60 text-sm mb-4 text-center"
      >
        Scroll to discover
      </motion.p>
      <motion.div
        animate={{ y: [0, 8, 0] }}
        transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }}
        className="w-6 h-10 border border-white/30 rounded-full mx-auto flex items-start justify-center p-2 hover:border-white/50 transition-colors"
      >
        <motion.div 
          animate={{ height: ["20%", "40%", "20%"] }}
          transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }}
          className="w-1 bg-white/60 rounded-full" 
        />
      </motion.div>
    </motion.div>
  )
}