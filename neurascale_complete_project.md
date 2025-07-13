# NEURASCALE - Complete Project Documentation and Code

## README.md

```markdown
# NEURASCALE - Neural-Prosthetics Application Cloud

An open-source infrastructure for processing petabytes of brain data, enabling applications that restore mobility, unlock robotic control, and create immersive realities.

## 📁 Project Structure

```
neurascale/
├── apps/                       # Monorepo root
│   ├── web/                    # Next.js web application (Vercel deploys from here)
│   │   ├── app/
│   │   ├── components/
│   │   ├── public/
│   │   └── package.json
│   ├── packages/               # Shared packages
│   │   ├── ui/                 # Shared UI components
│   │   ├── config-typescript/  # TypeScript configs
│   │   └── config-tailwind/    # Tailwind configs
│   ├── package.json            # Workspace root (future)
│   ├── turbo.json              # Turborepo config (future)
│   └── pnpm-workspace.yaml     # PNPM workspaces (future)
├── backend/                    # Future backend services
├── infrastructure/             # Future IaC
└── README.md                   # This file
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or pnpm

### Installation & Development

```bash
# Navigate to the web app
cd apps/web

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

## 🎨 Features

- **3D Visualizations**: Neural processor and server rack animations using Three.js
- **Smooth Animations**: Framer Motion for fluid transitions
- **Loading Screen**: Professional loading experience
- **Responsive Design**: Works on all devices
- **Type Safety**: Full TypeScript support

## 🚢 Deployment

### Vercel Configuration
- **Root Directory**: `apps/web`
- **Framework Preset**: Next.js
- **Build & Output**: Auto-detected

## 🛠️ Technology Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **3D Graphics**: Three.js, React Three Fiber
- **Animations**: Framer Motion, Lenis
- **Language**: TypeScript
- **Deployment**: Vercel

## 📦 Future Monorepo Setup

When ready to implement the full monorepo:

1. Add workspace configuration files to `apps/`
2. Move shared code to `apps/packages/`
3. Update imports to use workspace packages
4. Change Vercel root directory to `apps/`

## 👥 Team

Led by Rob Franklin (SVP, Blackrock Neurotech), Wael El Ghazzawi (CTO, Brain Finance), and a world-class team of engineers and researchers.

## 📄 License

[Your License]
```

---

## Project Files

### 1. apps/web/package.json

```json
{
  "name": "@neurascale/web",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "framer-motion": "^10.16.16",
    "react-intersection-observer": "^9.5.3",
    "@studio-freight/lenis": "^1.0.33",
    "three": "^0.160.0",
    "@react-three/fiber": "^8.15.0",
    "@react-three/drei": "^9.92.0"
  },
  "devDependencies": {
    "@types/node": "^20.10.5",
    "@types/react": "^18.2.45",
    "@types/react-dom": "^18.2.18",
    "@types/three": "^0.160.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.3",
    "eslint": "^8.0.0",
    "eslint-config-next": "14.0.4"
  }
}
```

### 2. apps/web/next.config.js

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['three'],
}

module.exports = nextConfig
```

### 3. apps/web/tailwind.config.js

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
```

### 4. apps/web/tsconfig.json

```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### 5. apps/web/postcss.config.js

```js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### 6. apps/web/.gitignore

```
# See https://help.github.com/articles/ignoring-files/ for more about ignoring files.

# dependencies
/node_modules
/.pnp
.pnp.js
.yarn/install-state.gz

# testing
/coverage

# next.js
/.next/
/out/

# production
/build

# misc
.DS_Store
*.pem

# debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# local env files
.env*.local

# vercel
.vercel

# typescript
*.tsbuildinfo
next-env.d.ts
```

### 7. apps/web/app/layout.tsx

```tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'NEURASCALE - Neural-Prosthetics Application Cloud',
  description: 'Open-source infrastructure for processing petabytes of brain data, enabling applications that restore mobility, unlock robotic control, and create immersive realities.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
```

### 8. apps/web/app/page.tsx

```tsx
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
import BackgroundEffects from '@/components/ui/BackgroundEffects'
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
          <BackgroundEffects />
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
```

### 9. apps/web/app/globals.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 0%;
    --foreground: 0 0% 100%;
  }

  * {
    @apply border-border;
  }

  html {
    scroll-behavior: smooth;
  }

  body {
    @apply bg-background text-foreground antialiased;
    font-feature-settings: "rlig" 1, "calt" 1;
    overscroll-behavior: none;
    background: #000000;
    background-image: 
      radial-gradient(ellipse at top, #0a1628 0%, transparent 50%),
      radial-gradient(ellipse at bottom, #0d1117 0%, transparent 50%);
  }

  ::selection {
    @apply bg-white/20;
  }

  /* Hide scrollbar for Chrome, Safari and Opera */
  body::-webkit-scrollbar {
    display: none;
  }

  /* Hide scrollbar for IE, Edge and Firefox */
  body {
    -ms-overflow-style: none;  /* IE and Edge */
    scrollbar-width: none;  /* Firefox */
  }

  /* Section styling for full viewport */
  section {
    position: relative;
    width: 100%;
    min-height: 100vh;
    display: flex;
    align-items: center;
  }

  /* Smooth section transitions */
  section.in-view {
    opacity: 1;
  }
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
  
  .gradient-text {
    @apply bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent;
  }

  .gradient-green {
    @apply bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent;
  }

  .glow {
    box-shadow: 0 0 40px rgba(255, 255, 255, 0.1);
  }

  .glow-green {
    box-shadow: 0 0 40px rgba(0, 255, 136, 0.3);
  }

  /* Smooth transitions for all interactive elements */
  .transition-smooth {
    @apply transition-all duration-500 ease-out;
  }

  /* Hover lift effect */
  .hover-lift {
    @apply hover:-translate-y-1 transition-transform duration-300;
  }

  /* Text reveal animation */
  @keyframes reveal {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .reveal {
    animation: reveal 0.8s cubic-bezier(0.215, 0.61, 0.355, 1) forwards;
  }

  /* Fade animations */
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  @keyframes fadeUp {
    from {
      opacity: 0;
      transform: translateY(40px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-fade-in {
    animation: fadeIn 1s ease-out forwards;
  }

  .animate-fade-up {
    animation: fadeUp 1s cubic-bezier(0.215, 0.61, 0.355, 1) forwards;
  }

  /* Stagger delay utilities */
  .delay-100 { animation-delay: 100ms; }
  .delay-200 { animation-delay: 200ms; }
  .delay-300 { animation-delay: 300ms; }
  .delay-400 { animation-delay: 400ms; }
  .delay-500 { animation-delay: 500ms; }

  /* Glass morphism effect */
  .glass {
    @apply backdrop-blur-md bg-white/5 border border-white/10;
  }

  /* Noise overlay */
  .noise::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0.015;
    z-index: 1;
    pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
  }
}
```

### 10. apps/web/components/layout/Header.tsx

```tsx
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
```

### 11. apps/web/components/layout/SmoothScroll.tsx

```tsx
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
      normalizeWheel: true,
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
```

### 12. apps/web/components/sections/Hero.tsx

```tsx
'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef, Suspense } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'
import ScrollIndicator from '@/components/ui/ScrollIndicator'
import dynamic from 'next/dynamic'

// Dynamic import for 3D component to avoid SSR issues
const NeuralProcessor3D = dynamic(
  () => import('@/components/visuals/NeuralProcessor3D'),
  { 
    ssr: false,
    loading: () => <div className="absolute inset-0 bg-black/50" />
  }
)

export default function Hero() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end start'],
  })

  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 0.95])
  const y = useTransform(scrollYProgress, [0, 0.5], [0, -50])

  return (
    <section ref={containerRef} className="relative min-h-screen flex flex-col justify-center px-6 md:px-12 lg:px-24 overflow-hidden">
      {/* 3D Neural Processor Background */}
      <div className="absolute inset-0 opacity-50">
        <Suspense fallback={<div className="absolute inset-0 bg-black" />}>
          <NeuralProcessor3D />
        </Suspense>
      </div>

      <motion.div
        style={{ opacity, scale, y }}
        className="max-w-6xl relative z-10"
      >
        <AnimatedText
          text="Neural-Prosthetics Application Cloud"
          className="text-5xl md:text-7xl lg:text-8xl font-light mb-8"
          delay={0.5}
          stagger={0.02}
        />
        
        <motion.p
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 1 }}
          className="text-xl md:text-2xl lg:text-3xl font-light leading-relaxed text-white/80 max-w-4xl"
        >
          An open-source project designed to process petabytes of complex brain data, blurring the boundaries between the human mind and the real world.
        </motion.p>
        
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1.5 }}
          className="text-lg md:text-xl mt-8 text-white/60"
        >
          Enabling communication at the speed of thought through real-time neural signal processing and agentic applications.
        </motion.p>
      </motion.div>
      <ScrollIndicator />
    </section>
  )
}
```

### 13. apps/web/components/sections/Problem.tsx

```tsx
'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'
import dynamic from 'next/dynamic'

const NeuralProcessor3D = dynamic(
  () => import('@/components/visuals/NeuralProcessor3D'),
  { 
    ssr: false,
    loading: () => <div className="absolute inset-0 bg-black/50" />
  }
)

// AI Unit Icon Component
const AIUnitIcon = () => (
  <svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="20" y="20" width="80" height="80" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.3" />
    <rect x="30" y="30" width="60" height="60" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.5" />
    <rect x="40" y="40" width="40" height="40" fill="currentColor" opacity="0.1" />
    
    {/* Corner elements */}
    <path d="M20 20 L30 20 L30 30" stroke="currentColor" strokeWidth="2" fill="none" />
    <path d="M90 20 L100 20 L100 30" stroke="currentColor" strokeWidth="2" fill="none" />
    <path d="M100 90 L100 100 L90 100" stroke="currentColor" strokeWidth="2" fill="none" />
    <path d="M30 100 L20 100 L20 90" stroke="currentColor" strokeWidth="2" fill="none" />
    
    {/* Center cross */}
    <path d="M50 60 L70 60" stroke="currentColor" strokeWidth="1" opacity="0.8" />
    <path d="M60 50 L60 70" stroke="currentColor" strokeWidth="1" opacity="0.8" />
  </svg>
)

export default function Problem() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'end start'],
  })

  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0])
  const y = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [100, 0, 0, -100])

  return (
    <section ref={containerRef} className="min-h-screen flex items-center px-6 md:px-12 lg:px-24 py-24 relative">
      {/* 3D Processor Background */}
      <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1/2 h-full opacity-20 hidden lg:block">
        <NeuralProcessor3D />
      </div>

      <motion.div
        style={{ opacity, y }}
        className="max-w-5xl relative z-10"
      >
        <div className="flex items-start mb-12">
          <span className="text-white/40 text-sm font-mono mr-4">≡</span>
          <span className="text-white/40 text-sm uppercase tracking-wider">SPECIFICITY</span>
        </div>

        <AnimatedText
          text="Architected to practically deliver 10×–30× reductions in energy consumption"
          className="text-4xl md:text-5xl lg:text-6xl font-light mb-12"
          stagger={0.02}
        />

        <div className="grid md:grid-cols-2 gap-16 items-start">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            viewport={{ once: true }}
          >
            <h3 className="text-2xl font-light mb-6 text-white/90">AI unit</h3>
            <p className="text-lg leading-relaxed text-white/70 mb-6">
              Built on NEURASCALE's proprietary multi-physics computing core, high-volume AI tasks with n³ complexity are accelerated and executed at ultra-low power consumption.
            </p>
            <div className="text-white/40 mt-8">
              <AIUnitIcon />
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.7 }}
            viewport={{ once: true }}
            className="space-y-8"
          >
            <div>
              <h4 className="text-lg font-light mb-3 text-white/80">Control unit</h4>
              <p className="text-white/60 text-sm leading-relaxed">
                Its deterministic architecture maximizes memory transfer efficiency and speeds up pointwise operations, achieving optimal performance for tasks with n² complexity.
              </p>
            </div>
            <div className="space-y-3 text-sm">
              <div className="flex items-start">
                <span className="text-white/40 mr-3 font-mono">An</span>
                <span className="text-white/60">Higher computation capacity</span>
              </div>
              <div className="flex items-start">
                <span className="text-white/40 mr-3 font-mono">An</span>
                <span className="text-white/60">Higher throughput</span>
              </div>
              <div className="flex items-start">
                <span className="text-white/40 mr-3 font-mono">An</span>
                <span className="text-white/60">Lower energy consumption</span>
              </div>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </section>
  )
}
```

### 14. apps/web/components/sections/Solution.tsx

```tsx
'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'

export default function Solution() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'center center'],
  })

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1])

  const features = [
    {
      title: 'Real-Time Movement Decoding',
      description: 'Instantly translates brain signals into commands to control external devices, restoring the direct link between intent and action.',
    },
    {
      title: 'Brain State Analysis',
      description: 'Machine learning identifies conditions like focus, fatigue, or seizures from patterns in neural data for proactive care.',
    },
    {
      title: 'Memory Preservation',
      description: 'Stimulation reinforces memory-related brain signals, restoring memory and fighting cognitive decline.',
    },
  ]

  return (
    <section ref={containerRef} className="min-h-screen px-6 md:px-12 lg:px-24 py-24 relative">
      <motion.div style={{ scale }} className="relative z-10">
        <AnimatedText
          text="Core capabilities that unlock human potential"
          className="text-3xl md:text-4xl lg:text-5xl font-light mb-16 max-w-4xl"
        />
        
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
          className="text-lg md:text-xl text-white/80 mb-16 max-w-3xl"
        >
          NEURASCALE processes up to 492Mb/s of raw neural data through advanced AI models running on 640-core TPUs and 14592-core GPUs, achieving 100 trillion ops/sec.
        </motion.p>

        <div className="grid md:grid-cols-3 gap-12">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: index * 0.2 }}
              viewport={{ once: true }}
              className="text-left"
            >
              <div className="flex items-start mb-6">
                <span className="text-white/40 text-sm font-mono mr-4">0{index + 1}</span>
                <div className="w-12 h-[1px] bg-white/20 mt-3" />
              </div>
              <h3 className="text-xl font-light mb-4 text-white/90">
                {feature.title}
              </h3>
              <p className="text-white/60 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </section>
  )
}
```

### 15. apps/web/components/sections/Compatibility.tsx

```tsx
'use client'

import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'

export default function Compatibility() {
  const { ref, inView } = useInView({
    threshold: 0.3,
    triggerOnce: true,
  })

  return (
    <section ref={ref} className="min-h-screen flex items-center px-6 md:px-12 lg:px-24 py-24">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={inView ? { opacity: 1, scale: 1 } : {}}
        transition={{ duration: 1 }}
        className="max-w-5xl"
      >
        <h2 className="text-3xl md:text-4xl lg:text-5xl font-light mb-12">
          Built on proven technologies, designed for scale
        </h2>
        
        <p className="text-lg md:text-xl text-white/80 mb-8">
          NEURASCALE leverages industry-standard frameworks and cloud-native architecture to ensure seamless integration with existing healthcare and research infrastructure.
        </p>

        <div className="grid md:grid-cols-2 gap-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="p-6 bg-white/5 rounded-xl backdrop-blur-sm"
          >
            <h3 className="text-xl font-medium mb-3">Neural Management System</h3>
            <p className="text-white/70">
              Orchestrates operations between Neural Interaction Layer, Emulation Layer, and Physical Integration Layer using modular monolith architecture.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="p-6 bg-white/5 rounded-xl backdrop-blur-sm"
          >
            <h3 className="text-xl font-medium mb-3">Open Standards</h3>
            <p className="text-white/70">
              Compatible with PyTorch, TensorFlow, and major cloud providers. Supports Lab Streaming Layer (LSL) and industry-standard neural data formats.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="p-6 bg-white/5 rounded-xl backdrop-blur-sm"
          >
            <h3 className="text-xl font-medium mb-3">Extended Reality Engine</h3>
            <p className="text-white/70">
              Full-Dive VR capabilities with Nvidia OmniVerse integration, enabling seamless neural-to-virtual interaction with under 20ns latency.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="p-6 bg-white/5 rounded-xl backdrop-blur-sm"
          >
            <h3 className="text-xl font-medium mb-3">Agentic Applications</h3>
            <p className="text-white/70">
              AI-powered applications that generate actions directly from movement intents and brain states using LLMs and reinforcement learning.
            </p>
          </motion.div>
        </div>
      </motion.div>
    </section>
  )
}
```

### 16. apps/web/components/sections/Future.tsx

```tsx
'use client'

import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import dynamic from 'next/dynamic'

const ServerRacks3D = dynamic(
  () => import('@/components/visuals/ServerRacks3D'),
  { 
    ssr: false,
    loading: () => <div className="absolute inset-0 bg-black" />
  }
)

export default function Future() {
  const { ref, inView } = useInView({
    threshold: 0.3,
    triggerOnce: true,
  })

  return (
    <section ref={ref} className="min-h-screen flex items-center px-6 md:px-12 lg:px-24 py-24 relative overflow-hidden">
      {/* 3D Server Racks Background */}
      <div className="absolute inset-0 opacity-40">
        <ServerRacks3D />
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={inView ? { opacity: 1 } : {}}
        transition={{ duration: 1 }}
        className="max-w-5xl relative z-10"
      >
        <h2 className="text-4xl md:text-5xl lg:text-6xl font-light mb-12">
          Unlocking human potential at the speed of thought
        </h2>
        
        <p className="text-xl md:text-2xl text-white/80 mb-16">
          Join us in building the infrastructure that will restore autonomy to millions and redefine human-machine interaction
        </p>

        <div className="space-y-8 text-lg text-white/70">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="backdrop-blur-sm bg-black/30 p-6 rounded-lg border border-white/10"
          >
            <h3 className="text-2xl text-white mb-3">Restored Autonomy</h3>
            <p>
              For millions living with paralysis, NEURASCALE offers the potential to regain mobility and communication, drastically improving quality of life through direct neural control of prosthetics and devices.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="backdrop-blur-sm bg-black/30 p-6 rounded-lg border border-white/10"
          >
            <h3 className="text-2xl text-white mb-3">Advanced Human-Machine Interaction</h3>
            <p>
              Enable sophisticated control over robotic systems, from prosthetic limbs to swarms of robots, and facilitate "Full-Dive" VR experiences seamlessly integrated with neural intent.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="backdrop-blur-sm bg-black/30 p-6 rounded-lg border border-white/10"
          >
            <h3 className="text-2xl text-white mb-3">Next-Generation Security</h3>
            <p>
              Introducing passwordless "Neural ID" authentication using unique brain patterns, providing unprecedented security for the digital age.
            </p>
          </motion.div>
        </div>
      </motion.div>
    </section>
  )
}
```

### 17. apps/web/components/sections/Careers.tsx

```tsx
'use client'

import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import JobTable from '@/components/ui/JobTable'

// SVG Icons matching the style from the screenshots
const HighVelocityIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="10" cy="20" r="2" fill="currentColor" opacity="0.8" />
    <circle cx="20" cy="20" r="2" fill="currentColor" opacity="0.8" />
    <circle cx="30" cy="20" r="2" fill="currentColor" opacity="0.8" />
    <path d="M10 20 L30 20" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
    <path d="M20 10 L20 30" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
    <path d="M12 12 L28 28" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
    <path d="M28 12 L12 28" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
  </svg>
)

const OneUnitIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="20" cy="20" r="15" stroke="currentColor" strokeWidth="1" opacity="0.6" fill="none" />
    <circle cx="20" cy="10" r="2" fill="currentColor" />
    <circle cx="10" cy="20" r="2" fill="currentColor" />
    <circle cx="30" cy="20" r="2" fill="currentColor" />
    <circle cx="20" cy="30" r="2" fill="currentColor" />
    <path d="M20 10 L10 20 L20 30 L30 20 Z" stroke="currentColor" strokeWidth="0.5" fill="none" opacity="0.4" />
  </svg>
)

const ExcellenceIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 5 L25 15 L35 17 L27.5 24.5 L29.5 34.5 L20 29 L10.5 34.5 L12.5 24.5 L5 17 L15 15 Z" 
          stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <circle cx="20" cy="20" r="2" fill="currentColor" />
  </svg>
)

export default function Careers() {
  const { ref, inView } = useInView({
    threshold: 0.2,
    triggerOnce: true,
  })

  const values = [
    {
      icon: <HighVelocityIcon />,
      title: 'HIGH VELOCITY',
      description: 'Speed matters. We move quickly, one step at a time.',
    },
    {
      icon: <OneUnitIcon />,
      title: 'ONE UNIT',
      description: 'We\'re all in this together, with relationships grounded in trust, respect, and camaraderie.',
    },
    {
      icon: <ExcellenceIcon />,
      title: 'DO GREAT THINGS',
      description: 'We deliver work we\'re proud to sign our name to.',
    },
  ]

  return (
    <section ref={ref} className="min-h-screen px-6 md:px-12 lg:px-24 py-24">
      <motion.div
        initial={{ opacity: 0 }}
        animate={inView ? { opacity: 1 } : {}}
        transition={{ duration: 1 }}
      >
        <div className="flex items-start mb-12">
          <span className="text-white/40 text-sm font-mono mr-4">≡</span>
          <span className="text-white/40 text-sm uppercase tracking-wider">TEAM</span>
        </div>

        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-4xl md:text-5xl lg:text-6xl font-light mb-8 max-w-4xl"
        >
          If you're excited about shaping the future of brain-computer interfaces, we'd love to hear from you
        </motion.h2>

        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-lg text-white/60 mb-16 max-w-3xl space-y-4"
        >
          <p>
            The power of computing has enabled humanity to explore new frontiers in neuroscience, 
            develop life-changing prosthetics, and restore autonomy to those who need it most.
          </p>
          <p>
            We don't want human potential to be limited by physical constraints.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-x-12 gap-y-16 mb-24">
          {values.map((value, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: 0.3 + index * 0.1 }}
              className="border border-white/10 p-8 hover:border-white/20 transition-colors duration-500"
            >
              <div className="text-white/60 mb-6">{value.icon}</div>
              <h3 className="text-lg font-light mb-4 text-white/90 uppercase tracking-wider">
                {value.title}
              </h3>
              <p className="text-white/60 text-sm leading-relaxed">{value.description}</p>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <JobTable />
        </motion.div>
      </motion.div>
    </section>
  )
}
```

### 18. apps/web/components/ui/LoadingScreen.tsx

```tsx
'use client'

import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

export default function LoadingScreen() {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + 2
      })
    }, 50)

    return () => clearInterval(interval)
  }, [])

  return (
    <motion.div
      initial={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
      className="fixed inset-0 bg-black z-50 flex items-center justify-center"
    >
      <div className="text-center">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-4xl md:text-5xl font-light mb-8 tracking-wider"
        >
          NEURAL-PROSTHETICS APPLICATION CLOUD
        </motion.h1>
        
        <div className="w-64 mx-auto">
          <div className="flex justify-between items-center mb-2">
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="text-sm text-white/60"
            >
              Loading
            </motion.span>
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="text-sm text-white/60"
            >
              {progress.toString().padStart(2, '0')}%
            </motion.span>
          </div>
          
          <div className="h-[1px] bg-white/10 relative overflow-hidden">
            <motion.div
              className="absolute inset-y-0 left-0 bg-white/80"
              initial={{ width: '0%' }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.1 }}
            />
          </div>
        </div>
      </div>
    </motion.div>
  )
}
```

### 19. apps/web/components/ui/AnimatedText.tsx

```tsx
'use client'

import { motion } from 'framer-motion'
import { useInView } from 'react-intersection-observer'

interface AnimatedTextProps {
  text: string
  className?: string
  delay?: number
  stagger?: number
}

export default function AnimatedText({ 
  text, 
  className = '', 
  delay = 0,
  stagger = 0.03 
}: AnimatedTextProps) {
  const { ref, inView } = useInView({
    threshold: 0.1,
    triggerOnce: true,
  })

  const words = text.split(' ')

  const container = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delayChildren: delay,
        staggerChildren: stagger,
      },
    },
  }

  const child = {
    hidden: {
      opacity: 0,
      y: 20,
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.8,
        ease: [0.215, 0.61, 0.355, 1],
      },
    },
  }

  return (
    <motion.div
      ref={ref}
      variants={container}
      initial="hidden"
      animate={inView ? 'visible' : 'hidden'}
      className={`${className} flex flex-wrap`}
    >
      {words.map((word, i) => (
        <motion.span
          key={i}
          variants={child}
          className="inline-block mr-[0.25em] last:mr-0"
        >
          {word}
        </motion.span>
      ))}
    </motion.div>
  )
}
```

### 20. apps/web/components/ui/ScrollIndicator.tsx

```tsx
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
```

### 21. apps/web/components/ui/JobTable.tsx

```tsx
'use client'

import { motion } from 'framer-motion'

const jobs = [
  {
    position: 'Neural Interface Engineer',
    location: 'Mountain View, Remote',
  },
  {
    position: 'ML/AI Research Scientist',
    location: 'San Francisco, Remote',
  },
  {
    position: 'Cloud Infrastructure Architect',
    location: 'Remote',
  },
  {
    position: 'Brain-Computer Interface Specialist',
    location: 'Boston, Remote',
  },
  {
    position: 'Full-Stack Developer (Agentic Applications)',
    location: 'Remote',
  },
]

export default function JobTable() {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-white/20">
            <th className="text-left py-4 px-4 font-normal text-white/60">Position</th>
            <th className="text-left py-4 px-4 font-normal text-white/60">Location</th>
            <th className="w-24"></th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job, index) => (
            <motion.tr
              key={index}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.1 }}
              className="border-b border-white/10 hover:bg-white/5 transition-colors"
            >
              <td className="py-6 px-4">{job.position}</td>
              <td className="py-6 px-4 text-white/70">{job.location}</td>
              <td className="py-6 px-4">
                <button className="text-white/60 hover:text-white transition-colors">
                  →
                </button>
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

### 22. apps/web/components/ui/BackgroundEffects.tsx

```tsx
'use client'

import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

export default function BackgroundEffects() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const setCanvasSize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    setCanvasSize()
    window.addEventListener('resize', setCanvasSize)

    // Particle system
    const particles: Array<{
      x: number
      y: number
      vx: number
      vy: number
      size: number
      opacity: number
    }> = []

    // Create particles
    for (let i = 0; i < 50; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        size: Math.random() * 2 + 1,
        opacity: Math.random() * 0.5 + 0.1,
      })
    }

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      particles.forEach((particle) => {
        // Update position
        particle.x += particle.vx
        particle.y += particle.vy

        // Wrap around edges
        if (particle.x < 0) particle.x = canvas.width
        if (particle.x > canvas.width) particle.x = 0
        if (particle.y < 0) particle.y = canvas.height
        if (particle.y > canvas.height) particle.y = 0

        // Draw particle
        ctx.beginPath()
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(255, 255, 255, ${particle.opacity})`
        ctx.fill()
      })

      requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('resize', setCanvasSize)
    }
  }, [])

  return (
    <>
      <canvas
        ref={canvasRef}
        className="fixed inset-0 pointer-events-none opacity-40"
        style={{ mixBlendMode: 'screen' }}
      />
      
      {/* Gradient orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            x: [0, 100, 0],
            y: [0, -100, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear",
          }}
          className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-blue-500/10 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            x: [0, -100, 0],
            y: [0, 100, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "linear",
          }}
          className="absolute bottom-1/4 right-1/4 w-[800px] h-[800px] bg-purple-500/10 rounded-full blur-3xl"
        />
      </div>

      {/* Noise texture overlay */}
      <div 
        className="fixed inset-0 opacity-[0.015] pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
          backgroundRepeat: 'repeat',
        }}
      />
    </>
  )
}
```

### 23. apps/web/components/visuals/NeuralProcessor3D.tsx

```tsx
'use client'

import { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame, useLoader } from '@react-three/fiber'
import { 
  Float, 
  Environment,
  ContactShadows,
  PerspectiveCamera,
  MeshReflectorMaterial,
  useTexture,
  Sparkles
} from '@react-three/drei'
import * as THREE from 'three'

function ProcessorChip() {
  const meshRef = useRef<THREE.Mesh>(null)
  const glowRef = useRef<THREE.Mesh>(null)
  const [hovered, setHovered] = useState(false)

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.2
    }
    if (glowRef.current) {
      glowRef.current.material.emissiveIntensity = 0.5 + Math.sin(state.clock.elapsedTime * 2) * 0.3
    }
  })

  return (
    <Float
      speed={1.5}
      rotationIntensity={0.2}
      floatIntensity={0.3}
      floatingRange={[-0.1, 0.1]}
    >
      <group
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        {/* Base PCB */}
        <mesh ref={meshRef} castShadow receiveShadow>
          <boxGeometry args={[4, 0.15, 4]} />
          <meshStandardMaterial 
            color="#0a0a0a"
            metalness={0.9}
            roughness={0.2}
          />
        </mesh>

        {/* PCB Surface Details */}
        <mesh position={[0, 0.08, 0]}>
          <planeGeometry args={[3.8, 3.8]} />
          <meshStandardMaterial 
            color="#111111"
            metalness={0.7}
            roughness={0.3}
          />
        </mesh>

        {/* Outer chip package */}
        {[-1.5, -0.5, 0.5, 1.5].map((x) => 
          [-1.5, -0.5, 0.5, 1.5].map((z) => (
            <mesh key={`${x}-${z}`} position={[x, 0.1, z]}>
              <boxGeometry args={[0.7, 0.05, 0.7]} />
              <meshStandardMaterial 
                color="#1a1a1a"
                metalness={0.8}
                roughness={0.3}
              />
            </mesh>
          ))
        )}

        {/* Central processor with glow */}
        <mesh position={[0, 0.15, 0]}>
          <boxGeometry args={[1.5, 0.1, 1.5]} />
          <meshStandardMaterial 
            color="#000000"
            metalness={0.95}
            roughness={0.1}
          />
        </mesh>

        {/* Glowing green core */}
        <mesh ref={glowRef} position={[0, 0.2, 0]}>
          <boxGeometry args={[1.2, 0.05, 1.2]} />
          <meshStandardMaterial 
            color="#00ff88"
            emissive="#00ff88"
            emissiveIntensity={hovered ? 1 : 0.5}
            metalness={0.5}
            roughness={0}
          />
        </mesh>

        {/* Core details */}
        <mesh position={[0, 0.25, 0]}>
          <boxGeometry args={[0.8, 0.02, 0.8]} />
          <meshStandardMaterial 
            color="#00ff88"
            emissive="#00ff88"
            emissiveIntensity={0.8}
          />
        </mesh>

        {/* Connection pins - sides */}
        {Array.from({ length: 12 }).map((_, i) => (
          <group key={`pins-${i}`}>
            <mesh position={[2.1, -0.05, -1.8 + i * 0.3]}>
              <boxGeometry args={[0.2, 0.05, 0.08]} />
              <meshStandardMaterial color="#gold" metalness={0.8} roughness={0.2} />
            </mesh>
            <mesh position={[-2.1, -0.05, -1.8 + i * 0.3]}>
              <boxGeometry args={[0.2, 0.05, 0.08]} />
              <meshStandardMaterial color="#gold" metalness={0.8} roughness={0.2} />
            </mesh>
          </group>
        ))}

        {/* Capacitors */}
        {[
          [-1.5, 0.15, 0],
          [1.5, 0.15, 0],
          [0, 0.15, -1.5],
          [0, 0.15, 1.5],
        ].map((pos, i) => (
          <mesh key={`cap-${i}`} position={pos as [number, number, number]}>
            <cylinderGeometry args={[0.1, 0.1, 0.1]} />
            <meshStandardMaterial color="#333333" metalness={0.7} />
          </mesh>
        ))}
      </group>
    </Float>
  )
}

function CircuitLines() {
  return (
    <group position={[0, -2, 0]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[3, 8, 6, 1]} />
        <meshBasicMaterial color="#003366" opacity={0.3} transparent />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[5, 6, 6, 1]} />
        <meshBasicMaterial color="#003366" opacity={0.2} transparent />
      </mesh>
    </group>
  )
}

export default function NeuralProcessor3D() {
  return (
    <div className="absolute inset-0 w-full h-full">
      <Canvas
        shadows
        gl={{ 
          antialias: true, 
          alpha: true,
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.5
        }}
      >
        <PerspectiveCamera makeDefault position={[5, 4, 5]} fov={45} />
        
        <ambientLight intensity={0.2} />
        <pointLight position={[10, 10, 10]} intensity={0.5} castShadow />
        <pointLight position={[-10, 10, -10]} intensity={0.3} />
        <pointLight position={[0, 5, 0]} intensity={0.5} color="#00ff88" />
        
        <ProcessorChip />
        <CircuitLines />
        
        <ContactShadows
          position={[0, -2, 0]}
          opacity={0.4}
          scale={10}
          blur={2}
          far={4}
        />
        
        <Sparkles
          count={50}
          scale={10}
          size={2}
          speed={0.4}
          opacity={0.3}
          color="#00ff88"
        />
        
        <Environment preset="night" />
      </Canvas>
    </div>
  )
}
```

### 24. apps/web/components/visuals/ServerRacks3D.tsx

```tsx
'use client'

import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { 
  PerspectiveCamera,
  Environment,
  Float,
  MeshReflectorMaterial
} from '@react-three/drei'
import * as THREE from 'three'

function ServerRack({ position, delay = 0 }: { position: [number, number, number], delay?: number }) {
  const groupRef = useRef<THREE.Group>(null)
  
  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime + delay) * 0.05
    }
  })

  return (
    <Float speed={1} rotationIntensity={0.01} floatIntensity={0.1}>
      <group ref={groupRef} position={position}>
        {/* Rack frame */}
        <mesh castShadow receiveShadow>
          <boxGeometry args={[2, 4, 0.8]} />
          <meshStandardMaterial 
            color="#0a0a0a"
            metalness={0.9}
            roughness={0.3}
          />
        </mesh>

        {/* Server units */}
        {Array.from({ length: 8 }).map((_, i) => (
          <group key={i} position={[0, -1.7 + i * 0.45, 0.05]}>
            {/* Server chassis */}
            <mesh castShadow>
              <boxGeometry args={[1.8, 0.4, 0.7]} />
              <meshStandardMaterial 
                color="#1a1a1a"
                metalness={0.8}
                roughness={0.4}
              />
            </mesh>
            
            {/* Front panel */}
            <mesh position={[0, 0, 0.36]}>
              <boxGeometry args={[1.7, 0.35, 0.02]} />
              <meshStandardMaterial 
                color="#2a2a2a"
                metalness={0.7}
                roughness={0.5}
              />
            </mesh>

            {/* LED indicators */}
            <mesh position={[-0.7, 0, 0.37]}>
              <boxGeometry args={[0.05, 0.05, 0.01]} />
              <meshStandardMaterial 
                color="#00ff00"
                emissive="#00ff00"
                emissiveIntensity={Math.random() > 0.5 ? 1 : 0.3}
              />
            </mesh>
            <mesh position={[-0.6, 0, 0.37]}>
              <boxGeometry args={[0.05, 0.05, 0.01]} />
              <meshStandardMaterial 
                color="#0099ff"
                emissive="#0099ff"
                emissiveIntensity={Math.random() > 0.5 ? 1 : 0.3}
              />
            </mesh>

            {/* Drive bays */}
            {Array.from({ length: 4 }).map((_, j) => (
              <mesh key={j} position={[0.2 + j * 0.3, 0, 0.37]}>
                <boxGeometry args={[0.25, 0.25, 0.02]} />
                <meshStandardMaterial 
                  color="#151515"
                  metalness={0.9}
                  roughness={0.2}
                />
              </mesh>
            ))}
          </group>
        ))}
      </group>
    </Float>
  )
}

function DataCenter() {
  const positions: [number, number, number][] = [
    [-4, 0, -2],
    [-2, 0, -2],
    [0, 0, -2],
    [2, 0, -2],
    [4, 0, -2],
    [-4, 0, 0],
    [-2, 0, 0],
    [0, 0, 0],
    [2, 0, 0],
    [4, 0, 0],
    [-4, 0, 2],
    [-2, 0, 2],
    [0, 0, 2],
    [2, 0, 2],
    [4, 0, 2],
  ]

  return (
    <>
      {positions.map((pos, i) => (
        <ServerRack key={i} position={pos} delay={i * 0.1} />
      ))}
    </>
  )
}

export default function ServerRacks3D() {
  return (
    <div className="absolute inset-0 w-full h-full">
      <Canvas
        shadows
        gl={{ 
          antialias: true, 
          alpha: true,
          toneMapping: THREE.ACESFilmicToneMapping,
        }}
      >
        <PerspectiveCamera 
          makeDefault 
          position={[8, 5, 8]} 
          fov={50}
        />
        
        <fog attach="fog" args={['#000000', 5, 20]} />
        
        <ambientLight intensity={0.1} />
        <pointLight position={[10, 10, 10]} intensity={0.3} castShadow />
        <pointLight position={[-10, 10, -10]} intensity={0.2} />
        <spotLight
          position={[0, 10, 0]}
          angle={0.5}
          penumbra={1}
          intensity={0.5}
          castShadow
          shadow-mapSize={[2048, 2048]}
        />
        
        <DataCenter />
        
        {/* Floor with reflection */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -2, 0]} receiveShadow>
          <planeGeometry args={[20, 20]} />
          <MeshReflectorMaterial
            blur={[300, 100]}
            resolution={2048}
            mixBlur={1}
            mixStrength={80}
            roughness={1}
            depthScale={1.2}
            minDepthThreshold={0.4}
            maxDepthThreshold={1.4}
            color="#101010"
            metalness={0.5}
          />
        </mesh>
        
        <Environment preset="night" />
      </Canvas>
    </div>
  )
}
```

---

## Installation & Running Instructions

```bash
# Create the project directory
mkdir -p neurascale/apps/web

# Navigate to the web directory
cd neurascale/apps/web

# Create all the files as shown above in their respective directories

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Vercel Deployment

1. Push your code to GitHub
2. Import the repository in Vercel
3. Set the root directory to `apps/web`
4. Deploy!

The complete NEURASCALE project is now ready with all 24 files properly structured and configured for immediate deployment.