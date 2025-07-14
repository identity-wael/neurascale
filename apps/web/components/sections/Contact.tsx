'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef, useState } from 'react'

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


export default function Contact() {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'center center'],
  })

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.8, 1])

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    organization: '',
    subject: '',
    message: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [statusMessage, setStatusMessage] = useState('')

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsSubmitting(true)
    setSubmitStatus('idle')

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        setSubmitStatus('success')
        setStatusMessage('Thank you for your message! We\'ll get back to you soon.')
        setFormData({
          name: '',
          email: '',
          organization: '',
          subject: '',
          message: ''
        })
      } else {
        setSubmitStatus('error')
        setStatusMessage('Failed to send message. Please try again.')
      }
    } catch (error) {
      setSubmitStatus('error')
      setStatusMessage('An error occurred. Please try again later.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const contactChannels = [
    {
      title: 'General Inquiries',
      email: 'hello@neurascale.io',
      description: 'Questions about NEURASCALE, partnership opportunities, or general information',
      icon: <ChatIcon />,
      responseTime: '24-48 hours'
    },
    {
      title: 'Technical Support',
      email: 'support@neurascale.io',
      description: 'Platform issues, integration help, and technical documentation questions',
      icon: <SupportIcon />,
      responseTime: '12-24 hours'
    },
    {
      title: 'Sales & Partnerships',
      email: 'sales@neurascale.io',
      description: 'Enterprise solutions, custom deployments, and strategic partnerships',
      icon: <HandshakeIcon />,
      responseTime: '4-8 hours'
    },
    {
      title: 'Research Collaboration',
      email: 'research@neurascale.io',
      description: 'Academic partnerships, clinical trials, and research data sharing',
      icon: <ResearchContactIcon />,
      responseTime: '24-48 hours'
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
    <section id="contact" ref={containerRef} className="px-6 py-16 relative">
      <motion.div style={{ scale }} className="relative z-10 w-full">
        <div className="flex items-start mb-8">
          <span className="text-white/40 text-sm font-mono mr-4">≡</span>
          <span className="text-white/40 text-sm uppercase tracking-wider">CONTACT</span>
        </div>

        <motion.h2
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          viewport={{ once: true }}
          className="text-4xl md:text-5xl lg:text-6xl font-light mb-6"
        >
          Let's Connect
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          viewport={{ once: true }}
          className="text-white/70 text-lg max-w-4xl mb-16"
        >
          Ready to explore neural interface technology? Get in touch for partnerships, 
          demos, research collaboration, or technical support.
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
              
              <form className="space-y-6" onSubmit={handleSubmit}>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-white/70 text-sm mb-2">Name</label>
                    <input 
                      type="text" 
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-blue-400"
                      placeholder="Your full name"
                    />
                  </div>
                  <div>
                    <label className="block text-white/70 text-sm mb-2">Email</label>
                    <input 
                      type="email" 
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-blue-400"
                      placeholder="your.email@example.com"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-white/70 text-sm mb-2">Organization</label>
                  <input 
                    type="text" 
                    name="organization"
                    value={formData.organization}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-blue-400"
                    placeholder="Your company or institution"
                  />
                </div>
                
                <div>
                  <label className="block text-white/70 text-sm mb-2">Subject</label>
                  <select 
                    name="subject"
                    value={formData.subject}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-blue-400">
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
                    name="message"
                    value={formData.message}
                    onChange={handleInputChange}
                    required
                    rows={6}
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-blue-400 resize-none"
                    placeholder="Tell us about your project, questions, or how we can help..."
                  />
                </div>
                
                <button 
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? 'Sending...' : 'Send Message'}
                </button>
                
                {submitStatus !== 'idle' && (
                  <div className={`mt-4 p-4 rounded-lg ${
                    submitStatus === 'success' ? 'bg-green-500/10 border border-green-500/30 text-green-400' : 'bg-red-500/10 border border-red-500/30 text-red-400'
                  }`}>
                    {statusMessage}
                  </div>
                )}
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

      </motion.div>
    </section>
  )
}