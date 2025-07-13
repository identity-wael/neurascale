'use client'

import { useState, useEffect } from 'react'
import Hero from '@/components/sections/Hero'
import Problem from '@/components/sections/Problem'
import Solution from '@/components/sections/Solution'
import Compatibility from '@/components/sections/Compatibility'
import Future from '@/components/sections/Future'
import Careers from '@/components/sections/Careers'
import Header from '@/components/layout/Header'
import LoadingScreen from '@/components/ui/LoadingScreen'
import SmoothScroll from '@/components/layout/SmoothScroll'
import { AnimatePresence } from 'framer-motion'

export default function Home() {
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setLoading(false)
    }, 3000)
    return () => clearTimeout(timer)
  }, [])

  return (
    <>
      <AnimatePresence mode="wait">
        {loading && <LoadingScreen key="loading" />}
      </AnimatePresence>
      
      {!loading && (
        <SmoothScroll>
          <Header />
          <main className="bg-black text-white relative">
            <Hero />
            <Problem />
            <Solution />
            <Compatibility />
            <Future />
            <Careers />
          </main>
        </SmoothScroll>
      )}
    </>
  )
}
