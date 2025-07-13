'use client'

import { motion } from 'framer-motion'

const jobs = [
  {
    position: 'Neural Interface Engineer',
    location: 'Mountain View, Remote',
  },
  {
    position: 'ML/AI Research Scientist',
    location: 'San Francisco, Remote',
  },
  {
    position: 'Cloud Infrastructure Architect',
    location: 'Remote',
  },
  {
    position: 'Brain-Computer Interface Specialist',
    location: 'Boston, Remote',
  },
  {
    position: 'Full-Stack Developer (Agentic Applications)',
    location: 'Remote',
  },
]

export default function JobTable() {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-white/20">
            <th className="text-left py-4 px-4 font-normal text-white/60">Position</th>
            <th className="text-left py-4 px-4 font-normal text-white/60">Location</th>
            <th className="w-24"></th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job, index) => (
            <motion.tr
              key={index}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: index * 0.1 }}
              className="border-b border-white/10 hover:bg-white/5 transition-colors"
            >
              <td className="py-6 px-4">{job.position}</td>
              <td className="py-6 px-4 text-white/70">{job.location}</td>
              <td className="py-6 px-4">
                <button className="text-white/60 hover:text-white transition-colors">
                  →
                </button>
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}