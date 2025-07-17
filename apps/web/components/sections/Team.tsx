'use client';

import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import AnimatedText from '@/components/ui/AnimatedText';
export default function Team() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'end start'],
  });

  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0]);
  const y = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [100, 0, 0, -100]);

  const teamMembers = [
    {
      name: 'Wael El Ghazzawi',
      role: 'CTO, Financial Technology',
      company: 'Brain Finance',
      expertise: 'ML/AI',
      bio: 'Visionary technologist specializing in machine learning and artificial intelligence applications in financial systems.',
    },
    {
      name: 'Ron Lehman',
      role: 'CEO, Geographic Information System',
      company: 'RYKER',
      expertise: 'Data',
      bio: 'Data systems architect with deep expertise in geographic information systems and large-scale data processing.',
    },
    {
      name: 'Donald Woodruff',
      role: 'Director of Technology, Cloud Solutions',
      company: 'Lumen Technologies',
      expertise: 'Cloud',
      bio: 'Cloud infrastructure specialist with proven track record in enterprise-scale technology deployments and architecture.',
    },
    {
      name: 'Jason Franklin',
      role: 'CITO, E-Retail',
      company: 'American Furniture Warehouse',
      expertise: 'IT Sys',
      bio: 'Information technology leader with extensive experience in e-commerce systems and enterprise technology management.',
    },
    {
      name: 'Vincent Liu',
      role: 'VP Engineering',
      company: 'Curae Soft Inc',
      expertise: 'AI',
      bio: 'Engineering executive with deep expertise in artificial intelligence and software development for healthcare applications.',
    },
  ];

  const getExpertiseColor = (expertise: string) => {
    switch (expertise) {
      case 'BCI':
        return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30';
      case 'ML/AI':
        return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      case 'Data':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'Cloud':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'IT Sys':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'AI':
        return 'bg-pink-500/20 text-pink-400 border-pink-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <section
      id="team"
      ref={containerRef}
      className="px-4 sm:px-6 md:px-12 lg:px-24 py-8 md:py-12 lg:py-16 relative"
    >
      <motion.div style={{ opacity, y }} className="relative z-10 w-full">
        <div className="flex items-start mb-8">
          <span className="text-white/40 text-sm font-mono mr-4">≡</span>
          <span className="text-white/40 text-sm uppercase tracking-wider">TEAM</span>
        </div>

        <AnimatedText
          text="Meet the Team"
          className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-light mb-4 md:mb-6"
          stagger={0.02}
        />

        <motion.p
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          viewport={{ once: true }}
          className="text-white/70 text-base md:text-lg max-w-4xl mb-8 md:mb-12 lg:mb-16"
        >
          Our multidisciplinary team brings together decades of experience in brain-computer
          interfaces, artificial intelligence, cloud computing, and data systems. Each member
          contributes unique expertise to advance the frontiers of neural technology and
          human-machine integration.
        </motion.p>

        {/* Team Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6 lg:gap-8">
          {teamMembers.map((member, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.8,
                delay: index * 0.1 + 0.4,
              }}
              viewport={{ once: true }}
              className="group"
            >
              <div
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 sm:p-5 md:p-6 h-full
                            hover:bg-white/10 transition-all duration-500 hover:border-white/20
                            hover:shadow-xl hover:shadow-blue-500/10"
              >
                {/* Expertise Badge */}
                <div className="flex justify-between items-start mb-4">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium border ${getExpertiseColor(
                      member.expertise
                    )}`}
                  >
                    {member.expertise}
                  </span>
                </div>

                {/* Name and Role */}
                <h3 className="text-xl font-light text-white/90 mb-2 group-hover:text-white transition-colors">
                  {member.name}
                </h3>

                <div className="text-blue-400 text-sm mb-1 font-medium">{member.role}</div>

                <div className="text-white/60 text-sm mb-4">{member.company}</div>

                {/* Bio */}
                <p className="text-white/70 text-sm leading-relaxed">{member.bio}</p>
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
          className="mt-10 md:mt-16 lg:mt-20 text-center"
        >
          <div className="max-w-4xl mx-auto px-4 sm:px-6">
            <h3 className="text-xl sm:text-2xl md:text-3xl font-light text-white/90 mb-4 md:mb-6">
              Our Mission
            </h3>
            <p className="text-white/70 text-base md:text-lg leading-relaxed">
              We are united by a shared vision to revolutionize human potential through advanced
              neural interfaces. Our diverse backgrounds in neurotechnology, artificial
              intelligence, and enterprise systems enable us to tackle the most complex challenges
              in brain-computer interface development, creating solutions that will transform how
              humans interact with technology and each other.
            </p>
          </div>
        </motion.div>
      </motion.div>
    </section>
  );
}
