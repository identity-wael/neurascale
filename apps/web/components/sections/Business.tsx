'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'

// SVG Icons for business models and partnerships
const CloudIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 24 C8 24, 6 20, 8 16 C10 12, 14 12, 16 14 C18 10, 22 10, 26 12 C30 14, 32 18, 30 22 C32 24, 32 28, 28 28 L12 28" 
          stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <circle cx="20" cy="18" r="2" fill="currentColor" opacity="0.6" />
    <path d="M18 22 L22 22" stroke="currentColor" strokeWidth="1" opacity="0.6" />
  </svg>
)

const EnterpriseIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="8" y="12" width="24" height="20" rx="2" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <rect x="14" y="8" width="12" height="4" rx="1" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <path d="M12 18 L28 18" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
    <path d="M12 22 L28 22" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
    <path d="M12 26 L28 26" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
    <rect x="18" y="28" width="4" height="4" rx="1" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
  </svg>
)

const GovernmentIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 6 L32 12 L8 12 Z" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <rect x="10" y="12" width="4" height="16" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <rect x="14" y="12" width="4" height="16" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <rect x="18" y="12" width="4" height="16" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <rect x="22" y="12" width="4" height="16" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <rect x="26" y="12" width="4" height="16" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <path d="M8 28 L32 28" stroke="currentColor" strokeWidth="2" opacity="0.8" />
    <path d="M6 32 L34 32" stroke="currentColor" strokeWidth="2" opacity="0.8" />
  </svg>
)

const ResearchIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="20" cy="15" r="8" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <path d="M26 21 L32 27" stroke="currentColor" strokeWidth="2" opacity="0.8" />
    <circle cx="20" cy="15" r="4" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <path d="M28 29 L32 33" stroke="currentColor" strokeWidth="1.5" opacity="0.6" />
  </svg>
)

const HospitalIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="8" y="10" width="24" height="22" rx="2" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <path d="M20 6 L20 14" stroke="currentColor" strokeWidth="3" opacity="0.8" />
    <path d="M16 10 L24 10" stroke="currentColor" strokeWidth="3" opacity="0.8" />
    <rect x="12" y="16" width="4" height="4" rx="1" stroke="currentColor" strokeWidth="0.5" fill="none" opacity="0.6" />
    <rect x="18" y="16" width="4" height="4" rx="1" stroke="currentColor" strokeWidth="0.5" fill="none" opacity="0.6" />
    <rect x="24" y="16" width="4" height="4" rx="1" stroke="currentColor" strokeWidth="0.5" fill="none" opacity="0.6" />
    <rect x="15" y="24" width="10" height="8" rx="1" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
  </svg>
)

const TechIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="8" y="12" width="24" height="16" rx="2" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <circle cx="12" cy="16" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="16" cy="16" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="20" cy="16" r="1.5" fill="currentColor" opacity="0.8" />
    <path d="M10 20 L30 20" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
    <path d="M10 24 L30 24" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
  </svg>
)

const HardwareIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="20" cy="20" r="8" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <circle cx="20" cy="20" r="4" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <path d="M8 20 L12 20" stroke="currentColor" strokeWidth="2" opacity="0.6" />
    <path d="M28 20 L32 20" stroke="currentColor" strokeWidth="2" opacity="0.6" />
    <path d="M20 8 L20 12" stroke="currentColor" strokeWidth="2" opacity="0.6" />
    <path d="M20 28 L20 32" stroke="currentColor" strokeWidth="2" opacity="0.6" />
    <path d="M13 13 L15 15" stroke="currentColor" strokeWidth="1.5" opacity="0.4" />
    <path d="M25 25 L27 27" stroke="currentColor" strokeWidth="1.5" opacity="0.4" />
  </svg>
)

export default function Business() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'center center'],
  })

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1])

  const businessModel = [
    {
      title: 'Fully Managed Services',
      description: 'Complete SaaS platform with real-time neural processing, AI model hosting, and 24/7 support for healthcare providers and research institutions.',
      icon: <CloudIcon />,
      revenue: 'Subscription-based pricing',
      target: 'Hospitals, Clinics, Research Labs'
    },
    {
      title: 'On-Premise Deployments',
      description: 'Custom installations for organizations requiring local data processing, enhanced security, and specialized integration with existing systems.',
      icon: <EnterpriseIcon />,
      revenue: 'Implementation & licensing fees',
      target: 'Government, Defense, Enterprise'
    },
    {
      title: 'Government Contracts',
      description: 'Large-scale implementations for veteran affairs, defense applications, and public healthcare systems with specialized compliance requirements.',
      icon: <GovernmentIcon />,
      revenue: 'Multi-year contracts',
      target: 'VA, DoD, Public Health Systems'
    }
  ]

  const marketAnalysis = [
    {
      metric: '>20M',
      label: 'People with Paralysis Worldwide',
      description: 'Primary addressable market for mobility restoration'
    },
    {
      metric: '$5.4B',
      label: 'BCI Market by 2030',
      description: 'Expected market size with 15.1% CAGR'
    },
    {
      metric: '650K',
      label: 'Annual Spinal Cord Injuries',
      description: 'Growing need for neural interface solutions'
    }
  ]

  const revenueStreams = [
    {
      stream: 'Platform Subscriptions',
      description: 'Monthly/annual SaaS subscriptions based on data processing volume and feature access',
      percentage: '60%'
    },
    {
      stream: 'Custom Integration',
      description: 'One-time deployment fees and ongoing customization services',
      percentage: '25%'
    },
    {
      stream: 'Support & Consulting',
      description: 'Technical support, training, and consulting services',
      percentage: '15%'
    }
  ]

  const partnershipOpportunities = [
    {
      category: 'Research Institutions',
      partners: ['Universities', 'Medical Centers', 'R&D Labs'],
      value: 'Collaborative research, clinical trials, academic validation',
      icon: <ResearchIcon />
    },
    {
      category: 'Hardware Manufacturers',
      partners: ['Prosthetics Companies', 'Medical Device OEMs', 'Robotics Firms'],
      value: 'Integrated solutions, co-development, market expansion',
      icon: <HardwareIcon />
    },
    {
      category: 'Healthcare Providers',
      partners: ['Hospitals', 'Rehabilitation Centers', 'Specialty Clinics'],
      value: 'Patient care improvement, outcome tracking, clinical deployment',
      icon: <HospitalIcon />
    },
    {
      category: 'Technology Companies',
      partners: ['Cloud Providers', 'AI/ML Platforms', 'IoT Companies'],
      value: 'Infrastructure scaling, technology integration, innovation acceleration',
      icon: <TechIcon />
    }
  ]

  return (
    <section ref={containerRef} className="min-h-screen px-6 md:px-12 lg:px-24 py-24 relative">
      <motion.div style={{ scale }} className="relative z-10">
        <AnimatedText
          text="Building sustainable impact through strategic partnerships"
          className="text-3xl md:text-4xl lg:text-5xl font-light mb-16 max-w-4xl"
        />
        
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
          className="text-lg md:text-xl text-white/80 mb-20 max-w-4xl"
        >
          NEURASCALE follows a proven commercial model similar to Kubernetes, combining open-source innovation 
          with sustainable revenue streams to accelerate neural interface adoption globally.
        </motion.p>

        {/* Business Model */}
        <div className="mb-24">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            Business Model
          </motion.h3>
          
          <div className="grid lg:grid-cols-3 gap-8">
            {businessModel.map((model, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
              >
                <div className="flex items-center mb-4">
                  <div className="text-white/60 mr-3">{model.icon}</div>
                  <h4 className="text-lg font-light text-white/90">{model.title}</h4>
                </div>
                
                <p className="text-white/70 text-sm mb-6 leading-relaxed">
                  {model.description}
                </p>
                
                <div className="space-y-2">
                  <div>
                    <span className="text-blue-400/80 text-xs font-medium">Revenue Model</span>
                    <p className="text-white/60 text-xs">{model.revenue}</p>
                  </div>
                  <div>
                    <span className="text-blue-400/80 text-xs font-medium">Target Market</span>
                    <p className="text-white/60 text-xs">{model.target}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Market Analysis */}
        <div className="mb-24">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            Market Opportunity
          </motion.h3>
          
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            {marketAnalysis.map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
              >
                <div className="text-4xl font-light text-blue-400 mb-2">{item.metric}</div>
                <h4 className="text-lg font-light text-white/90 mb-3">{item.label}</h4>
                <p className="text-white/60 text-sm">{item.description}</p>
              </motion.div>
            ))}
          </div>
          
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="p-6 rounded-lg border border-blue-400/30 bg-blue-400/5 backdrop-blur-sm"
          >
            <p className="text-white/70 leading-relaxed">
              The brain-computer interface market is expanding rapidly beyond medical applications into consumer electronics, 
              gaming, security, and immersive computing. NEURASCALE's open-source approach positions us to capture 
              significant market share across multiple verticals while fostering innovation through community collaboration.
            </p>
          </motion.div>
        </div>

        {/* Revenue Streams */}
        <div className="mb-24">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            Revenue Streams
          </motion.h3>
          
          <div className="space-y-6">
            {revenueStreams.map((stream, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="flex items-center p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
              >
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <h4 className="text-lg font-light text-white/90 mr-4">{stream.stream}</h4>
                    <span className="text-blue-400 font-mono text-sm">{stream.percentage}</span>
                  </div>
                  <p className="text-white/60 text-sm">{stream.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Partnership Opportunities */}
        <div className="mb-20">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            Partnership Opportunities
          </motion.h3>
          
          <div className="grid lg:grid-cols-2 gap-8">
            {partnershipOpportunities.map((opportunity, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
              >
                <div className="flex items-center mb-4">
                  <div className="text-white/60 mr-3">{opportunity.icon}</div>
                  <h4 className="text-lg font-light text-white/90">{opportunity.category}</h4>
                </div>
                
                <div className="mb-4">
                  <span className="text-blue-400/80 text-sm font-medium">Key Partners</span>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {opportunity.partners.map((partner, partnerIndex) => (
                      <span
                        key={partnerIndex}
                        className="px-3 py-1 rounded-full border border-white/20 text-white/70 text-xs bg-white/5"
                      >
                        {partner}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div>
                  <span className="text-blue-400/80 text-sm font-medium">Partnership Value</span>
                  <p className="text-white/60 text-sm mt-1">{opportunity.value}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Call to Action */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center p-8 rounded-lg border border-blue-400/30 bg-blue-400/5 backdrop-blur-sm"
        >
          <h3 className="text-2xl font-light text-white/90 mb-4">Ready to Partner with NEURASCALE?</h3>
          <p className="text-white/70 mb-6 max-w-2xl mx-auto">
            Join us in revolutionizing neural interface technology. Whether you're a healthcare provider, 
            technology company, or research institution, let's explore how we can collaborate to unlock human potential.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors">
              Request Demo
            </button>
            <button className="px-6 py-3 border border-white/20 text-white/90 hover:bg-white/10 rounded-lg transition-colors">
              Contact Sales
            </button>
          </div>
        </motion.div>
      </motion.div>
    </section>
  )
}