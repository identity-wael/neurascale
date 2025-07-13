'use client'

import { useEffect, useRef } from 'react'
import Lenis from '@studio-freight/lenis'

export default function SmoothScroll({ children }: { children: React.ReactNode }) {
  const lenisRef = useRef<Lenis | null>(null)

  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: 'vertical',
      gestureOrientation: 'vertical',
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 2,
      infinite: false,
    })

    lenisRef.current = lenis

    function raf(time: number) {
      lenis.raf(time)
      requestAnimationFrame(raf)
    }

    requestAnimationFrame(raf)

    // Add scroll snap behavior
    const sections = document.querySelectorAll('section')
    let isScrolling = false
    
    const handleScroll = () => {
      if (!isScrolling) {
        window.requestAnimationFrame(() => {
          const scrollTop = window.pageYOffset || document.documentElement.scrollTop
          const windowHeight = window.innerHeight
          
          sections.forEach((section) => {
            const rect = section.getBoundingClientRect()
            const sectionTop = rect.top + scrollTop
            const sectionHeight = rect.height
            const sectionCenter = sectionTop + sectionHeight / 2
            const windowCenter = scrollTop + windowHeight / 2
            
            // Add active class for section in view
            if (Math.abs(sectionCenter - windowCenter) < windowHeight / 2) {
              section.classList.add('in-view')
            } else {
              section.classList.remove('in-view')
            }
          })
          
          isScrolling = false
        })
        isScrolling = true
      }
    }

    lenis.on('scroll', handleScroll)

    return () => {
      lenis.destroy()
    }
  }, [])

  return <>{children}</>
}