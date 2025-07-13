'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'

// SVG Icons for contact channels
const ChatIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="6" y="12" width="28" height="16" rx="4" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <circle cx="15" cy="18" r="2" fill="currentColor" opacity="0.8" />
    <circle cx="25" cy="18" r="2" fill="currentColor" opacity="0.8" />
    <path d="M12 24 Q15 26 20 26 Q25 26 28 24" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <path d="M10 16 L6 12" stroke="currentColor" strokeWidth="1" opacity="0.4" />
    <path d="M30 16 L34 12" stroke="currentColor" strokeWidth="1" opacity="0.4" />
  </svg>
)

const SupportIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="8" y="12" width="24" height="16" rx="2" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <circle cx="12" cy="16" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="16" cy="16" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="20" cy="16" r="1.5" fill="currentColor" opacity="0.8" />
    <path d="M10 20 L30 20" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
    <path d="M10 24 L30 24" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
  </svg>
)

const HandshakeIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="15" cy="12" r="4" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <circle cx="25" cy="12" r="4" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <path d="M8 28 C8 24, 11 20, 15 20 C19 20, 22 24, 22 28" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <path d="M18 28 C18 24, 21 20, 25 20 C29 20, 32 24, 32 28" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
  </svg>
)

const ResearchContactIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="20" cy="15" r="8" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <path d="M26 21 L32 27" stroke="currentColor" strokeWidth="2" opacity="0.8" />
    <circle cx="20" cy="15" r="4" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6" />
    <path d="M28 29 L32 33" stroke="currentColor" strokeWidth="1.5" opacity="0.6" />
  </svg>
)

// Real social media brand icons adjusted for black/white theme
const LinkedInIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="6" y="6" width="28" height="28" rx="4" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <circle cx="14" cy="14" r="2" fill="currentColor" opacity="0.8" />
    <rect x="12" y="18" width="4" height="12" fill="currentColor" opacity="0.8" />
    <path d="M20 18 C20 18, 20 18, 22 18 C24 18, 26 19, 26 22 L26 30 L22 30 L22 22 C22 21, 21 20, 20 20" 
          stroke="currentColor" strokeWidth="1" fill="currentColor" opacity="0.8" />
    <rect x="18" y="18" width="4" height="12" fill="currentColor" opacity="0.8" />
  </svg>
)

const TwitterIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M32 10 C30 11, 28 11, 26 11 C24 9, 21 9, 19 11 C17 13, 17 16, 19 18 L8 18 C8 16, 10 14, 12 14 C8 14, 6 12, 6 10 C10 10, 14 12, 16 14 C18 10, 22 8, 26 10 C28 8, 30 8, 32 10 Z" 
          stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <path d="M19 18 C19 20, 20 22, 22 24 C24 26, 27 27, 30 26" 
          stroke="currentColor" strokeWidth="1.5" fill="none" opacity="0.8" />
  </svg>
)

const GitHubBrandIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="20" cy="20" r="14" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <path d="M20 8 C13 8, 8 13, 8 20 C8 25, 11 29, 15 31 C16 31, 16 30, 16 29 L16 27 C12 28, 11 25, 11 25 C10 24, 9 23, 9 23 C8 22, 10 22, 10 22 C11 22, 12 23, 12 23 C13 25, 15 24, 16 24 C16 23, 17 22, 17 22 C13 21, 10 20, 10 16 C10 14, 11 13, 12 12 C11 11, 10 9, 12 8 C12 8, 14 8, 16 10 C17 9, 19 9, 20 9 C21 9, 23 9, 24 10 C26 8, 28 8, 28 8 C30 9, 29 11, 28 12 C29 13, 30 14, 30 16 C30 20, 27 21, 23 22 C23 22, 24 23, 24 24 L24 29 C24 30, 24 31, 25 31 C29 29, 32 25, 32 20 C32 13, 27 8, 20 8 Z" 
          stroke="currentColor" strokeWidth="0.5" fill="none" opacity="0.6" />
  </svg>
)

const DiscordBrandIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M28 10 C26 9, 24 8, 22 8 C22 8, 22 9, 22 10 C20 10, 20 10, 18 10 C18 9, 18 8, 18 8 C16 8, 14 9, 12 10 C10 15, 9 20, 10 25 C12 27, 15 28, 18 28 C18 28, 19 27, 20 26 C18 26, 17 25, 16 24 C17 24, 18 25, 20 25 C22 25, 23 24, 24 24 C23 25, 22 26, 20 26 C21 27, 22 28, 22 28 C25 28, 28 27, 30 25 C31 20, 30 15, 28 10 Z" 
          stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8" />
    <circle cx="16" cy="18" r="1.5" fill="currentColor" opacity="0.8" />
    <circle cx="24" cy="18" r="1.5" fill="currentColor" opacity="0.8" />
  </svg>
)

export default function Contact() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'center center'],
  })

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1])

  const contactChannels = [
    {
      title: 'General Inquiries',
      email: 'hello@neurascale.org',
      description: 'Questions about NEURASCALE, partnership opportunities, or general information',
      icon: <ChatIcon />,
      responseTime: '24-48 hours'
    },
    {
      title: 'Technical Support',
      email: 'support@neurascale.org',
      description: 'Platform issues, integration help, and technical documentation questions',
      icon: <SupportIcon />,
      responseTime: '12-24 hours'
    },
    {
      title: 'Sales & Partnerships',
      email: 'sales@neurascale.org',
      description: 'Enterprise solutions, custom deployments, and strategic partnerships',
      icon: <HandshakeIcon />,
      responseTime: '4-8 hours'
    },
    {
      title: 'Research Collaboration',
      email: 'research@neurascale.org',
      description: 'Academic partnerships, clinical trials, and research data sharing',
      icon: <ResearchContactIcon />,
      responseTime: '24-48 hours'
    }
  ]

  const socialLinks = [
    {
      platform: 'LinkedIn',
      url: 'linkedin.com/company/neurascale',
      description: 'Professional updates and industry insights',
      icon: <LinkedInIcon />
    },
    {
      platform: 'Twitter/X',
      url: '@neurascale',
      description: 'Real-time updates and community discussions',
      icon: <TwitterIcon />
    },
    {
      platform: 'GitHub',
      url: 'github.com/neurascale',
      description: 'Open source repositories and code contributions',
      icon: <GitHubBrandIcon />
    },
    {
      platform: 'Discord',
      url: 'discord.gg/neurascale',
      description: 'Community chat and developer support',
      icon: <DiscordBrandIcon />
    }
  ]

  const officeLocations = [
    {
      city: 'San Francisco',
      address: '123 Neural Avenue, Suite 400\nSan Francisco, CA 94103',
      type: 'Headquarters',
      focus: 'Research & Development'
    },
    {
      city: 'Boston',
      address: '456 Medical Center Drive\nBoston, MA 02115',
      type: 'Clinical Research',
      focus: 'Healthcare Partnerships'
    },
    {
      city: 'Austin',
      address: '789 Innovation Boulevard\nAustin, TX 78701',
      type: 'Engineering Hub',
      focus: 'Platform Development'
    }
  ]

  return (
    <section id="contact" ref={containerRef} className="min-h-screen px-6 md:px-12 lg:px-24 py-24 relative">
      <motion.div style={{ scale }} className="relative z-10">
        

        {/* Contact Form */}
        <div className="grid lg:grid-cols-3 gap-12 mb-24">
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="p-8 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
            >
              <h3 className="text-2xl font-light text-white/90 mb-6">Send us a message</h3>
              
              <form className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-white/70 text-sm mb-2">Name</label>
                    <input 
                      type="text" 
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-blue-400"
                      placeholder="Your full name"
                    />
                  </div>
                  <div>
                    <label className="block text-white/70 text-sm mb-2">Email</label>
                    <input 
                      type="email" 
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-blue-400"
                      placeholder="your.email@example.com"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-white/70 text-sm mb-2">Organization</label>
                  <input 
                    type="text" 
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-blue-400"
                    placeholder="Your company or institution"
                  />
                </div>
                
                <div>
                  <label className="block text-white/70 text-sm mb-2">Subject</label>
                  <select className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-blue-400">
                    <option value="" className="bg-black">Select a topic</option>
                    <option value="general" className="bg-black">General Inquiry</option>
                    <option value="partnership" className="bg-black">Partnership Opportunity</option>
                    <option value="demo" className="bg-black">Request Demo</option>
                    <option value="research" className="bg-black">Research Collaboration</option>
                    <option value="support" className="bg-black">Technical Support</option>
                    <option value="press" className="bg-black">Press & Media</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-white/70 text-sm mb-2">Message</label>
                  <textarea 
                    rows={6}
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-blue-400 resize-vertical"
                    placeholder="Tell us about your project, questions, or how we can help..."
                  />
                </div>
                
                <button 
                  type="submit"
                  className="w-full py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors font-medium"
                >
                  Send Message
                </button>
              </form>
            </motion.div>
          </div>
          
          {/* Contact Channels */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              viewport={{ once: true }}
              className="space-y-6"
            >
              <h3 className="text-xl font-light text-white/90 mb-6">Direct Contact</h3>
              
              {contactChannels.map((channel, index) => (
                <div
                  key={index}
                  className="p-4 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
                >
                  <div className="flex items-center mb-2">
                    <div className="text-white/60 mr-2">{channel.icon}</div>
                    <h4 className="text-white/90 font-medium">{channel.title}</h4>
                  </div>
                  <p className="text-blue-400 text-sm mb-2">{channel.email}</p>
                  <p className="text-white/60 text-xs mb-2">{channel.description}</p>
                  <p className="text-green-400 text-xs">Response: {channel.responseTime}</p>
                </div>
              ))}
            </motion.div>
          </div>
        </div>

        {/* Social Media & Community */}
        <div className="mb-24">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            Connect with our Community
          </motion.h3>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {socialLinks.map((social, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm text-center hover:border-white/20 transition-colors cursor-pointer"
              >
                <span className="text-3xl mb-3 block">{social.icon}</span>
                <h4 className="text-lg font-light text-white/90 mb-2">{social.platform}</h4>
                <p className="text-white/60 text-sm mb-3">{social.description}</p>
                <div className="text-blue-400 text-xs font-mono">{social.url}</div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Office Locations */}
        <div className="mb-20">
          <motion.h3
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-2xl md:text-3xl font-light mb-12 text-white/90"
          >
            Our Locations
          </motion.h3>
          
          <div className="grid lg:grid-cols-3 gap-8">
            {officeLocations.map((location, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="p-6 rounded-lg border border-white/10 bg-white/5 backdrop-blur-sm"
              >
                <div className="flex justify-between items-start mb-4">
                  <h4 className="text-lg font-light text-white/90">{location.city}</h4>
                  <span className="text-purple-400 text-xs font-medium">{location.type}</span>
                </div>
                
                <div className="text-white/60 text-sm mb-4 whitespace-pre-line">
                  {location.address}
                </div>
                
                <div>
                  <span className="text-blue-400/80 text-xs font-medium">Focus Area</span>
                  <p className="text-white/60 text-xs">{location.focus}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Footer CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center p-8 rounded-lg border border-green-400/30 bg-green-400/5 backdrop-blur-sm"
        >
          <h3 className="text-2xl font-light text-white/90 mb-4">Ready to Get Started?</h3>
          <p className="text-white/70 mb-6 max-w-2xl mx-auto">
            Join the neural interface revolution. Whether you want to integrate NEURASCALE into your 
            healthcare practice, contribute to open-source development, or explore research partnerships, 
            we're here to help make it happen.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors">
              Schedule a Demo
            </button>
            <button className="px-6 py-3 border border-white/20 text-white/90 hover:bg-white/10 rounded-lg transition-colors">
              Explore Documentation
            </button>
          </div>
        </motion.div>
      </motion.div>
    </section>
  )
}