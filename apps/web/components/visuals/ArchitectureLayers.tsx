'use client'

import React, { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface LayerComponent {
  name: string
  description: string
  category?: string
}

interface Layer {
  id: string
  name: string
  color: string
  description: string
  components: LayerComponent[]
}

const ArchitectureLayers = () => {
  const [activeLayer, setActiveLayer] = useState(0)
  const [expandedComponent, setExpandedComponent] = useState<string | null>(null)

  const layers: Layer[] = [
    {
      id: 'xr',
      name: 'XR Layer',
      color: 'from-purple-500 to-pink-500',
      description: 'Extended Reality and Immersive Interfaces',
      components: [
        {
          name: 'World Simulator (VR/XR)',
          description: 'Advanced virtual world simulation engine for immersive experiences',
          category: 'Simulation'
        },
        {
          name: 'Mixed Reality XR API Gateway',
          description: 'API layer managing mixed reality interactions and data flows',
          category: 'API'
        },
        {
          name: 'NVIDIA OmniVerse XR API Gateway',
          description: 'Integration with NVIDIA OmniVerse platform for XR development',
          category: 'Platform'
        },
        {
          name: 'NVIDIA OmniVerse VR',
          description: 'Virtual reality implementation using NVIDIA OmniVerse technology',
          category: 'VR'
        }
      ]
    },
    {
      id: 'application',
      name: 'Application Layer',
      color: 'from-cyan-500 to-blue-500',
      description: 'Core Applications and User Interfaces',
      components: [
        {
          name: 'Full Dive VR',
          description: 'Complete virtual reality immersion system for neural interfaces',
          category: 'VR'
        },
        {
          name: 'Virtual Myoelectric Simulator',
          description: 'Simulation environment for myoelectric prosthetic training',
          category: 'Simulation'
        },
        {
          name: 'Myoelectric Diagnostics & Optimization',
          description: 'Advanced diagnostics and optimization tools for prosthetic devices',
          category: 'Diagnostics'
        },
        {
          name: 'Retinal Prostheses Video Stream',
          description: 'Video processing pipeline for retinal implant systems',
          category: 'Medical'
        },
        {
          name: 'Cochlear Implants Audio Stream',
          description: 'Audio processing system for cochlear implant devices',
          category: 'Medical'
        },
        {
          name: 'VR Scenario Manager',
          description: 'Management system for virtual reality training scenarios',
          category: 'Management'
        }
      ]
    },
    {
      id: 'nms',
      name: 'Neural Management System',
      color: 'from-green-500 to-emerald-500',
      description: 'Core Orchestration and AI Systems',
      components: [
        {
          name: 'AI Domain Agnostic Models',
          description: 'Flexible AI models adaptable across different neural interface domains',
          category: 'AI'
        },
        {
          name: 'Robotic Controller',
          description: 'Advanced control systems for robotic prosthetics and devices',
          category: 'Robotics'
        },
        {
          name: 'Fleet Management',
          description: 'Centralized management of distributed neural interface devices',
          category: 'Management'
        },
        {
          name: 'Real-Time Feed Streams',
          description: 'High-speed data streaming for real-time neural signal processing',
          category: 'Data'
        },
        {
          name: 'Device Telemetry',
          description: 'Comprehensive monitoring and telemetry for connected devices',
          category: 'Monitoring'
        },
        {
          name: 'Device Interface',
          description: 'Standardized interface layer for diverse neural devices',
          category: 'Interface'
        },
        {
          name: 'Device Identity',
          description: 'Secure identity management for neural interface devices',
          category: 'Security'
        }
      ]
    },
    {
      id: 'genai',
      name: 'GenAI Layer',
      color: 'from-orange-500 to-red-500',
      description: 'Generative AI and Agent Systems',
      components: [
        {
          name: 'Agent Protocol (ADK with A2A)',
          description: 'Advanced agent development kit with agent-to-agent communication',
          category: 'Protocol'
        },
        {
          name: 'LLM (Anthropic Claude Opus, Sonnet, Haiku)',
          description: 'Large language models for natural language processing and reasoning',
          category: 'LLM'
        },
        {
          name: 'AI Operating System (Letta)',
          description: 'Specialized operating system for AI agent management',
          category: 'OS'
        },
        {
          name: 'Agent Orchestrator (Agent Engine / CrewAI)',
          description: 'Orchestration platform for coordinating multiple AI agents',
          category: 'Orchestration'
        }
      ]
    },
    {
      id: 'ml',
      name: 'ML Layer',
      color: 'from-yellow-500 to-orange-500',
      description: 'Machine Learning and Signal Processing',
      components: [
        {
          name: 'Adaptive Learning Agent (Reinforcement Learning)',
          description: 'Self-improving ML agent using reinforcement learning techniques',
          category: 'Learning'
        },
        {
          name: 'Memory Correlator (Reinforcement Learning)',
          description: 'Neural memory correlation system for pattern recognition',
          category: 'Memory'
        },
        {
          name: 'Seizure Prediction Model (CNN, LSTM)',
          description: 'Deep learning model for predicting epileptic seizures',
          category: 'Medical'
        },
        {
          name: 'Movement Intention Classifier (RNN / LSTM)',
          description: 'Neural network for classifying intended movements from brain signals',
          category: 'Classification'
        },
        {
          name: 'Feature Extraction Engine (PCA)',
          description: 'Principal component analysis for neural signal feature extraction',
          category: 'Processing'
        },
        {
          name: 'Signal Denoising & Filtering (Kalman Filter)',
          description: 'Advanced filtering system for neural signal cleanup',
          category: 'Processing'
        }
      ]
    },
    {
      id: 'cloud',
      name: 'Multi-Cloud Layer',
      color: 'from-indigo-500 to-purple-500',
      description: 'Cloud Infrastructure and Data Services',
      components: [
        {
          name: 'Load Balancing (GCP LB)',
          description: 'Google Cloud Platform load balancing for distributed systems',
          category: 'Infrastructure'
        },
        {
          name: 'Serverless Workload (Cloud Run)',
          description: 'Containerized serverless computing platform',
          category: 'Compute'
        },
        {
          name: 'Data Warehouse (BigQuery)',
          description: 'Scalable data warehouse for analytics and machine learning',
          category: 'Storage'
        },
        {
          name: 'Object Storage (Google Storage)',
          description: 'Distributed object storage for large-scale data',
          category: 'Storage'
        },
        {
          name: 'High Speed Vector Database (AlloyDB)',
          description: 'High-performance database optimized for vector operations',
          category: 'Database'
        },
        {
          name: 'In Memory DB (Redis)',
          description: 'Ultra-fast in-memory database for real-time operations',
          category: 'Database'
        },
        {
          name: 'Message Broker (Pub/Sub)',
          description: 'Asynchronous messaging system for distributed components',
          category: 'Messaging'
        },
        {
          name: 'Processing Unit (TPU/GPU/NPU/CPU)',
          description: 'Specialized processing units for AI and ML workloads',
          category: 'Compute'
        }
      ]
    }
  ]

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      'Simulation': 'bg-purple-500/20 text-purple-300',
      'API': 'bg-blue-500/20 text-blue-300',
      'Platform': 'bg-green-500/20 text-green-300',
      'VR': 'bg-pink-500/20 text-pink-300',
      'Diagnostics': 'bg-orange-500/20 text-orange-300',
      'Medical': 'bg-red-500/20 text-red-300',
      'Management': 'bg-cyan-500/20 text-cyan-300',
      'AI': 'bg-indigo-500/20 text-indigo-300',
      'Robotics': 'bg-emerald-500/20 text-emerald-300',
      'Data': 'bg-teal-500/20 text-teal-300',
      'Monitoring': 'bg-yellow-500/20 text-yellow-300',
      'Interface': 'bg-lime-500/20 text-lime-300',
      'Security': 'bg-rose-500/20 text-rose-300',
      'Protocol': 'bg-violet-500/20 text-violet-300',
      'LLM': 'bg-fuchsia-500/20 text-fuchsia-300',
      'OS': 'bg-sky-500/20 text-sky-300',
      'Orchestration': 'bg-amber-500/20 text-amber-300',
      'Learning': 'bg-slate-500/20 text-slate-300',
      'Memory': 'bg-zinc-500/20 text-zinc-300',
      'Classification': 'bg-stone-500/20 text-stone-300',
      'Processing': 'bg-neutral-500/20 text-neutral-300',
      'Infrastructure': 'bg-gray-500/20 text-gray-300',
      'Compute': 'bg-blue-600/20 text-blue-400',
      'Storage': 'bg-green-600/20 text-green-400',
      'Database': 'bg-purple-600/20 text-purple-400',
      'Messaging': 'bg-orange-600/20 text-orange-400'
    }
    return colors[category] || 'bg-gray-500/20 text-gray-300'
  }

  return (
    <div className="w-full h-full bg-black text-white overflow-hidden">
      {/* Layer Navigation */}
      <div className="flex items-center justify-center space-x-4 py-6 px-4">
        {layers.map((layer, index) => (
          <motion.button
            key={layer.id}
            onClick={() => setActiveLayer(index)}
            className={`px-4 py-2 rounded-lg transition-all duration-300 ${
              activeLayer === index
                ? 'bg-white/20 text-white border-2 border-white/30'
                : 'bg-white/5 text-white/70 border border-white/10 hover:bg-white/10'
            }`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <div className="text-sm font-medium">{layer.name}</div>
          </motion.button>
        ))}
      </div>

      {/* Layer Visualization */}
      <div className="relative h-96 mx-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeLayer}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -100 }}
            transition={{ duration: 0.5 }}
            className="absolute inset-0"
          >
            {/* Layer Header */}
            <div className="text-center mb-6">
              <div className={`inline-block px-6 py-3 rounded-lg bg-gradient-to-r ${layers[activeLayer].color} mb-4`}>
                <h3 className="text-xl font-bold text-white">{layers[activeLayer].name}</h3>
              </div>
              <p className="text-white/70 max-w-2xl mx-auto">{layers[activeLayer].description}</p>
            </div>

            {/* Components Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-64 overflow-y-auto px-4">
              {layers[activeLayer].components.map((component, index) => (
                <motion.div
                  key={`${activeLayer}-${index}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 
                           hover:bg-white/10 transition-all duration-300 cursor-pointer
                           hover:border-white/20 hover:shadow-lg"
                  onClick={() => setExpandedComponent(
                    expandedComponent === `${activeLayer}-${index}` 
                      ? null 
                      : `${activeLayer}-${index}`
                  )}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-white/90 text-sm">{component.name}</h4>
                    {component.category && (
                      <span className={`px-2 py-1 rounded text-xs ${getCategoryColor(component.category)}`}>
                        {component.category}
                      </span>
                    )}
                  </div>
                  
                  <AnimatePresence>
                    {expandedComponent === `${activeLayer}-${index}` && (
                      <motion.p
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="text-white/70 text-xs leading-relaxed"
                      >
                        {component.description}
                      </motion.p>
                    )}
                  </AnimatePresence>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Layer Indicators */}
      <div className="flex justify-center space-x-2 mt-6 pb-6">
        {layers.map((_, index) => (
          <motion.div
            key={index}
            className={`w-3 h-3 rounded-full transition-all duration-300 ${
              activeLayer === index ? 'bg-white' : 'bg-white/30'
            }`}
            whileHover={{ scale: 1.2 }}
          />
        ))}
      </div>
    </div>
  )
}

export default ArchitectureLayers