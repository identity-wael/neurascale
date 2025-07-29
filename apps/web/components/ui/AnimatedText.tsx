'use client';

import { motion, Variants } from 'framer-motion';
import { useInView } from 'react-intersection-observer';

interface AnimatedTextProps {
  text: string;
  className?: string;
  delay?: number;
  stagger?: number;
}

export default function AnimatedText({
  text,
  className = '',
  delay = 0,
  stagger = 0.03,
}: AnimatedTextProps) {
  const { ref, inView } = useInView({
    threshold: 0.1,
    triggerOnce: true,
  });

  const words = text.split(' ');

  const container: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delayChildren: delay,
        staggerChildren: stagger,
      },
    },
  };

  const child: Variants = {
    hidden: {
      opacity: 0,
      y: 20,
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.8,
        ease: 'easeOut',
      },
    },
  };

  return (
    <motion.div
      ref={ref}
      variants={container}
      initial="hidden"
      animate={inView ? 'visible' : 'hidden'}
      className={`${className} flex flex-wrap`}
    >
      {words.map((word, i) => (
        <motion.span key={i} variants={child} className="inline-block mr-[0.25em] last:mr-0">
          {word}
        </motion.span>
      ))}
    </motion.div>
  );
}
