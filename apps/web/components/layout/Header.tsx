'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (mobileMenuOpen && !(e.target as HTMLElement).closest('.mobile-menu')) {
        setMobileMenuOpen(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [mobileMenuOpen]);

  const menuItems = [
    { label: 'Vision', href: '#vision' },
    { label: 'Specificity', href: '#specificity' },
    { label: 'Roadmap', href: '#roadmap' },
    { label: 'Team', href: '#team' },
    { label: 'Resources', href: '#resources' },
    { label: 'Contact', href: '#contact' },
  ];

  return (
    <>
      <motion.header
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className={`fixed top-0 left-0 right-0 z-50 px-4 sm:px-6 md:px-12 lg:px-24 py-4 sm:py-6 transition-all ${
          scrolled ? 'backdrop-blur-md bg-black/50' : ''
        }`}
      >
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2 sm:gap-4">
            <a className="flex items-center justify-center" href="#">
              <span className="sr-only">NEURASCALE</span>
              <span
                className="font-extrabold text-xl sm:text-2xl tracking-wider"
                style={{ fontFamily: 'Proxima Nova, sans-serif' }}
              >
                <span className="text-[#eeeeee]">NEURA</span>
                <span className="text-[#4185f4]">SCALE</span>
              </span>
            </a>
            <div className="hidden sm:block w-px h-6 bg-white/20" />
            <div className="hidden md:flex items-center gap-2 lg:gap-4">
              {/* MIT Logo */}
              <svg
                className="h-6 lg:h-8 w-auto"
                viewBox="0 0 536.229 536.229"
                fill="white"
                fillOpacity="0.8"
                xmlns="http://www.w3.org/2000/svg"
              >
                <g>
                  <g>
                    <rect y="130.031" width="58.206" height="276.168" />
                    <rect x="95.356" y="130.031" width="58.206" height="190.712" />
                    <rect x="190.712" y="130.031" width="58.206" height="276.168" />
                    <rect x="381.425" y="217.956" width="58.212" height="188.236" />
                    <rect x="381.425" y="130.031" width="154.805" height="58.206" />
                    <rect x="286.074" y="217.956" width="58.2" height="188.236" />
                    <rect x="286.074" y="130.031" width="58.2" height="58.206" />
                  </g>
                </g>
              </svg>
              {/* MIT Text - hidden on smaller screens */}
              <span
                className="hidden lg:block text-sm text-white/70"
                style={{
                  fontFamily:
                    'Neue Haas Grotesk Medium, -apple-system, BlinkMacSystemFont, sans-serif',
                  fontWeight: 500,
                }}
              >
                Massachusetts Institute of Technology
              </span>
              <span
                className="lg:hidden text-xs text-white/70"
                style={{
                  fontFamily:
                    'Neue Haas Grotesk Medium, -apple-system, BlinkMacSystemFont, sans-serif',
                  fontWeight: 500,
                }}
              >
                MIT
              </span>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center gap-6">
            {menuItems.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="text-sm text-white/70 hover:text-white transition-colors uppercase tracking-wider"
              >
                {item.label}
              </a>
            ))}

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
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="currentColor"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path d="M12 0C5.374 0 0 5.373 0 12 0 17.302 3.438 21.8 8.207 23.387c.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z" />
              </svg>
            </a>
          </nav>

          {/* Mobile Menu Button */}
          <button
            className="lg:hidden mobile-menu p-2 text-white/70 hover:text-white transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              setMobileMenuOpen(!mobileMenuOpen);
            }}
            aria-label="Toggle menu"
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              {mobileMenuOpen ? (
                <path d="M6 18L18 6M6 6l12 12" />
              ) : (
                <>
                  <path d="M3 12h18" />
                  <path d="M3 6h18" />
                  <path d="M3 18h18" />
                </>
              )}
            </svg>
          </button>
        </div>
      </motion.header>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
            className="mobile-menu fixed top-[60px] sm:top-[72px] left-0 right-0 z-40 bg-black/95 backdrop-blur-md border-t border-white/10 lg:hidden"
          >
            <nav className="flex flex-col py-4">
              {menuItems.map((item, index) => (
                <motion.a
                  key={item.href}
                  href={item.href}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="px-6 py-3 text-white/70 hover:text-white hover:bg-white/5 transition-colors uppercase tracking-wider text-sm"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.label}
                </motion.a>
              ))}

              {/* GitHub link in mobile menu */}
              <motion.a
                href="https://github.com/identity-wael/neurascale"
                target="_blank"
                rel="noopener noreferrer"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: menuItems.length * 0.05 }}
                className="px-6 py-3 text-white/70 hover:text-white hover:bg-white/5 transition-colors flex items-center gap-2 text-sm"
                onClick={() => setMobileMenuOpen(false)}
              >
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M12 0C5.374 0 0 5.373 0 12 0 17.302 3.438 21.8 8.207 23.387c.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z" />
                </svg>
                GitHub Repository
              </motion.a>

              {/* MIT info in mobile menu */}
              <div className="px-6 py-4 mt-2 border-t border-white/10 flex items-center gap-3">
                <svg
                  className="h-6 w-auto"
                  viewBox="0 0 536.229 536.229"
                  fill="white"
                  fillOpacity="0.6"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <g>
                    <g>
                      <rect y="130.031" width="58.206" height="276.168" />
                      <rect x="95.356" y="130.031" width="58.206" height="190.712" />
                      <rect x="190.712" y="130.031" width="58.206" height="276.168" />
                      <rect x="381.425" y="217.956" width="58.212" height="188.236" />
                      <rect x="381.425" y="130.031" width="154.805" height="58.206" />
                      <rect x="286.074" y="217.956" width="58.2" height="188.236" />
                      <rect x="286.074" y="130.031" width="58.2" height="58.206" />
                    </g>
                  </g>
                </svg>
                <span
                  className="text-xs text-white/60"
                  style={{
                    fontFamily:
                      'Neue Haas Grotesk Medium, -apple-system, BlinkMacSystemFont, sans-serif',
                    fontWeight: 500,
                  }}
                >
                  Massachusetts Institute of Technology
                </span>
              </div>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
