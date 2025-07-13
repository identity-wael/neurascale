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
          Meet the minds behind NEURASCALE
        </motion.h2>

        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-lg text-white/60 mb-16 max-w-4xl space-y-4"
        >
          <p>
            Our team combines decades of experience in AI, neural interfaces, scalable cloud infrastructure, 
            and advanced robotics to bridge the gap between human potential and technological capability.
          </p>
          <p>
            United by our shared passion for unlocking human potential, we're building the future where 
            physical limitations no longer define what's possible.
          </p>
        </motion.div>

        {/* Team Members */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-20">
          {[
            {
              name: 'Rob Franklin',
              role: 'Co-Founder & Chief Architect',
              expertise: 'Neural Interface Design, AI/ML Systems',
              bio: 'Leading expert in neural signal processing with 15+ years developing brain-computer interfaces for medical applications.'
            },
            {
              name: 'Wael El Ghazzawi',
              role: 'Co-Founder & CTO',
              expertise: 'Scalable Cloud Infrastructure, Data Engineering',
              bio: 'Former cloud architect at major tech companies, specializing in real-time data processing at petabyte scale.'
            },
            {
              name: 'Ron Lehman',
              role: 'Head of Robotics Integration',
              expertise: 'Robotics Control Systems, Prosthetics',
              bio: 'Pioneering work in neural-controlled prosthetics and robotic systems with multiple breakthrough patents.'
            },
            {
              name: 'Donald Woodruff',
              role: 'Lead AI Research Scientist',
              expertise: 'Machine Learning, Pattern Recognition',
              bio: 'PhD in Computational Neuroscience, leading research in real-time neural pattern decoding algorithms.'
            },
            {
              name: 'Jason Franklin',
              role: 'VP of Engineering',
              expertise: 'Software Architecture, DevOps',
              bio: 'Expert in building fault-tolerant systems for mission-critical applications in healthcare and aerospace.'
            },
            {
              name: 'Vincent Liu',
              role: 'Head of XR/Immersive Technologies',
              expertise: 'Virtual Reality, Neural Interfaces',
              bio: 'Specialist in neural-controlled VR systems and immersive brain-computer interaction experiences.'
            }
          ].map((member, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: 0.3 + index * 0.1 }}
              className="p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
            >
              <h3 className="text-xl font-light text-white/90 mb-2">{member.name}</h3>
              <p className="text-blue-400/80 text-sm mb-3">{member.role}</p>
              <p className="text-white/60 text-sm mb-4">{member.expertise}</p>
              <p className="text-white/50 text-xs leading-relaxed">{member.bio}</p>
            </motion.div>
          ))}
        </div>

        {/* Mission Statement */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="p-8 rounded-lg border border-blue-400/30 bg-blue-400/5 backdrop-blur-sm mb-20"
        >
          <h3 className="text-2xl font-light text-white/90 mb-4">Our Mission</h3>
          <p className="text-white/70 leading-relaxed text-lg">
            To democratize neural interface technology through open-source innovation, 
            creating a world where human potential is unlimited by physical constraints. 
            We believe that breakthrough technologies should be accessible to all, 
            fostering collaboration and accelerating progress for humanity.
          </p>
        </motion.div>

        {/* Core Values */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 1.0 }}
          className="mb-20"
        >
          <h3 className="text-2xl md:text-3xl font-light mb-12 text-white/90">Our Values</h3>
          <div className="grid md:grid-cols-3 gap-x-12 gap-y-16">
            {values.map((value, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.8, delay: 1.1 + index * 0.1 }}
                className="border border-white/10 p-8 hover:border-white/20 transition-colors duration-500"
              >
                <div className="text-white/60 mb-6">{value.icon}</div>
                <h4 className="text-lg font-light mb-4 text-white/90 uppercase tracking-wider">
                  {value.title}
                </h4>
                <p className="text-white/60 text-sm leading-relaxed">{value.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Join Our Team */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 1.4 }}
          className="mb-16"
        >
          <h3 className="text-2xl md:text-3xl font-light mb-8 text-white/90">
            Join Our Mission
          </h3>
          <p className="text-lg text-white/70 mb-8 max-w-3xl">
            If you're excited about shaping the future of brain-computer interfaces 
            and want to help unlock human potential through technology, we'd love to hear from you.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 1.5 }}
        >
          <JobTable />
        </motion.div>
      </motion.div>
    </section>
  )
}