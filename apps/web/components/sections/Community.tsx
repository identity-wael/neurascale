'use client';

import { motion, useScroll, useTransform } from 'framer-motion';
import { useRef } from 'react';
import AnimatedText from '@/components/ui/AnimatedText';

// SVG Icons matching the style from the screenshots
const CodeIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect
      x="5"
      y="8"
      width="30"
      height="24"
      rx="2"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.6"
    />
    <path d="M12 16 L8 20 L12 24" stroke="currentColor" strokeWidth="1.5" fill="none" />
    <path d="M28 16 L32 20 L28 24" stroke="currentColor" strokeWidth="1.5" fill="none" />
    <path d="M22 14 L18 26" stroke="currentColor" strokeWidth="1" opacity="0.8" />
  </svg>
);

const HardwareIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect
      x="8"
      y="12"
      width="24"
      height="16"
      rx="2"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.6"
    />
    <circle cx="12" cy="16" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="16" cy="16" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="20" cy="16" r="1.5" fill="currentColor" opacity="0.8" />
    <path d="M10 20 L30 20" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
    <path d="M10 24 L30 24" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
  </svg>
);

const BrainIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M12 20 C12 12, 20 8, 28 12 C32 14, 32 18, 30 22 C28 26, 24 28, 20 26 C16 24, 12 22, 12 20 Z"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.8"
    />
    <circle cx="18" cy="18" r="1" fill="currentColor" />
    <circle cx="24" cy="16" r="1" fill="currentColor" />
    <circle cx="22" cy="22" r="1" fill="currentColor" />
    <path
      d="M15 22 Q18 24 21 22"
      stroke="currentColor"
      strokeWidth="0.5"
      fill="none"
      opacity="0.6"
    />
  </svg>
);

const DocumentIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M12 6 L28 6 L32 10 L32 34 L12 34 Z"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.6"
    />
    <path d="M28 6 L28 10 L32 10" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <path d="M16 16 L28 16" stroke="currentColor" strokeWidth="0.5" opacity="0.8" />
    <path d="M16 20 L28 20" stroke="currentColor" strokeWidth="0.5" opacity="0.8" />
    <path d="M16 24 L24 24" stroke="currentColor" strokeWidth="0.5" opacity="0.8" />
  </svg>
);

const DesignIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect
      x="8"
      y="8"
      width="24"
      height="18"
      rx="2"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.6"
    />
    <circle cx="20" cy="17" r="3" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <path d="M8 28 L16 20 L24 28" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <circle cx="14" cy="14" r="1.5" fill="currentColor" opacity="0.8" />
    <path d="M8 32 L32 32" stroke="currentColor" strokeWidth="2" opacity="0.4" />
  </svg>
);

const SecurityIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M20 6 L28 10 L28 20 C28 26, 24 30, 20 32 C16 30, 12 26, 12 20 L12 10 Z"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.8"
    />
    <circle cx="20" cy="18" r="3" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <rect
      x="18"
      y="20"
      width="4"
      height="6"
      rx="1"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.6"
    />
  </svg>
);

const TransparencyIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle
      cx="20"
      cy="20"
      r="12"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.6"
    />
    <circle cx="20" cy="20" r="8" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <circle cx="20" cy="20" r="4" fill="currentColor" opacity="0.8" />
    <path d="M8 20 L32 20" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
    <path d="M20 8 L20 32" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
  </svg>
);

const CollaborationIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="15" cy="12" r="4" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <circle cx="25" cy="12" r="4" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <path
      d="M8 28 C8 24, 11 20, 15 20 C19 20, 22 24, 22 28"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.6"
    />
    <path
      d="M18 28 C18 24, 21 20, 25 20 C29 20, 32 24, 32 28"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.6"
    />
  </svg>
);

const AccessibilityIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle
      cx="20"
      cy="20"
      r="15"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.6"
    />
    <circle cx="12" cy="16" r="2" fill="currentColor" opacity="0.8" />
    <circle cx="28" cy="16" r="2" fill="currentColor" opacity="0.8" />
    <circle cx="20" cy="24" r="2" fill="currentColor" opacity="0.8" />
    <path
      d="M12 16 L20 24 L28 16"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.4"
    />
  </svg>
);

const InnovationIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="20" cy="18" r="6" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <path d="M16 28 L24 28" stroke="currentColor" strokeWidth="2" opacity="0.6" />
    <path d="M18 32 L22 32" stroke="currentColor" strokeWidth="2" opacity="0.6" />
    <path d="M20 6 L20 12" stroke="currentColor" strokeWidth="1" opacity="0.4" />
    <path d="M12 10 L14 12" stroke="currentColor" strokeWidth="1" opacity="0.4" />
    <path d="M28 10 L26 12" stroke="currentColor" strokeWidth="1" opacity="0.4" />
  </svg>
);

const GitHubIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect
      x="8"
      y="12"
      width="24"
      height="20"
      rx="2"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.6"
    />
    <rect
      x="12"
      y="8"
      width="16"
      height="4"
      rx="1"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.8"
    />
    <path d="M14 18 L26 18" stroke="currentColor" strokeWidth="0.5" opacity="0.6" />
    <path d="M14 22 L26 22" stroke="currentColor" strokeWidth="0.5" opacity="0.6" />
    <path d="M14 26 L22 26" stroke="currentColor" strokeWidth="0.5" opacity="0.6" />
  </svg>
);

const DiscordIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect
      x="6"
      y="12"
      width="28"
      height="16"
      rx="4"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.6"
    />
    <circle cx="15" cy="18" r="2" fill="currentColor" opacity="0.8" />
    <circle cx="25" cy="18" r="2" fill="currentColor" opacity="0.8" />
    <path
      d="M12 24 Q15 26 20 26 Q25 26 28 24"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.6"
    />
    <path d="M10 16 L6 12" stroke="currentColor" strokeWidth="1" opacity="0.4" />
    <path d="M30 16 L34 12" stroke="currentColor" strokeWidth="1" opacity="0.4" />
  </svg>
);

const ForumIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect
      x="8"
      y="10"
      width="20"
      height="14"
      rx="2"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.6"
    />
    <rect
      x="12"
      y="16"
      width="24"
      height="14"
      rx="2"
      stroke="currentColor"
      strokeWidth="1"
      fill="none"
      opacity="0.8"
    />
    <path d="M16 22 L28 22" stroke="currentColor" strokeWidth="0.5" opacity="0.6" />
    <path d="M16 26 L24 26" stroke="currentColor" strokeWidth="0.5" opacity="0.6" />
  </svg>
);

const SlackIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M15 8 L15 15 L8 15"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      opacity="0.8"
    />
    <path
      d="M25 8 L25 15 L32 15"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      opacity="0.8"
    />
    <path
      d="M15 32 L15 25 L8 25"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      opacity="0.8"
    />
    <path
      d="M25 32 L25 25 L32 25"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      opacity="0.8"
    />
    <circle cx="20" cy="20" r="3" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
  </svg>
);

export default function Community() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'center center'],
  });

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1]);

  const contributionAreas = [
    {
      title: 'Core Platform Development',
      description:
        'Contribute to the Neural Management System, NIIL, PICL, and ADAM components with cutting-edge neural processing algorithms.',
      icon: <CodeIcon />,
      skills: ['Python', 'TensorFlow/PyTorch', 'Real-time Systems', 'Neural Networks'],
      difficulty: 'Advanced',
    },
    {
      title: 'Hardware Integration',
      description:
        'Develop drivers and interfaces for neural acquisition devices, prosthetics, and robotic systems.',
      icon: <HardwareIcon />,
      skills: ['C/C++', 'Embedded Systems', 'Device Drivers', 'Robotics'],
      difficulty: 'Expert',
    },
    {
      title: 'AI/ML Model Development',
      description:
        'Create and optimize machine learning models for neural pattern recognition and predictive analytics.',
      icon: <BrainIcon />,
      skills: ['Machine Learning', 'Signal Processing', 'Computer Vision', 'Statistics'],
      difficulty: 'Advanced',
    },
    {
      title: 'Documentation & Testing',
      description:
        'Write comprehensive documentation, create tutorials, and develop testing frameworks for the platform.',
      icon: <DocumentIcon />,
      skills: ['Technical Writing', 'Testing Frameworks', 'API Documentation'],
      difficulty: 'Intermediate',
    },
    {
      title: 'UI/UX Design',
      description:
        'Design intuitive interfaces for neural data visualization, patient monitoring, and system configuration.',
      icon: <DesignIcon />,
      skills: ['React', 'Design Systems', 'Data Visualization', 'Accessibility'],
      difficulty: 'Intermediate',
    },
    {
      title: 'Security & Compliance',
      description:
        'Implement security protocols, ensure HIPAA compliance, and develop neural identity authentication systems.',
      icon: <SecurityIcon />,
      skills: ['Cybersecurity', 'Cryptography', 'Healthcare Compliance', 'Privacy'],
      difficulty: 'Expert',
    },
  ];

  const openSourcePrinciples = [
    {
      principle: 'Transparency',
      description:
        'All core algorithms and system designs are open for review, ensuring trust and scientific rigor in neural interface technology.',
      icon: <TransparencyIcon />,
    },
    {
      principle: 'Collaboration',
      description:
        'Global community of researchers, developers, and healthcare professionals working together to advance the field.',
      icon: <CollaborationIcon />,
    },
    {
      principle: 'Accessibility',
      description:
        'Open standards and free access to core technologies ensure neural interfaces benefit everyone, not just those who can afford proprietary solutions.',
      icon: <AccessibilityIcon />,
    },
    {
      principle: 'Innovation',
      description:
        'Rapid iteration and community-driven development accelerate breakthroughs in neural interface capabilities.',
      icon: <InnovationIcon />,
    },
  ];

  const communityChannels = [
    {
      platform: 'GitHub',
      purpose: 'Code repositories, issue tracking, pull requests',
      link: 'github.com/neurascale',
      members: '2.5K+',
      icon: <GitHubIcon />,
    },
    {
      platform: 'Discord',
      purpose: 'Real-time chat, technical discussions, community support',
      link: 'discord.gg/neurascale',
      members: '5.8K+',
      icon: <DiscordIcon />,
    },
    {
      platform: 'Forum',
      purpose: 'Long-form discussions, research papers, project announcements',
      link: 'community.neurascale.io',
      members: '3.2K+',
      icon: <ForumIcon />,
    },
    {
      platform: 'Slack',
      purpose: 'Developer workspace, working groups, project coordination',
      link: 'neurascale.slack.com',
      members: '1.8K+',
      icon: <SlackIcon />,
    },
  ];

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Beginner':
        return 'text-green-400';
      case 'Intermediate':
        return 'text-yellow-400';
      case 'Advanced':
        return 'text-orange-400';
      case 'Expert':
        return 'text-red-400';
      default:
        return 'text-white/60';
    }
  };

  return (
    <section
      id="community"
      ref={containerRef}
      className="min-h-screen px-6 md:px-12 lg:px-24 py-24 relative"
    >
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
          and healthcare professionals is building the future of human-computer interaction
          together.
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
                  <div className="text-white/60 mr-3">{item.icon}</div>
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
                  <div className="text-white/60 mr-3">{area.icon}</div>
                  <h4 className="text-lg font-light text-white/90">{area.title}</h4>
                </div>

                <p className="text-white/70 text-sm mb-4 leading-relaxed">{area.description}</p>

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
                <div className="text-white/60 mb-3">{channel.icon}</div>
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
              We&apos;re developing a tokenized reward system to recognize and incentivize valuable
              contributions to the NEURASCALE ecosystem. Contributors earn tokens for code commits,
              documentation, bug reports, and community support activities.
            </p>
            <div className="grid md:grid-cols-3 gap-6 text-sm">
              <div>
                <h4 className="text-blue-400/80 font-medium mb-2">Development Rewards</h4>
                <p className="text-white/60">
                  Tokens for merged pull requests, feature implementations, and bug fixes
                </p>
              </div>
              <div>
                <h4 className="text-blue-400/80 font-medium mb-2">Community Support</h4>
                <p className="text-white/60">
                  Recognition for helping other developers and maintaining community standards
                </p>
              </div>
              <div>
                <h4 className="text-blue-400/80 font-medium mb-2">Research Contributions</h4>
                <p className="text-white/60">
                  Rewards for publishing research, sharing datasets, and algorithm improvements
                </p>
              </div>
            </div>
          </motion.div>
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
            of neural interface technology. Every contribution matters in our mission to unlock
            human potential.
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
  );
}
