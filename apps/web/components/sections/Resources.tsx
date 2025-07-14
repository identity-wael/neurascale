'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'

// SVG Icons for resources
const RocketIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 6 L24 14 L32 16 L26 22 L20 34 L14 22 L8 16 L16 14 Z" 
          stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <circle cx="20" cy="16" r="2" fill="currentColor" opacity="0.8" />
    <path d="M12 24 L16 28" stroke="currentColor" strokeWidth="1" opacity="0.6" />
    <path d="M24 28 L28 24" stroke="currentColor" strokeWidth="1" opacity="0.6" />
    <path d="M18 32 L22 32" stroke="currentColor" strokeWidth="2" opacity="0.6" />
  </svg>
)

const BookIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="10" y="8" width="20" height="26" rx="2" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <path d="M14 14 L26 14" stroke="currentColor" strokeWidth="0.5" opacity="0.6" />
    <path d="M14 18 L26 18" stroke="currentColor" strokeWidth="0.5" opacity="0.6" />
    <path d="M14 22 L22 22" stroke="currentColor" strokeWidth="0.5" opacity="0.6" />
    <path d="M14 26 L24 26" stroke="currentColor" strokeWidth="0.5" opacity="0.6" />
    <path d="M20 8 L20 34" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
  </svg>
)

const DeveloperIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="5" y="8" width="30" height="24" rx="2" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <path d="M12 16 L8 20 L12 24" stroke="currentColor" strokeWidth="1.5" fill="none" />
    <path d="M28 16 L32 20 L28 24" stroke="currentColor" strokeWidth="1.5" fill="none" />
    <path d="M22 14 L18 26" stroke="currentColor" strokeWidth="1" opacity="0.8" />
  </svg>
)

const ManualIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 6 L28 6 L32 10 L32 34 L12 34 Z" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <path d="M28 6 L28 10 L32 10" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <path d="M16 16 L28 16" stroke="currentColor" strokeWidth="0.5" opacity="0.8" />
    <path d="M16 20 L28 20" stroke="currentColor" strokeWidth="0.5" opacity="0.8" />
    <path d="M16 24 L24 24" stroke="currentColor" strokeWidth="0.5" opacity="0.8" />
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


export default function Resources() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'center center'],
  })

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1])

  const documentationSections = [
    {
      title: 'Getting Started',
      description: 'Quick setup guides, installation instructions, and your first neural interface application.',
      icon: <RocketIcon />,
      resources: ['Quick Start Guide', 'Installation Manual', 'First Project Tutorial', 'System Requirements']
    },
    {
      title: 'API Reference',
      description: 'Comprehensive documentation for all NEURASCALE APIs, endpoints, and integration methods.',
      icon: <BookIcon />,
      resources: ['REST API Docs', 'WebSocket Interfaces', 'Neural Data Formats', 'SDK Documentation']
    },
    {
      title: 'Developer Guides',
      description: 'In-depth tutorials for building neural interface applications and integrating with existing systems.',
      icon: <DeveloperIcon />,
      resources: ['Architecture Overview', 'Integration Patterns', 'Best Practices', 'Performance Optimization']
    },
    {
      title: 'User Manuals',
      description: 'End-user documentation for healthcare providers, researchers, and system administrators.',
      icon: <ManualIcon />,
      resources: ['User Interface Guide', 'Patient Monitoring', 'System Administration', 'Troubleshooting']
    }
  ]


  const whitepapers = [
    {
      title: 'Demonstration of a portable intracortical brain-computer interface',
      authors: 'J.D. Collinger, R.A. Gaunt, J.E. Downey, S.M. Flesher, J.L. Weiss, J.L. Foldes, E.C. Tyler-Kabara, A.B. Wodlinger, M.L. Boninger, D.J. Weber, R. Franklin, et al.',
      summary: 'Development and testing of a self-contained, portable intracortical BCI weighing 1.5 kg, enabling users with paralysis to perform computer tasks outside laboratory settings.',
      category: 'BCI / Computing',
      pages: '16 pages',
      date: '2019',
      url: 'https://www.researchgate.net/publication/338341319_Demonstration_of_a_portable_intracortical_brain-computer_interface'
    },
    {
      title: 'Fault-tolerant and Transactional Stateful Serverless Workflows',
      authors: 'H. Zhang, A. Cardoza, P.B. Chen, S. Angel, V. Liu',
      summary: 'Beldi, a library and runtime system for writing fault-tolerant and transactional stateful serverless functions with strong consistency guarantees on AWS Lambda.',
      category: 'Cloud Computing / Computing',
      pages: '16 pages',
      date: '2020',
      url: 'https://www.researchgate.net/publication/344663207_Fault-tolerant_and_Transactional_Stateful_Serverless_Workflows_extended_version'
    }
  ]

  const externalReferences = [
    {
      title: 'NVIDIA Holoscan Platform',
      description: 'High-performance computing platform for AI applications in healthcare and life sciences',
      url: 'developer.nvidia.com/holoscan',
      category: 'Platform'
    },
    {
      title: 'DGX Cloud Infrastructure',
      description: 'Cloud-native AI supercomputing for training and inference at scale',
      url: 'nvidia.com/en-us/data-center/dgx-cloud',
      category: 'Infrastructure'
    },
    {
      title: 'AWS IoT Core Documentation',
      description: 'Managed cloud service for IoT device connectivity and data processing',
      url: 'docs.aws.amazon.com/iot',
      category: 'IoT Integration'
    },
    {
      title: 'Robot Operating System (ROS)',
      description: 'Open-source robotics middleware suite for robot application development',
      url: 'ros.org',
      category: 'Robotics'
    }
  ]

  return (
    <section id="resources" ref={containerRef} className="px-6 py-16 relative">
      <motion.div
        style={{ scale }}
        className="relative z-10 w-full"
      >
        <div className="flex items-start mb-8">
          <span className="text-white/40 text-sm font-mono mr-4">≡</span>
          <span className="text-white/40 text-sm uppercase tracking-wider">RESOURCES</span>
        </div>

        <AnimatedText
          text="Knowledge hub for neural interface innovation"
          className="text-4xl md:text-5xl lg:text-6xl font-light mb-6"
          stagger={0.02}
        />
        
        <motion.p
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          viewport={{ once: true }}
          className="text-white/70 text-lg max-w-4xl mb-16"
        >
          Access comprehensive documentation, research papers, tutorials, and community resources 
          to accelerate your neural interface development and stay current with the latest innovations.
        </motion.p>

        {/* Documentation */}
        <div className="mb-24">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            Documentation
          </motion.h3>
          
          <div className="grid lg:grid-cols-2 gap-8">
            {documentationSections.map((section, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
              >
                <div className="flex items-center mb-4">
                  <div className="text-white/60 mr-3">{section.icon}</div>
                  <h4 className="text-lg font-light text-white/90">{section.title}</h4>
                </div>
                
                <p className="text-white/70 text-sm mb-4 leading-relaxed">
                  {section.description}
                </p>
                
                <div>
                  <span className="text-blue-400/80 text-xs font-medium block mb-2">Available Resources</span>
                  <ul className="space-y-1">
                    {section.resources.map((resource, resourceIndex) => (
                      <li key={resourceIndex} className="text-white/60 text-sm flex items-center">
                        <span className="text-blue-400 mr-2">•</span>
                        {resource}
                      </li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            ))}
          </div>
        </div>


        {/* Whitepapers & Research */}
        <div className="mb-24">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            Whitepapers & Research
          </motion.h3>
          
          <div className="space-y-6">
            {whitepapers.map((paper, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
              >
                <div className="flex flex-col lg:flex-row lg:items-start justify-between mb-4">
                  <div className="flex-1">
                    <h4 className="text-lg font-light text-white/90 mb-2">{paper.title}</h4>
                    <p className="text-blue-400/80 text-sm mb-3">{paper.authors}</p>
                    <p className="text-white/70 text-sm leading-relaxed">{paper.summary}</p>
                  </div>
                  <div className="lg:ml-6 mt-4 lg:mt-0 text-right">
                    <div className="space-y-2">
                      <div>
                        <span className="text-green-400 text-xs font-medium">{paper.category}</span>
                      </div>
                      <div>
                        <span className="text-white/60 text-xs">{paper.pages}</span>
                      </div>
                      <div>
                        <span className="text-white/60 text-xs">{paper.date}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                {paper.url && (
                  <a 
                    href={paper.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-block px-4 py-2 border border-blue-400/30 text-blue-400 hover:bg-blue-400/10 rounded-lg text-sm transition-colors"
                  >
                    Download PDF
                  </a>
                )}
              </motion.div>
            ))}
          </div>
        </div>

        {/* External References */}
        <div className="mb-20">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            External References
          </motion.h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            {externalReferences.map((ref, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm hover:border-white/20 transition-colors cursor-pointer"
              >
                <div className="flex justify-between items-start mb-3">
                  <h4 className="text-lg font-light text-white/90">{ref.title}</h4>
                  <span className="text-purple-400 text-xs font-medium">{ref.category}</span>
                </div>
                
                <p className="text-white/70 text-sm mb-3 leading-relaxed">
                  {ref.description}
                </p>
                
                <div className="text-blue-400/80 text-xs font-mono">
                  {ref.url}
                </div>
              </motion.div>
            ))}
          </div>
        </div>

      </motion.div>
    </section>
  )
}