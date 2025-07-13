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