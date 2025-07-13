'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef, useState } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'

export default function Team() {
  const containerRef = useRef<HTMLDivElement>(null)
  const [hoveredMember, setHoveredMember] = useState<number | null>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'end start'],
  })

  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0])
  const y = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [100, 0, 0, -100])

  const teamMembers = [
    {
      name: "Rob Franklin",
      role: "SVP, Brain Computer Interface",
      company: "Blackrock Neurotech",
      expertise: "BCI",
      bio: "Leading expert in brain-computer interface technology with extensive experience in neural signal processing and implantable systems.",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face&auto=format&q=80",
      gradient: "from-cyan-500 to-blue-600"
    },
    {
      name: "Wael El Ghazzawi",
      role: "CTO, Financial Technology",
      company: "Brain Finance",
      expertise: "ML/AI",
      bio: "Visionary technologist specializing in machine learning and artificial intelligence applications in financial systems.",
      avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face&auto=format&q=80",
      gradient: "from-purple-500 to-pink-600"
    },
    {
      name: "Ron Lehman",
      role: "CEO, Geographic Information System",
      company: "RYKER",
      expertise: "Data",
      bio: "Data systems architect with deep expertise in geographic information systems and large-scale data processing.",
      avatar: "https://images.unsplash.com/photo-1519244703995-f4e0f30006d5?w=150&h=150&fit=crop&crop=face&auto=format&q=80",
      gradient: "from-blue-500 to-indigo-600"
    },
    {
      name: "Donald Woodruff",
      role: "Director of Technology, Cloud Solutions",
      company: "Lumen Technologies",
      expertise: "Cloud",
      bio: "Cloud infrastructure specialist with proven track record in enterprise-scale technology deployments and architecture.",
      avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face&auto=format&q=80",
      gradient: "from-green-500 to-emerald-600"
    },
    {
      name: "Jason Franklin",
      role: "CITO, E-Retail",
      company: "American Furniture Warehouse",
      expertise: "IT Sys",
      bio: "Information technology leader with extensive experience in e-commerce systems and enterprise technology management.",
      avatar: "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150&h=150&fit=crop&crop=face&auto=format&q=80",
      gradient: "from-orange-500 to-red-600"
    },
    {
      name: "Vincent Liu",
      role: "VP Engineering",
      company: "Curae Soft Inc",
      expertise: "AI",
      bio: "Engineering executive with deep expertise in artificial intelligence and software development for healthcare applications.",
      avatar: "https://images.unsplash.com/photo-1507101105822-7472b28e22ac?w=150&h=150&fit=crop&crop=face&auto=format&q=80",
      gradient: "from-pink-500 to-rose-600"
    }
  ]

  const getExpertiseColor = (expertise: string) => {
    switch (expertise) {
      case 'BCI': return 'from-cyan-400 to-cyan-600'
      case 'ML/AI': return 'from-purple-400 to-purple-600'
      case 'Data': return 'from-blue-400 to-blue-600'
      case 'Cloud': return 'from-green-400 to-green-600'
      case 'IT Sys': return 'from-orange-400 to-orange-600'
      case 'AI': return 'from-pink-400 to-pink-600'
      default: return 'from-gray-400 to-gray-600'
    }
  }

  return (
    <section id="team" ref={containerRef} className="px-6 py-16 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-purple-900/10 to-cyan-900/20" />
      <div className="absolute inset-0">
        {/* Floating orbs */}
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-64 h-64 rounded-full opacity-5"
            style={{
              background: `radial-gradient(circle, ${['#00f5ff', '#8a2be2', '#ff1493', '#00ff00', '#ffa500', '#ff69b4'][i]} 0%, transparent 70%)`,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              x: [0, 30, 0],
              y: [0, -30, 0],
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 10 + i * 2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>

      <motion.div
        style={{ opacity, y }}
        className="relative z-10 w-full"
      >
        <div className="flex items-start mb-8">
          <span className="text-white/40 text-sm font-mono mr-4">≡</span>
          <span className="text-white/40 text-sm uppercase tracking-wider">TEAM</span>
        </div>

        <AnimatedText
          text="Meet the Team"
          className="text-4xl md:text-5xl lg:text-6xl font-light mb-6 bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent"
          stagger={0.02}
        />

        <motion.p
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          viewport={{ once: true }}
          className="text-white/70 text-lg max-w-4xl mb-16"
        >
          Our multidisciplinary team brings together decades of experience in brain-computer interfaces, 
          artificial intelligence, cloud computing, and data systems. Each member contributes unique expertise 
          to advance the frontiers of neural technology and human-machine integration.
        </motion.p>

        {/* Team Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-20">
          {teamMembers.map((member, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ 
                duration: 0.8, 
                delay: index * 0.1 + 0.4
              }}
              viewport={{ once: true }}
              className="group relative"
              onMouseEnter={() => setHoveredMember(index)}
              onMouseLeave={() => setHoveredMember(null)}
            >
              {/* Card */}
              <div className="relative overflow-hidden bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-8 h-full
                            hover:border-white/30 transition-all duration-500 group-hover:bg-black/60
                            group-hover:shadow-2xl group-hover:shadow-blue-500/20 group-hover:scale-[1.02]">
                
                {/* Gradient overlay */}
                <div className={`absolute inset-0 bg-gradient-to-br ${member.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-500`} />
                
                {/* Profile Section */}
                <div className="relative z-10 text-center mb-6">
                  {/* Profile Picture */}
                  <motion.div
                    className="relative inline-block mb-4"
                    animate={{
                      scale: hoveredMember === index ? 1.1 : 1,
                    }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className={`w-24 h-24 rounded-full bg-gradient-to-br ${member.gradient} p-0.5 mx-auto`}>
                      <img
                        src={member.avatar}
                        alt={member.name}
                        className="w-full h-full rounded-full object-cover border-2 border-black/20"
                      />
                    </div>
                    {/* Expertise Badge */}
                    <motion.div
                      className={`absolute -bottom-1 -right-1 w-8 h-8 rounded-full bg-gradient-to-r ${getExpertiseColor(member.expertise)} 
                                 flex items-center justify-center text-xs font-bold text-white shadow-lg`}
                      animate={{
                        rotate: hoveredMember === index ? 360 : 0,
                      }}
                      transition={{ duration: 0.6 }}
                    >
                      {member.expertise === 'ML/AI' ? 'AI' : member.expertise === 'IT Sys' ? 'IT' : member.expertise.slice(0, 2)}
                    </motion.div>
                  </motion.div>

                  {/* Name */}
                  <h3 className="text-xl font-semibold text-white mb-1 group-hover:text-white transition-colors">
                    {member.name}
                  </h3>
                  
                  {/* Role */}
                  <div className={`text-sm font-medium mb-1 bg-gradient-to-r ${getExpertiseColor(member.expertise)} bg-clip-text text-transparent`}>
                    {member.role}
                  </div>
                  
                  {/* Company */}
                  <div className="text-white/60 text-sm mb-4 font-light">
                    {member.company}
                  </div>
                </div>

                {/* Bio */}
                <motion.div
                  className="relative z-10"
                  animate={{
                    opacity: hoveredMember === index ? 1 : 0.8,
                  }}
                  transition={{ duration: 0.3 }}
                >
                  <p className="text-white/70 text-sm leading-relaxed">
                    {member.bio}
                  </p>
                </motion.div>

                {/* Expertise Full Badge */}
                <div className="absolute top-4 right-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r ${getExpertiseColor(member.expertise)} text-white shadow-lg`}>
                    {member.expertise}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Mission Statement */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.8 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <div className="max-w-4xl mx-auto bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-12">
            <div className="w-16 h-16 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-2xl md:text-3xl font-light text-white/90 mb-6 bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
              Our Mission
            </h3>
            <p className="text-white/70 text-lg leading-relaxed">
              We are united by a shared vision to revolutionize human potential through advanced neural interfaces. 
              Our diverse backgrounds in neurotechnology, artificial intelligence, and enterprise systems enable us 
              to tackle the most complex challenges in brain-computer interface development, creating solutions that 
              will transform how humans interact with technology and each other.
            </p>
          </div>
        </motion.div>
      </motion.div>
    </section>
  )
}