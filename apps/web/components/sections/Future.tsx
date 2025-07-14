'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import dynamic from 'next/dynamic';

const ServerRacks3D = dynamic(() => import('@/components/visuals/ServerRacks3D'), {
  ssr: false,
  loading: () => <div className="absolute inset-0 bg-black" />,
});

export default function Future() {
  const { ref, inView } = useInView({
    threshold: 0.3,
    triggerOnce: true,
  });

  return (
    <section
      ref={ref}
      className="min-h-screen flex items-center px-6 md:px-12 lg:px-24 py-24 relative overflow-hidden"
    >
      {/* 3D Server Racks Background */}
      <div className="absolute inset-0 opacity-40">
        <ServerRacks3D />
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={inView ? { opacity: 1 } : {}}
        transition={{ duration: 1 }}
        className="max-w-5xl relative z-10"
      >
        <h2 className="text-4xl md:text-5xl lg:text-6xl font-light mb-12">
          Unlocking human potential at the speed of thought
        </h2>

        <p className="text-xl md:text-2xl text-white/80 mb-16">
          Join us in building the infrastructure that will restore autonomy to millions and redefine
          human-machine interaction
        </p>

        <div className="space-y-8 text-lg text-white/70">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="backdrop-blur-sm bg-black/30 p-6 rounded-lg border border-white/10"
          >
            <h3 className="text-2xl text-white mb-3">Restored Autonomy</h3>
            <p>
              For millions living with paralysis, NEURASCALE offers the potential to regain mobility
              and communication, drastically improving quality of life through direct neural control
              of prosthetics and devices.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="backdrop-blur-sm bg-black/30 p-6 rounded-lg border border-white/10"
          >
            <h3 className="text-2xl text-white mb-3">Advanced Human-Machine Interaction</h3>
            <p>
              Enable sophisticated control over robotic systems, from prosthetic limbs to swarms of
              robots, and facilitate "Full-Dive" VR experiences seamlessly integrated with neural
              intent.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="backdrop-blur-sm bg-black/30 p-6 rounded-lg border border-white/10"
          >
            <h3 className="text-2xl text-white mb-3">Next-Generation Security</h3>
            <p>
              Introducing passwordless "Neural ID" authentication using unique brain patterns,
              providing unprecedented security for the digital age.
            </p>
          </motion.div>
        </div>
      </motion.div>
    </section>
  );
}
