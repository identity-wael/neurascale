'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'

export default function Community() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'center center'],
  })

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1])

  const contributionAreas = [
    {
      title: 'Core Platform Development',
      description: 'Contribute to the Neural Management System, NIIL, PICL, and ADAM components with cutting-edge neural processing algorithms.',
      icon: '💻',
      skills: ['Python', 'TensorFlow/PyTorch', 'Real-time Systems', 'Neural Networks'],
      difficulty: 'Advanced'
    },
    {
      title: 'Hardware Integration',
      description: 'Develop drivers and interfaces for neural acquisition devices, prosthetics, and robotic systems.',
      icon: '🔧',
      skills: ['C/C++', 'Embedded Systems', 'Device Drivers', 'Robotics'],
      difficulty: 'Expert'
    },
    {
      title: 'AI/ML Model Development',
      description: 'Create and optimize machine learning models for neural pattern recognition and predictive analytics.',
      icon: '🧠',
      skills: ['Machine Learning', 'Signal Processing', 'Computer Vision', 'Statistics'],
      difficulty: 'Advanced'
    },
    {
      title: 'Documentation & Testing',
      description: 'Write comprehensive documentation, create tutorials, and develop testing frameworks for the platform.',
      icon: '📚',
      skills: ['Technical Writing', 'Testing Frameworks', 'API Documentation'],
      difficulty: 'Intermediate'
    },
    {
      title: 'UI/UX Design',
      description: 'Design intuitive interfaces for neural data visualization, patient monitoring, and system configuration.',
      icon: '🎨',
      skills: ['React', 'Design Systems', 'Data Visualization', 'Accessibility'],
      difficulty: 'Intermediate'
    },
    {
      title: 'Security & Compliance',
      description: 'Implement security protocols, ensure HIPAA compliance, and develop neural identity authentication systems.',
      icon: '🔒',
      skills: ['Cybersecurity', 'Cryptography', 'Healthcare Compliance', 'Privacy'],
      difficulty: 'Expert'
    }
  ]

  const openSourcePrinciples = [
    {
      principle: 'Transparency',
      description: 'All core algorithms and system designs are open for review, ensuring trust and scientific rigor in neural interface technology.',
      icon: '👁️'
    },
    {
      principle: 'Collaboration',
      description: 'Global community of researchers, developers, and healthcare professionals working together to advance the field.',
      icon: '🤝'
    },
    {
      principle: 'Accessibility',
      description: 'Open standards and free access to core technologies ensure neural interfaces benefit everyone, not just those who can afford proprietary solutions.',
      icon: '🌍'
    },
    {
      principle: 'Innovation',
      description: 'Rapid iteration and community-driven development accelerate breakthroughs in neural interface capabilities.',
      icon: '💡'
    }
  ]

  const communityChannels = [
    {
      platform: 'GitHub',
      purpose: 'Code repositories, issue tracking, pull requests',
      link: 'github.com/neurascale',
      members: '2.5K+',
      icon: '📁'
    },
    {
      platform: 'Discord',
      purpose: 'Real-time chat, technical discussions, community support',
      link: 'discord.gg/neurascale',
      members: '5.8K+',
      icon: '💬'
    },
    {
      platform: 'Forum',
      purpose: 'Long-form discussions, research papers, project announcements',
      link: 'community.neurascale.org',
      members: '3.2K+',
      icon: '📋'
    },
    {
      platform: 'Slack',
      purpose: 'Developer workspace, working groups, project coordination',
      link: 'neurascale.slack.com',
      members: '1.8K+',
      icon: '⚡'
    }
  ]

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Beginner':
        return 'text-green-400'
      case 'Intermediate':
        return 'text-yellow-400'
      case 'Advanced':
        return 'text-orange-400'
      case 'Expert':
        return 'text-red-400'
      default:
        return 'text-white/60'
    }
  }

  return (
    <section ref={containerRef} className="min-h-screen px-6 md:px-12 lg:px-24 py-24 relative">
      <motion.div style={{ scale }} className="relative z-10">
        <AnimatedText
          text="Join the neural interface revolution"
          className="text-3xl md:text-4xl lg:text-5xl font-light mb-16 max-w-4xl"
        />
        
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
          className="text-lg md:text-xl text-white/80 mb-20 max-w-4xl"
        >
          NEURASCALE thrives on open collaboration. Our global community of researchers, developers, 
          and healthcare professionals is building the future of human-computer interaction together.
        </motion.p>

        {/* Open Source Philosophy */}
        <div className="mb-24">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            Open-Source Philosophy
          </motion.h3>
          
          <div className="grid md:grid-cols-2 gap-8">
            {openSourcePrinciples.map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
              >
                <div className="flex items-center mb-4">
                  <span className="text-2xl mr-3">{item.icon}</span>
                  <h4 className="text-lg font-light text-white/90">{item.principle}</h4>
                </div>
                <p className="text-white/70 text-sm leading-relaxed">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* How to Contribute */}
        <div className="mb-24">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            How to Contribute
          </motion.h3>
          
          <div className="grid lg:grid-cols-2 xl:grid-cols-3 gap-8">
            {contributionAreas.map((area, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
              >
                <div className="flex items-center mb-4">
                  <span className="text-2xl mr-3">{area.icon}</span>
                  <h4 className="text-lg font-light text-white/90">{area.title}</h4>
                </div>
                
                <p className="text-white/70 text-sm mb-4 leading-relaxed">
                  {area.description}
                </p>
                
                <div className="space-y-3">
                  <div>
                    <span className="text-blue-400/80 text-xs font-medium">Required Skills</span>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {area.skills.map((skill, skillIndex) => (
                        <span
                          key={skillIndex}
                          className="px-2 py-1 rounded text-xs bg-white/10 text-white/70 border border-white/20"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-white/60 text-xs">Difficulty</span>
                    <span className={`text-xs font-medium ${getDifficultyColor(area.difficulty)}`}>
                      {area.difficulty}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Community Channels */}
        <div className="mb-24">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            Community Channels
          </motion.h3>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {communityChannels.map((channel, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm text-center hover:border-white/20 transition-colors cursor-pointer"
              >
                <span className="text-3xl mb-3 block">{channel.icon}</span>
                <h4 className="text-lg font-light text-white/90 mb-2">{channel.platform}</h4>
                <p className="text-white/60 text-sm mb-3">{channel.purpose}</p>
                <div className="text-blue-400/80 text-xs font-mono mb-2">{channel.link}</div>
                <div className="text-green-400 text-sm font-medium">{channel.members} members</div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Tokenized Rewards */}
        <div className="mb-20">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="p-8 rounded-lg border border-blue-400/30 bg-blue-400/5 backdrop-blur-sm"
          >
            <h3 className="text-2xl font-light text-white/90 mb-4">Contributor Recognition</h3>
            <p className="text-white/70 leading-relaxed mb-6">
              We're developing a tokenized reward system to recognize and incentivize valuable contributions 
              to the NEURASCALE ecosystem. Contributors earn tokens for code commits, documentation, 
              bug reports, and community support activities.
            </p>
            <div className="grid md:grid-cols-3 gap-6 text-sm">
              <div>
                <h4 className="text-blue-400/80 font-medium mb-2">Development Rewards</h4>
                <p className="text-white/60">Tokens for merged pull requests, feature implementations, and bug fixes</p>
              </div>
              <div>
                <h4 className="text-blue-400/80 font-medium mb-2">Community Support</h4>
                <p className="text-white/60">Recognition for helping other developers and maintaining community standards</p>
              </div>
              <div>
                <h4 className="text-blue-400/80 font-medium mb-2">Research Contributions</h4>
                <p className="text-white/60">Rewards for publishing research, sharing datasets, and algorithm improvements</p>
              </div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center p-8 rounded-lg border border-green-400/30 bg-green-400/5 backdrop-blur-sm"
        >
          <h3 className="text-2xl font-light text-white/90 mb-4">Ready to Shape the Future?</h3>
          <p className="text-white/70 mb-6 max-w-2xl mx-auto">
            Join thousands of developers, researchers, and innovators building the next generation 
            of neural interface technology. Every contribution matters in our mission to unlock human potential.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors">
              Join Our Community
            </button>
            <button className="px-6 py-3 border border-white/20 text-white/90 hover:bg-white/10 rounded-lg transition-colors">
              Explore Repositories
            </button>
          </div>
        </motion.div>
      </motion.div>
    </section>
  )
}