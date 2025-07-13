'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import AnimatedText from '@/components/ui/AnimatedText'

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
      icon: '💬',
      responseTime: '24-48 hours'
    },
    {
      title: 'Technical Support',
      email: 'support@neurascale.org',
      description: 'Platform issues, integration help, and technical documentation questions',
      icon: '🔧',
      responseTime: '12-24 hours'
    },
    {
      title: 'Sales & Partnerships',
      email: 'sales@neurascale.org',
      description: 'Enterprise solutions, custom deployments, and strategic partnerships',
      icon: '🤝',
      responseTime: '4-8 hours'
    },
    {
      title: 'Research Collaboration',
      email: 'research@neurascale.org',
      description: 'Academic partnerships, clinical trials, and research data sharing',
      icon: '🔬',
      responseTime: '24-48 hours'
    }
  ]

  const socialLinks = [
    {
      platform: 'LinkedIn',
      url: 'linkedin.com/company/neurascale',
      description: 'Professional updates and industry insights',
      icon: '💼'
    },
    {
      platform: 'Twitter/X',
      url: '@neurascale',
      description: 'Real-time updates and community discussions',
      icon: '🐦'
    },
    {
      platform: 'GitHub',
      url: 'github.com/neurascale',
      description: 'Open source repositories and code contributions',
      icon: '📁'
    },
    {
      platform: 'Discord',
      url: 'discord.gg/neurascale',
      description: 'Community chat and developer support',
      icon: '💬'
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
    <section ref={containerRef} className="min-h-screen px-6 md:px-12 lg:px-24 py-24 relative">
      <motion.div style={{ scale }} className="relative z-10">
        <AnimatedText
          text="Let's unlock human potential together"
          className="text-3xl md:text-4xl lg:text-5xl font-light mb-16 max-w-4xl"
        />
        
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
          className="text-lg md:text-xl text-white/80 mb-20 max-w-4xl"
        >
          Whether you're a healthcare provider, researcher, developer, or someone interested in neural interface technology, 
          we'd love to hear from you. Reach out to explore how NEURASCALE can advance your work.
        </motion.p>

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
                    <span className="text-lg mr-2">{channel.icon}</span>
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