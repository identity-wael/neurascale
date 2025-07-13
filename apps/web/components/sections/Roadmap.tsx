'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'

export default function Roadmap() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'center center'],
  })

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1])

  const developmentPhases = [
    {
      phase: 'Phase 1',
      title: 'Foundation & Core Research',
      timeline: 'Q1-Q2 2024',
      status: 'Current',
      objectives: [
        'Establish neural signal processing infrastructure',
        'Develop initial AI/ML models for pattern recognition',
        'Create basic brain-computer interface protocols',
        'Build core team and secure initial funding'
      ],
      funding: 'Bootstrapping through grants and cloud credits'
    },
    {
      phase: 'Phase 2',
      title: 'Platform Development',
      timeline: 'Q3-Q4 2024',
      status: 'In Progress',
      objectives: [
        'Complete Neural Management System architecture',
        'Deploy multi-cloud infrastructure',
        'Implement real-time data processing pipeline',
        'Launch early adopter program'
      ],
      funding: 'Seed funding and government research grants'
    },
    {
      phase: 'Phase 3',
      title: 'Feature Expansion',
      timeline: 'Q1-Q2 2025',
      status: 'Planned',
      objectives: [
        'Expand neural interface capabilities',
        'Integrate advanced robotics control',
        'Deploy immersive VR/XR applications',
        'Commercial pilot programs'
      ],
      funding: 'Series A and enterprise partnerships'
    },
    {
      phase: 'Phase 4',
      title: 'Ecosystem Growth',
      timeline: 'Q3 2025+',
      status: 'Future',
      objectives: [
        'Global platform scaling',
        'Open-source community expansion',
        'Medical device certifications',
        'Consumer market entry'
      ],
      funding: 'Commercial revenue and strategic partnerships'
    }
  ]

  const featuredProjects = [
    {
      title: 'Inverse Kinematics for Prosthetics',
      objective: 'Enable realistic and intuitive control of prosthetic limbs through neural signals with natural movement patterns.',
      status: 'Active Development',
      timeline: 'Q2 2024 - Q1 2025',
      technologies: ['Neural Pattern Recognition', 'Robotics Control', 'Machine Learning'],
      impact: 'Restore natural mobility for amputees',
      icon: '🦾'
    },
    {
      title: 'ROS Integration Platform',
      objective: 'Seamlessly integrate NEURASCALE with Robot Operating System for advanced robotic control across industrial and medical applications.',
      status: 'Prototype Phase',
      timeline: 'Q3 2024 - Q2 2025',
      technologies: ['NVIDIA ROS', 'Real-time Control', 'Multi-robot Systems'],
      impact: 'Enable neural control of robot swarms',
      icon: '🤖'
    },
    {
      title: 'Modular 3D Platform',
      objective: 'Create flexible and extensible platform for immersive VR/XR experiences and neural emulation environments.',
      status: 'Foundational Development',
      timeline: 'Q4 2024 - Q3 2025',
      technologies: ['WebGPU', '3D Neural Visualization', 'Immersive Computing'],
      impact: 'Full-dive VR controlled by thought',
      icon: '🥽'
    },
    {
      title: 'Neural Identity System',
      objective: 'Develop and implement passwordless \"Neural ID\" authentication using unique brain patterns for enhanced security.',
      status: 'Conceptualization',
      timeline: 'Q1 2025 - Q4 2025',
      technologies: ['Biometric Security', 'Neural Signatures', 'Cryptography'],
      impact: 'Unbreakable personal authentication',
      icon: '🧠'
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Current':
      case 'Active Development':
        return 'text-green-400'
      case 'In Progress':
      case 'Prototype Phase':
        return 'text-blue-400'
      case 'Planned':
      case 'Foundational Development':
        return 'text-yellow-400'
      case 'Future':
      case 'Conceptualization':
        return 'text-purple-400'
      default:
        return 'text-white/60'
    }
  }

  return (
    <section ref={containerRef} className="min-h-screen px-6 md:px-12 lg:px-24 py-24 relative">
      <motion.div style={{ scale }} className="relative z-10">
        <AnimatedText
          text="Roadmap to the future of human potential"
          className="text-3xl md:text-4xl lg:text-5xl font-light mb-16 max-w-4xl"
        />
        
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
          className="text-lg md:text-xl text-white/80 mb-20 max-w-4xl"
        >
          Our strategic development phases combine cutting-edge research with practical implementation, 
          building toward a world where neural interfaces unlock unlimited human potential.
        </motion.p>

        {/* Development Phases */}
        <div className="mb-24">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            Development Phases
          </motion.h3>
          
          <div className="space-y-8">
            {developmentPhases.map((phase, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-8 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
              >
                <div className="flex flex-col md:flex-row md:items-start justify-between mb-6">
                  <div>
                    <div className="flex items-center mb-2">
                      <span className="text-blue-400 font-mono text-sm mr-4">{phase.phase}</span>
                      <h4 className="text-xl font-light text-white/90">{phase.title}</h4>
                    </div>
                    <div className="flex items-center space-x-4">
                      <span className="text-white/60 text-sm">{phase.timeline}</span>
                      <span className={`text-sm font-medium ${getStatusColor(phase.status)}`}>
                        {phase.status}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="grid md:grid-cols-2 gap-8">
                  <div>
                    <h5 className="text-white/80 font-medium mb-3">Key Objectives</h5>
                    <ul className="space-y-2">
                      {phase.objectives.map((objective, objIndex) => (
                        <li key={objIndex} className="text-white/60 text-sm flex items-start">
                          <span className="text-blue-400 mr-2 mt-1">•</span>
                          {objective}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h5 className="text-white/80 font-medium mb-3">Funding Strategy</h5>
                    <p className="text-white/60 text-sm">{phase.funding}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Featured Projects */}
        <div className="mb-20">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            Featured Projects
          </motion.h3>
          
          <div className="grid lg:grid-cols-2 gap-8">
            {featuredProjects.map((project, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
              >
                <div className="flex items-center mb-4">
                  <span className="text-2xl mr-3">{project.icon}</span>
                  <h4 className="text-lg font-light text-white/90">{project.title}</h4>
                </div>
                
                <p className="text-white/70 text-sm mb-4 leading-relaxed">
                  {project.objective}
                </p>
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-white/60 text-xs">Status</span>
                    <span className={`text-xs font-medium ${getStatusColor(project.status)}`}>
                      {project.status}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-white/60 text-xs">Timeline</span>
                    <span className="text-white/60 text-xs">{project.timeline}</span>
                  </div>
                  
                  <div>
                    <span className="text-white/60 text-xs block mb-2">Technologies</span>
                    <div className="flex flex-wrap gap-2">
                      {project.technologies.map((tech, techIndex) => (
                        <span
                          key={techIndex}
                          className="px-2 py-1 rounded text-xs bg-blue-400/10 text-blue-400/80 border border-blue-400/20"
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="pt-2 border-t border-white/10">
                    <span className="text-blue-400/80 text-xs font-medium">
                      Impact: {project.impact}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Commercial Strategy */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="p-8 rounded-lg border border-blue-400/30 bg-blue-400/5 backdrop-blur-sm"
        >
          <h3 className="text-xl font-light text-white/90 mb-4">Commercial Viability</h3>
          <p className="text-white/70 leading-relaxed mb-4">
            Following the successful Kubernetes model, NEURASCALE focuses on long-term sustainability through 
            managed services, on-premise deployments, and strategic government partnerships.
          </p>
          <div className="grid md:grid-cols-3 gap-6 text-sm">
            <div>
              <h4 className="text-blue-400/80 font-medium mb-2">Managed Services</h4>
              <p className="text-white/60">SaaS platform subscriptions for healthcare providers and research institutions</p>
            </div>
            <div>
              <h4 className="text-blue-400/80 font-medium mb-2">Enterprise Deployments</h4>
              <p className="text-white/60">Custom on-premise solutions for hospitals and specialized facilities</p>
            </div>
            <div>
              <h4 className="text-blue-400/80 font-medium mb-2">Government Contracts</h4>
              <p className="text-white/60">Large-scale implementations for defense and veteran affairs</p>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </section>
  )
}