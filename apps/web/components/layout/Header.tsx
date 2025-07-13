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
          <a className="flex items-center justify-center" href="#">
            <span className="sr-only">NEURASCALE</span>
            <span
              className="font-extrabold text-2xl tracking-wider"
              style={{ fontFamily: 'Proxima Nova, sans-serif' }}
            >
              <span className="text-[#eeeeee]">NEURA</span>
              <span className="text-[#4185f4]">SCALE</span>
            </span>
          </a>
          <div className="w-px h-6 bg-white/20" />
          <span className="text-xs uppercase tracking-wider text-white/60">Neural-Prosthetics Application Cloud</span>
        </div>
        <nav className="flex items-center gap-6">
          <a href="#vision" className="text-sm text-white/70 hover:text-white transition-colors uppercase tracking-wider">Vision</a>
          <a href="#specificity" className="text-sm text-white/70 hover:text-white transition-colors uppercase tracking-wider">Specificity</a>
          <a href="#roadmap" className="text-sm text-white/70 hover:text-white transition-colors uppercase tracking-wider">Roadmap</a>
          <a href="#solution" className="text-sm text-white/70 hover:text-white transition-colors uppercase tracking-wider">Solution</a>
          <a href="#technology" className="text-sm text-white/70 hover:text-white transition-colors uppercase tracking-wider">Technology</a>
          <a href="#community" className="text-sm text-white/70 hover:text-white transition-colors uppercase tracking-wider">Community</a>
          <a href="#resources" className="text-sm text-white/70 hover:text-white transition-colors uppercase tracking-wider">Resources</a>
          <a href="#contact" className="text-sm text-white/70 hover:text-white transition-colors uppercase tracking-wider">Contact</a>
          
          {/* Visual separator */}
          <div className="w-px h-6 bg-white/20" />
          
          {/* GitHub link */}
          <a 
            href="https://github.com/identity-wael/neurascale" 
            target="_blank" 
            rel="noopener noreferrer"
            className="p-2 text-white/70 hover:text-white transition-colors"
            title="Open Source Repository"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 0C5.374 0 0 5.373 0 12 0 17.302 3.438 21.8 8.207 23.387c.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
            </svg>
          </a>
        </nav>
      </div>
    </motion.header>
  )
}