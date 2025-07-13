'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'

export default function InteractiveInfographic() {
  const [hoveredButton, setHoveredButton] = useState<string | null>(null)

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 1 }}
      viewport={{ once: true }}
      className="mb-20 flex justify-center"
    >
      <div className="w-full max-w-7xl">
        <div className="relative w-full h-auto">
          {/* SVG Container with dynamic scaling */}
          <svg 
            viewBox="0.0 0.0 960.0 540.0" 
            className="w-full h-auto"
            fill="none" 
            stroke="none" 
            strokeLinecap="square" 
            strokeMiterlimit="10"
            style={{ 
              userSelect: 'text',
              WebkitUserSelect: 'text',
              MozUserSelect: 'text',
              msUserSelect: 'text'
            }}
          >
            {/* Background */}
            <rect width="960" height="540" fill="#181818" />
            
            {/* Interactive Buttons/Sections */}
            {/* Raw Data Section */}
            <g 
              onMouseEnter={() => setHoveredButton('raw-data')}
              onMouseLeave={() => setHoveredButton(null)}
              style={{ cursor: 'pointer' }}
            >
              <rect 
                x="30" 
                y="28" 
                width="206" 
                height="104" 
                rx="20" 
                fill={hoveredButton === 'raw-data' ? '#333333' : '#000000'}
                stroke={hoveredButton === 'raw-data' ? '#4185f4' : 'transparent'}
                strokeWidth="2"
                className="transition-all duration-300"
              />
              <text 
                x="133" 
                y="65" 
                fill="url(#gradient1)" 
                fontSize="32" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
              >
                Raw Data
              </text>
              <text 
                x="133" 
                y="95" 
                fill="#ffffff" 
                fontSize="14" 
                textAnchor="middle"
                className="select-text"
              >
                492 Mb/s
              </text>
            </g>

            {/* 640-core Section */}
            <g 
              onMouseEnter={() => setHoveredButton('640-core')}
              onMouseLeave={() => setHoveredButton(null)}
              style={{ cursor: 'pointer' }}
            >
              <rect 
                x="265" 
                y="28" 
                width="211" 
                height="104" 
                rx="20" 
                fill={hoveredButton === '640-core' ? '#333333' : '#000000'}
                stroke={hoveredButton === '640-core' ? '#4185f4' : 'transparent'}
                strokeWidth="2"
                className="transition-all duration-300"
              />
              <text 
                x="370" 
                y="65" 
                fill="url(#gradient1)" 
                fontSize="28" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
              >
                640-core
              </text>
              <text 
                x="370" 
                y="95" 
                fill="#ffffff" 
                fontSize="14" 
                textAnchor="middle"
                className="select-text"
              >
                TPU Processing
              </text>
            </g>

            {/* AI Models Section */}
            <g 
              onMouseEnter={() => setHoveredButton('ai-models')}
              onMouseLeave={() => setHoveredButton(null)}
              style={{ cursor: 'pointer' }}
            >
              <rect 
                x="505" 
                y="28" 
                width="160" 
                height="104" 
                rx="20" 
                fill={hoveredButton === 'ai-models' ? '#333333' : '#000000'}
                stroke={hoveredButton === 'ai-models' ? '#4185f4' : 'transparent'}
                strokeWidth="2"
                className="transition-all duration-300"
              />
              <text 
                x="585" 
                y="65" 
                fill="url(#gradient1)" 
                fontSize="24" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
              >
                AI Models
              </text>
              <text 
                x="585" 
                y="95" 
                fill="#ffffff" 
                fontSize="14" 
                textAnchor="middle"
                className="select-text"
              >
                Advanced ML
              </text>
            </g>

            {/* GPU Sections */}
            <g 
              onMouseEnter={() => setHoveredButton('gpu-1')}
              onMouseLeave={() => setHoveredButton(null)}
              style={{ cursor: 'pointer' }}
            >
              <rect 
                x="694" 
                y="30" 
                width="114" 
                height="190" 
                rx="23" 
                fill={hoveredButton === 'gpu-1' ? '#333333' : '#000000'}
                stroke={hoveredButton === 'gpu-1' ? '#4185f4' : 'transparent'}
                strokeWidth="2"
                className="transition-all duration-300"
              />
              <text 
                x="751" 
                y="135" 
                fill="url(#gradient1)" 
                fontSize="20" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
                transform="rotate(-90 751 135)"
              >
                14592-core GPU
              </text>
            </g>

            <g 
              onMouseEnter={() => setHoveredButton('gpu-2')}
              onMouseLeave={() => setHoveredButton(null)}
              style={{ cursor: 'pointer' }}
            >
              <rect 
                x="836" 
                y="30" 
                width="114" 
                height="190" 
                rx="23" 
                fill={hoveredButton === 'gpu-2' ? '#333333' : '#000000'}
                stroke={hoveredButton === 'gpu-2' ? '#4185f4' : 'transparent'}
                strokeWidth="2"
                className="transition-all duration-300"
              />
              <text 
                x="893" 
                y="135" 
                fill="url(#gradient1)" 
                fontSize="20" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
                transform="rotate(-90 893 135)"
              >
                Parallel Processing
              </text>
            </g>

            {/* Output sections */}
            <g 
              onMouseEnter={() => setHoveredButton('output-1')}
              onMouseLeave={() => setHoveredButton(null)}
              style={{ cursor: 'pointer' }}
            >
              <rect 
                x="694" 
                y="250" 
                width="116" 
                height="102" 
                rx="20" 
                fill={hoveredButton === 'output-1' ? '#333333' : '#000000'}
                stroke={hoveredButton === 'output-1' ? '#4185f4' : 'transparent'}
                strokeWidth="2"
                className="transition-all duration-300"
              />
              <text 
                x="752" 
                y="285" 
                fill="url(#gradient1)" 
                fontSize="16" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
              >
                Movement
              </text>
              <text 
                x="752" 
                y="305" 
                fill="url(#gradient1)" 
                fontSize="16" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
              >
                Decoding
              </text>
              <text 
                x="752" 
                y="330" 
                fill="#ffffff" 
                fontSize="12" 
                textAnchor="middle"
                className="select-text"
              >
                Real-time commands
              </text>
            </g>

            <g 
              onMouseEnter={() => setHoveredButton('output-2')}
              onMouseLeave={() => setHoveredButton(null)}
              style={{ cursor: 'pointer' }}
            >
              <rect 
                x="836" 
                y="250" 
                width="116" 
                height="102" 
                rx="20" 
                fill={hoveredButton === 'output-2' ? '#333333' : '#000000'}
                stroke={hoveredButton === 'output-2' ? '#4185f4' : 'transparent'}
                strokeWidth="2"
                className="transition-all duration-300"
              />
              <text 
                x="894" 
                y="285" 
                fill="url(#gradient1)" 
                fontSize="16" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
              >
                Brain State
              </text>
              <text 
                x="894" 
                y="305" 
                fill="url(#gradient1)" 
                fontSize="16" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
              >
                Analysis
              </text>
              <text 
                x="894" 
                y="330" 
                fill="#ffffff" 
                fontSize="12" 
                textAnchor="middle"
                className="select-text"
              >
                ML patterns
              </text>
            </g>

            {/* Memory sections */}
            <g 
              onMouseEnter={() => setHoveredButton('memory-1')}
              onMouseLeave={() => setHoveredButton(null)}
              style={{ cursor: 'pointer' }}
            >
              <rect 
                x="694" 
                y="375" 
                width="123" 
                height="66" 
                rx="13" 
                fill={hoveredButton === 'memory-1' ? '#333333' : '#000000'}
                stroke={hoveredButton === 'memory-1' ? '#4185f4' : 'transparent'}
                strokeWidth="2"
                className="transition-all duration-300"
              />
              <text 
                x="755" 
                y="400" 
                fill="url(#gradient1)" 
                fontSize="14" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
              >
                Memory
              </text>
              <text 
                x="755" 
                y="420" 
                fill="url(#gradient1)" 
                fontSize="14" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
              >
                Preservation
              </text>
            </g>

            <g 
              onMouseEnter={() => setHoveredButton('memory-2')}
              onMouseLeave={() => setHoveredButton(null)}
              style={{ cursor: 'pointer' }}
            >
              <rect 
                x="836" 
                y="375" 
                width="123" 
                height="66" 
                rx="13" 
                fill={hoveredButton === 'memory-2' ? '#333333' : '#000000'}
                stroke={hoveredButton === 'memory-2' ? '#4185f4' : 'transparent'}
                strokeWidth="2"
                className="transition-all duration-300"
              />
              <text 
                x="897" 
                y="400" 
                fill="url(#gradient1)" 
                fontSize="14" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
              >
                Cognitive
              </text>
              <text 
                x="897" 
                y="420" 
                fill="url(#gradient1)" 
                fontSize="14" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
              >
                Enhancement
              </text>
            </g>

            {/* Bottom sections */}
            <g 
              onMouseEnter={() => setHoveredButton('bottom-1')}
              onMouseLeave={() => setHoveredButton(null)}
              style={{ cursor: 'pointer' }}
            >
              <rect 
                x="694" 
                y="464" 
                width="266" 
                height="66" 
                rx="13" 
                fill={hoveredButton === 'bottom-1' ? '#333333' : '#000000'}
                stroke={hoveredButton === 'bottom-1' ? '#4185f4' : 'transparent'}
                strokeWidth="2"
                className="transition-all duration-300"
              />
              <text 
                x="827" 
                y="485" 
                fill="url(#gradient1)" 
                fontSize="18" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
              >
                100 Trillion Operations/Second
              </text>
              <text 
                x="827" 
                y="510" 
                fill="#ffffff" 
                fontSize="14" 
                textAnchor="middle"
                className="select-text"
              >
                Real-time neural signal processing
              </text>
            </g>

            {/* Left side sections */}
            <g 
              onMouseEnter={() => setHoveredButton('left-bottom-1')}
              onMouseLeave={() => setHoveredButton(null)}
              style={{ cursor: 'pointer' }}
            >
              <rect 
                x="19" 
                y="464" 
                width="266" 
                height="66" 
                rx="13" 
                fill={hoveredButton === 'left-bottom-1' ? '#333333' : '#000000'}
                stroke={hoveredButton === 'left-bottom-1' ? '#4185f4' : 'transparent'}
                strokeWidth="2"
                className="transition-all duration-300"
              />
              <text 
                x="152" 
                y="485" 
                fill="url(#gradient1)" 
                fontSize="18" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
              >
                Neural-Prosthetics Platform
              </text>
              <text 
                x="152" 
                y="510" 
                fill="#ffffff" 
                fontSize="14" 
                textAnchor="middle"
                className="select-text"
              >
                Open-source infrastructure
              </text>
            </g>

            <g 
              onMouseEnter={() => setHoveredButton('left-bottom-2')}
              onMouseLeave={() => setHoveredButton(null)}
              style={{ cursor: 'pointer' }}
            >
              <rect 
                x="314" 
                y="464" 
                width="360" 
                height="66" 
                rx="13" 
                fill={hoveredButton === 'left-bottom-2' ? '#333333' : '#000000'}
                stroke={hoveredButton === 'left-bottom-2' ? '#4185f4' : 'transparent'}
                strokeWidth="2"
                className="transition-all duration-300"
              />
              <text 
                x="494" 
                y="485" 
                fill="url(#gradient1)" 
                fontSize="18" 
                fontWeight="bold" 
                textAnchor="middle"
                className="select-text"
              >
                Brain-Computer Interface Applications
              </text>
              <text 
                x="494" 
                y="510" 
                fill="#ffffff" 
                fontSize="14" 
                textAnchor="middle"
                className="select-text"
              >
                Restore mobility, unlock robotic control, create immersive realities
              </text>
            </g>

            {/* Gradients */}
            <defs>
              <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#6ed0be" />
                <stop offset="32%" stopColor="#19a1e0" />
                <stop offset="63%" stopColor="#028deb" />
                <stop offset="100%" stopColor="#006dda" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>
    </motion.div>
  )
}