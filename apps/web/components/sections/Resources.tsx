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
      title: 'Behavioral Demonstration of a Somatosensory Neuroprosthesis',
      authors: 'S.J. Bensmaia, L.E. Miller, R. Franklin, et al.',
      summary: 'Implementation of a somatosensory prosthesis using intracortical microstimulation to provide graded tactile feedback for prosthetic limb control in Rhesus macaques.',
      category: 'Neuroprosthetics / BCI',
      pages: '8 pages',
      date: '2013',
      url: 'https://www.researchgate.net/publication/235895922_Behavioral_Demonstration_of_a_Somatosensory_Neuroprosthesis'
    },
    {
      title: 'A Comparison of Fabrication Methods for Iridium Oxide Reference Electrodes',
      authors: 'R. Franklin, et al.',
      summary: 'Characterization of SIROF and AIROF fabrication methods for IrOx films used as reference electrodes in neurochemical recordings, establishing AIROF superiority.',
      category: 'Neural Electrodes',
      pages: '4 pages',
      date: '2009',
      url: 'https://www.researchgate.net/publication/224107954_A_Comparison_of_Fabrication_Methods_for_Iridium_Oxide_Reference_Electrodes'
    },
    {
      title: 'Implantable microelectrode arrays for simultaneous electrophysiological and neurochemical recordings',
      authors: 'P.E. Takmakov, K. Zachek, R.B. Keithley, E.A. Bucher, G.S. McCarty, R.M. Wightman, R. Franklin, et al.',
      summary: 'Multi-modal neural recording arrays enabling simultaneous measurement of spikes, field potentials, and dopamine overflow at matching spatiotemporal scales.',
      category: 'Neural Recording',
      pages: '10 pages',
      date: '2008',
      url: 'https://www.researchgate.net/publication/23160768_Implantable_microelectrode_arrays_for_simultaneous_electrophysiological_and_neurochemical_recordings'
    },
    {
      title: 'A wireless transmission neural interface system for unconstrained non-human primates',
      authors: 'D.A. Schwarz, M.A. Lebedev, T.L. Hanson, D.F. Dimitrov, G. Lehew, J. Meloy, S. Rajangam, V. Subramanian, P.J. Ifft, Z. Li, A. Ramakrishnan, A. Tate, K.Z. Zhuang, M.A.L. Nicolelis, R. Franklin, et al.',
      summary: 'High-fidelity 96-channel wireless system for recording neural activity in freely moving primates, revealing behavioral-state dependent neural dynamics.',
      category: 'Wireless BCI',
      pages: '15 pages',
      date: '2015',
      url: 'https://www.researchgate.net/publication/280945213_A_wireless_transmission_neural_interface_system_for_unconstrained_non-human_primates'
    },
    {
      title: 'High channel-count neural interfaces for multiple degree-of-freedom neuroprosthetics',
      authors: 'R. Franklin, et al.',
      summary: 'Advanced neural interface integrating Utah Electrode Arrays with custom ASIC for 200-channel recordings to control 17-DoF prosthetic devices.',
      category: 'Neural Interfaces',
      pages: '2 pages',
      date: '2011',
      url: 'https://www.researchgate.net/publication/271614384_High_channel-count_neural_interfaces_for_multiple_degree-_of-freedom_neuroprosthetics'
    },
    {
      title: 'Analog Circuit Design Methodologies to Improve Negative-Bias Temperature Instability Degradation',
      authors: 'R. Franklin, et al.',
      summary: 'Novel techniques for mitigating NBTI effects in PMOS devices through input switching and body-bias modulation in differential pairs.',
      category: 'Circuit Design',
      pages: '6 pages',
      date: '2010',
      url: 'https://www.researchgate.net/publication/221295849_Analog_Circuit_Design_Methodologies_to_Improve_Negative-Bias_Temperature_Instability_Degradation'
    }
  ]

  const externalReferences = [
    {
      title: 'NVIDIA Holoscan Platform',
      description: 'High-performance computing platform for AI applications in healthcare and life sciences',
      url: 'https://developer.nvidia.com/holoscan-sdk',
      displayUrl: 'developer.nvidia.com/holoscan-sdk',
      category: 'Platform'
    },
    {
      title: 'DGX Cloud Infrastructure',
      description: 'Cloud-native AI supercomputing for training and inference at scale',
      url: 'https://developer.nvidia.com/dgx-cloud',
      displayUrl: 'developer.nvidia.com/dgx-cloud',
      category: 'Infrastructure'
    },
    {
      title: 'AWS IoT Core Documentation',
      description: 'Managed cloud service for IoT device connectivity and data processing',
      url: 'https://aws.amazon.com/iot-core/',
      displayUrl: 'aws.amazon.com/iot-core',
      category: 'IoT Integration'
    },
    {
      title: 'Robot Operating System (ROS)',
      description: 'Open-source robotics middleware suite for robot application development',
      url: 'https://www.ros.org/',
      displayUrl: 'ros.org',
      category: 'Robotics'
    }
  ]

  return (
    <section id="resources" ref={containerRef} className="px-4 sm:px-6 md:px-12 lg:px-24 py-8 md:py-12 lg:py-16 relative">
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
          className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-light mb-4 md:mb-6"
          stagger={0.02}
          as="h2"
        />
        
        <motion.p
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          viewport={{ once: true }}
          className="text-white/70 text-base md:text-lg max-w-4xl mb-8 md:mb-12 lg:mb-16"
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
            className="text-xl sm:text-2xl md:text-3xl font-light mb-6 md:mb-8 lg:mb-12 text-white/90"
          >
            Documentation
          </motion.h3>
          
          <div className="grid lg:grid-cols-2 gap-4 md:gap-6 lg:gap-8">
            {documentationSections.map((section, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-4 sm:p-5 md:p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
              >
                <div className="flex items-center mb-4">
                  <div className="text-white/60 mr-3">{section.icon}</div>
                  <h4 className="text-lg font-light text-white/90">{section.title}</h4>
                </div>
                
                <p className="text-white/70 text-sm mb-4 leading-relaxed">
                  {section.description}
                </p>
                
                <div className="mt-6 p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                  <span className="text-yellow-400 text-sm font-medium flex items-center">
                    <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Coming Soon
                  </span>
                  <p className="text-yellow-400/80 text-xs mt-2">
                    Documentation for {section.title.toLowerCase()} will be available shortly.
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>


        {/* Whitepapers & Research */}
        <div className="mb-12 md:mb-16 lg:mb-24">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-xl sm:text-2xl md:text-3xl font-light mb-6 md:mb-8 lg:mb-12 text-white/90"
          >
            Whitepapers & Research
          </motion.h3>
          
          <div className="space-y-4 md:space-y-6">
            {whitepapers.map((paper, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-4 sm:p-5 md:p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
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
        <div className="mb-10 md:mb-16 lg:mb-20">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-xl sm:text-2xl md:text-3xl font-light mb-6 md:mb-8 lg:mb-12 text-white/90"
          >
            External References
          </motion.h3>
          
          <div className="grid md:grid-cols-2 gap-4 md:gap-6">
            {externalReferences.map((ref, index) => (
              <motion.a
                key={index}
                href={ref.url}
                target="_blank"
                rel="noopener noreferrer"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="block p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm hover:border-white/20 transition-colors cursor-pointer"
              >
                <div className="flex justify-between items-start mb-3">
                  <h4 className="text-lg font-light text-white/90">{ref.title}</h4>
                  <span className="text-purple-400 text-xs font-medium">{ref.category}</span>
                </div>
                
                <p className="text-white/70 text-sm mb-3 leading-relaxed">
                  {ref.description}
                </p>
                
                <div className="text-blue-400/80 text-xs font-mono hover:text-blue-300 transition-colors">
                  {ref.displayUrl || ref.url} →
                </div>
              </motion.a>
            ))}
          </div>
        </div>

      </motion.div>
    </section>
  )
}