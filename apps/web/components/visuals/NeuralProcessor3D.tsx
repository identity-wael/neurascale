'use client'

import { useRef, useEffect } from 'react'
import * as anime from 'animejs'

function GPUChip() {
  const chipRef = useRef<HTMLDivElement>(null)
  const coresRef = useRef<HTMLDivElement>(null)
  const dataFlowRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Floating animation for the whole chip
    anime.default({
      targets: chipRef.current,
      translateY: [-5, 5],
      duration: 3000,
      direction: 'alternate',
      loop: true,
      easing: 'easeInOutSine'
    })

    // Pulsing cores animation
    anime.default({
      targets: '.gpu-core',
      scale: [0.9, 1.1],
      duration: 2000,
      direction: 'alternate',
      loop: true,
      delay: anime.stagger(100),
      easing: 'easeInOutQuad'
    })

    // Data flow animation
    anime.default({
      targets: '.data-flow',
      translateX: [-100, 100],
      opacity: [0, 1, 0],
      duration: 1500,
      loop: true,
      delay: anime.stagger(200),
      easing: 'easeInOutCubic'
    })

    // Memory blocks animation
    anime.default({
      targets: '.memory-block',
      backgroundColor: ['#0066ff', '#00aaff', '#0066ff'],
      duration: 1000,
      direction: 'alternate',
      loop: true,
      delay: anime.stagger(150),
      easing: 'easeInOutSine'
    })

  }, [])

  return (
    <div className="relative w-full h-full flex items-center justify-center">
      <div 
        ref={chipRef}
        className="relative w-96 h-96 perspective-1000"
        style={{
          transform: 'rotateX(10deg) rotateY(15deg)',
          transformStyle: 'preserve-3d'
        }}
      >
        {/* Main GPU Die */}
        <div className="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg shadow-2xl border border-gray-600">
          {/* Central Processing Unit */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-gradient-to-br from-green-500 to-green-700 rounded-sm shadow-lg">
            <div className="absolute inset-2 bg-black/30 rounded-sm">
              <div className="text-center pt-8 text-green-300 text-xs font-bold">
                H100
              </div>
            </div>
          </div>

          {/* GPU Cores Grid */}
          <div 
            ref={coresRef}
            className="absolute inset-8 grid grid-cols-8 grid-rows-8 gap-1"
          >
            {Array.from({ length: 64 }).map((_, i) => (
              <div
                key={i}
                className="gpu-core w-full h-full bg-blue-500 rounded-sm opacity-80"
                style={{
                  boxShadow: '0 0 4px #4185f4',
                  background: `linear-gradient(45deg, #4185f4, #1976d2)`
                }}
              />
            ))}
          </div>

          {/* Memory Blocks */}
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={`memory-${i}`}
              className="memory-block absolute w-8 h-16 bg-blue-600 rounded-sm shadow-md"
              style={{
                top: '20px',
                left: `${60 + i * 50}px`,
                boxShadow: '0 0 8px #0066ff'
              }}
            />
          ))}

          {/* Data Flow Lines */}
          <div ref={dataFlowRef} className="absolute inset-0">
            {Array.from({ length: 8 }).map((_, i) => (
              <div
                key={`flow-${i}`}
                className="data-flow absolute h-0.5 w-20 bg-gradient-to-r from-transparent via-cyan-400 to-transparent"
                style={{
                  top: `${100 + i * 25}px`,
                  left: '50px',
                  boxShadow: '0 0 4px #00ffff'
                }}
              />
            ))}
          </div>

          {/* Circuit Traces */}
          <svg className="absolute inset-0 w-full h-full" style={{ zIndex: 1 }}>
            {Array.from({ length: 20 }).map((_, i) => (
              <path
                key={`trace-${i}`}
                d={`M${Math.random() * 400},${Math.random() * 400} Q${Math.random() * 400},${Math.random() * 400} ${Math.random() * 400},${Math.random() * 400}`}
                stroke="#00ff88"
                strokeWidth="1"
                fill="none"
                opacity="0.3"
              />
            ))}
          </svg>

          {/* Corner Pins */}
          {[
            { top: '10px', left: '10px' },
            { top: '10px', right: '10px' },
            { bottom: '10px', left: '10px' },
            { bottom: '10px', right: '10px' }
          ].map((pos, i) => (
            <div
              key={`pin-${i}`}
              className="absolute w-3 h-3 bg-yellow-500 rounded-full shadow-md"
              style={{
                ...pos,
                boxShadow: '0 0 6px #ffd700'
              }}
            />
          ))}

          {/* NEURASCALE Branding */}
          <div className="absolute bottom-4 left-4 text-xs font-bold tracking-wider">
            <span className="text-gray-300">NEURA</span>
            <span className="text-blue-400">SCALE</span>
          </div>
        </div>
      </div>
    </div>
  )
}


export default function NeuralProcessor3D() {
  return (
    <div className="absolute inset-0 w-full h-full bg-black" style={{ minHeight: '100vh', width: '100%', zIndex: 1 }}>
      <GPUChip />
    </div>
  )
}