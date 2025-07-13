'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef, useState } from 'react'

// Video Strip Component
const VideoStrip = ({ 
  videos, 
  speed, 
  direction = 'left',
  className = '' 
}: {
  videos: Array<{ src: string; title: string; aspectRatio: string }>
  speed: number
  direction?: 'left' | 'right'
  className?: string
}) => {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)
  
  return (
    <div className={`relative overflow-hidden ${className}`}>
      <motion.div
        className="flex gap-6"
        animate={{
          x: direction === 'left' ? [-100, -2000] : [100, 2000]
        }}
        transition={{
          duration: speed,
          repeat: Infinity,
          ease: "linear"
        }}
        style={{
          width: 'max-content'
        }}
      >
        {/* Duplicate videos for seamless loop */}
        {[...videos, ...videos].map((video, index) => (
          <motion.div
            key={index}
            className={`relative ${video.aspectRatio} bg-white/5 rounded-lg overflow-hidden border border-white/10`}
            onMouseEnter={() => setHoveredIndex(index)}
            onMouseLeave={() => setHoveredIndex(null)}
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.3 }}
          >
            {/* Video element with fallback */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-400/20 to-blue-600/20">
              {/* Show video if it exists, otherwise show placeholder */}
              <video
                className="w-full h-full object-cover"
                autoPlay
                muted
                loop
                playsInline
                onError={(e) => {
                  // Hide video and show placeholder on error
                  e.currentTarget.style.display = 'none';
                  const placeholder = e.currentTarget.nextElementSibling as HTMLElement;
                  if (placeholder) placeholder.style.display = 'flex';
                }}
              >
                <source src={video.src} type="video/mp4" />
              </video>
              
              {/* Fallback placeholder (hidden by default, shown on video error) */}
              <div className="absolute inset-0 flex items-center justify-center" style={{ display: 'none' }}>
                <div className="text-center">
                  <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center mb-2 mx-auto">
                    <div className="w-0 h-0 border-l-4 border-l-white/80 border-y-2 border-y-transparent ml-1"></div>
                  </div>
                  <p className="text-white/60 text-xs">{video.title}</p>
                </div>
              </div>
              
              {/* Hover overlay */}
              <motion.div
                className="absolute inset-0 bg-black/40 backdrop-blur-sm"
                initial={{ opacity: 0 }}
                animate={{ opacity: hoveredIndex === index ? 1 : 0 }}
                transition={{ duration: 0.2 }}
              />
            </div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  )
}

export default function Vision() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'center center'],
  })

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1])

  // Video data - replace with actual video sources
  const prostheticVideos = [
    { src: '/videos/prosthetic-arm.mp4', title: 'Neural Prosthetic Arm', aspectRatio: 'w-80 h-48' },
    { src: '/videos/prosthetic-leg.mp4', title: 'Robotic Leg Control', aspectRatio: 'w-64 h-48' },
    { src: '/videos/hand-movement.mp4', title: 'Hand Dexterity', aspectRatio: 'w-72 h-48' },
    { src: '/videos/walking-demo.mp4', title: 'Walking Restoration', aspectRatio: 'w-80 h-48' },
  ]

  const brainVisualizationVideos = [
    { src: '/videos/brain-signals.mp4', title: 'Neural Activity', aspectRatio: 'w-72 h-40' },
    { src: '/videos/signal-processing.mp4', title: 'Signal Processing', aspectRatio: 'w-96 h-40' },
    { src: '/videos/neural-patterns.mp4', title: 'Pattern Recognition', aspectRatio: 'w-64 h-40' },
    { src: '/videos/brain-mapping.mp4', title: 'Brain Mapping', aspectRatio: 'w-80 h-40' },
  ]

  const vrRoboticsVideos = [
    { src: '/videos/vr-control.mp4', title: 'VR Neural Control', aspectRatio: 'w-88 h-52' },
    { src: '/videos/robot-swarm.mp4', title: 'Robot Swarm Control', aspectRatio: 'w-72 h-52' },
    { src: '/videos/immersive-reality.mp4', title: 'Immersive Reality', aspectRatio: 'w-80 h-52' },
    { src: '/videos/neural-vr.mp4', title: 'Neural VR Interface', aspectRatio: 'w-96 h-52' },
  ]

  return (
    <section ref={containerRef} className="min-h-screen py-32 relative overflow-hidden bg-gradient-to-b from-black via-gray-950 to-black">
      {/* Parallax Video Strips - More Visible */}
      <div className="absolute inset-0 z-0">
        {/* Strip 1: Prosthetic Demos (Top) */}
        <div className="absolute top-24 left-0 right-0">
          <VideoStrip 
            videos={prostheticVideos} 
            speed={80} 
            direction="left"
            className="opacity-70 hover:opacity-90 transition-all duration-500"
          />
        </div>

        {/* Strip 2: Brain Visualizations (Middle) */}
        <div className="absolute top-1/2 transform -translate-y-1/2 left-0 right-0">
          <VideoStrip 
            videos={brainVisualizationVideos} 
            speed={60} 
            direction="right"
            className="opacity-60 hover:opacity-85 transition-all duration-500"
          />
        </div>

        {/* Strip 3: VR/Robotics (Bottom) */}
        <div className="absolute bottom-24 left-0 right-0">
          <VideoStrip 
            videos={vrRoboticsVideos} 
            speed={40} 
            direction="left"
            className="opacity-70 hover:opacity-90 transition-all duration-500"
          />
        </div>

        {/* Refined gradient overlays for content readability */}
        <div className="absolute inset-0 bg-gradient-to-r from-black/60 via-transparent to-black/60"></div>
        <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-black/40"></div>
      </div>

      {/* Content */}
      <div className="px-6 md:px-12 lg:px-24 relative z-20">
        <motion.div style={{ scale }} className="relative min-h-screen flex flex-col justify-center">
          {/* Section Header */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="flex items-start mb-16"
          >
            <span className="text-white/40 text-sm font-mono mr-4 mt-1">≡</span>
            <span className="text-white/40 text-sm uppercase tracking-[0.2em] font-light">VISION</span>
          </motion.div>

          {/* Main Content */}
          <div className="max-w-6xl relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.2 }}
              viewport={{ once: true }}
              className="mb-12"
            >
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-light leading-tight mb-8 text-white/95">
                Bridging minds and reality
              </h2>
              
              <div className="h-px bg-gradient-to-r from-transparent via-blue-400/50 to-transparent mb-12"></div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.4 }}
              viewport={{ once: true }}
              className="grid lg:grid-cols-2 gap-16 items-center"
            >
              {/* Left column - Statistics */}
              <div className="space-y-8">
                <div className="p-8 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-md">
                  <div className="text-5xl md:text-6xl font-light text-blue-400 mb-4">20M</div>
                  <p className="text-xl md:text-2xl leading-relaxed text-white/80">
                    people worldwide live with paralysis from spinal cord injury and stroke—their minds fully capable but physically separated from the world.
                  </p>
                </div>
                
                {/* Key statistics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl border border-white/10 bg-white/5 backdrop-blur-md text-center">
                    <div className="text-2xl font-light text-blue-300 mb-1">5.4M</div>
                    <div className="text-xs text-white/60 uppercase tracking-wide">New injuries annually</div>
                  </div>
                  <div className="p-4 rounded-xl border border-white/10 bg-white/5 backdrop-blur-md text-center">
                    <div className="text-2xl font-light text-white/90 mb-1">100%</div>
                    <div className="text-xs text-white/60 uppercase tracking-wide">Mental capacity intact</div>
                  </div>
                </div>
              </div>

              {/* Right column - Solution */}
              <div className="space-y-6">
                <div className="p-8 rounded-2xl border border-blue-400/20 bg-blue-400/5 backdrop-blur-md">
                  <h3 className="text-2xl md:text-3xl font-light text-white/95 mb-6">
                    NEURASCALE breaks down these barriers
                  </h3>
                  
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                      <span className="text-lg text-white/80"><span className="text-blue-400 font-medium">Restored mobility</span> through neural prosthetics</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 rounded-full bg-blue-300"></div>
                      <span className="text-lg text-white/80"><span className="text-blue-300 font-medium">Advanced robotics control</span> with thought</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 rounded-full bg-white/60"></div>
                      <span className="text-lg text-white/80"><span className="text-white/90 font-medium">Immersive reality experiences</span> beyond physical limits</span>
                    </div>
                  </div>
                  
                  <div className="mt-8 pt-6 border-t border-white/10">
                    <p className="text-white/60 text-sm leading-relaxed">
                      Through real-time neural signal processing at unprecedented scale and precision
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Call to action */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              viewport={{ once: true }}
              className="mt-16 text-center"
            >
              <button className="px-8 py-4 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-full transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-blue-500/25">
                Explore the Technology
              </button>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}