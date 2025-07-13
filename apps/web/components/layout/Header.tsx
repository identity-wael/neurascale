'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

export default function Header() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className={`fixed top-0 left-0 right-0 z-50 px-6 md:px-12 lg:px-24 py-6 transition-all ${
        scrolled ? 'backdrop-blur-md bg-black/50' : ''
      }`}
    >
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-light tracking-widest">NEURASCALE</h1>
          <div className="w-px h-6 bg-white/20" />
          <span className="text-xs uppercase tracking-wider text-white/60">Neural-Prosthetics Application Cloud</span>
        </div>
        <nav className="flex items-center gap-8">
          <a href="#" className="text-sm text-white/70 hover:text-white transition-colors uppercase tracking-wider">Contact</a>
          <button className="p-2 hover:opacity-70 transition-opacity">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 12H21" stroke="currentColor" strokeWidth="1" />
              <path d="M3 6H21" stroke="currentColor" strokeWidth="1" />
              <path d="M3 18H21" stroke="currentColor" strokeWidth="1" />
            </svg>
          </button>
        </nav>
      </div>
    </motion.header>
  )
}