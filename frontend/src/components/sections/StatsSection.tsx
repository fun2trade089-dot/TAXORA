import { useEffect, useState, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { Wallet, Users, Target, Clock } from 'lucide-react';

interface CountUpProps {
  to: number;
  duration?: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
}

function CountUp({ to, duration = 2, decimals = 0, prefix = '', suffix = '' }: CountUpProps) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });

  useEffect(() => {
    if (!isInView) return;

    const start = 0;
    const end = to;
    const totalFrames = duration * 60; // 60fps
    let frame = 0;

    const countAnimation = () => {
      frame++;
      const progress = frame / totalFrames;
      // Ease out quad curve
      const easedProgress = progress * (2 - progress);
      const current = start + easedProgress * (end - start);

      setCount(current);

      if (frame < totalFrames) {
        requestAnimationFrame(countAnimation);
      } else {
        setCount(end);
      }
    };

    requestAnimationFrame(countAnimation);
  }, [isInView, to, duration]);

  return (
    <span ref={ref} className="tabular-nums">
      {prefix}
      {count.toFixed(decimals)}
      {suffix}
    </span>
  );
}

export default function StatsSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const isContainerInView = useInView(containerRef, { once: true, margin: '-100px' });

  const containerVariants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: 0.15
      }
    }
  };

  const cardVariants = {
    hidden: { 
      opacity: 0, 
      y: 40,
      scale: 0.95
    },
    visible: { 
      opacity: 1, 
      y: 0,
      scale: 1,
      transition: { 
        duration: 0.8, 
        ease: [0.16, 1, 0.3, 1] as const
      }
    }
  };

  const stats = [
    {
      icon: <Wallet className="h-6 w-6 text-blue-400" />,
      label: 'Total Tax Saved legally',
      to: 120,
      prefix: '₹',
      suffix: 'Cr+',
      decimals: 0,
      description: 'Optimized via deductions & slabs u/s 80C, 24b, and 10(13A).'
    },
    {
      icon: <Users className="h-6 w-6 text-teal-400" />,
      label: 'Active Taxpayers & CAs',
      to: 50,
      prefix: '',
      suffix: 'K+',
      decimals: 0,
      description: 'Professionals, business owners, and consultants trust our advisor.'
    },
    {
      icon: <Target className="h-6 w-6 text-purple-400" />,
      label: 'AI Recommendation Accuracy',
      to: 99.8,
      prefix: '',
      suffix: '%',
      decimals: 1,
      description: 'Validated continuously against actual IT Department notifications.'
    },
    {
      icon: <Clock className="h-6 w-6 text-indigo-400" />,
      label: 'AI Legal Copilot Availability',
      to: 24,
      prefix: '',
      suffix: '/7',
      decimals: 0,
      description: 'Instant compliance queries and CA advisory memos, anytime.'
    }
  ];

  return (
    <div ref={containerRef} className="w-full py-16 px-6 md:px-12 relative overflow-hidden flex flex-col items-center justify-center">
      {/* Divider line style decoration */}
      <div className="w-full max-w-5xl h-px bg-gradient-to-r from-transparent via-slate-800 to-transparent mb-16" />

      {/* Grid container */}
      <motion.div 
        className="w-full max-w-5xl grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 relative z-10"
        variants={containerVariants}
        initial="hidden"
        animate={isContainerInView ? "visible" : "hidden"}
      >
        {stats.map((stat, idx) => (
          <motion.div
            key={idx}
            className="group relative flex flex-col p-6 bg-slate-900/20 hover:bg-slate-900/40 border border-slate-800/40 hover:border-blue-500/20 rounded-2xl shadow-xl backdrop-blur-md transition-all duration-300 overflow-hidden"
            variants={cardVariants}
          >
            {/* Soft inner cards glow */}
            <div className="absolute top-0 right-0 w-16 h-16 bg-blue-500/5 rounded-full blur-xl group-hover:bg-blue-500/10 transition-colors" />

            <div className="flex items-center gap-3">
              <div className="p-3 bg-slate-950/40 rounded-xl border border-slate-800/60 group-hover:border-blue-500/20 transition-colors shadow-inner shrink-0">
                {stat.icon}
              </div>
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider text-left leading-tight">
                {stat.label}
              </span>
            </div>

            <div className="mt-5 flex flex-col text-left">
              <span className="text-3xl font-extrabold text-white tracking-tight">
                <CountUp 
                  to={stat.to} 
                  decimals={stat.decimals} 
                  prefix={stat.prefix} 
                  suffix={stat.suffix} 
                />
              </span>
              <p className="text-xs text-slate-400 leading-relaxed mt-2.5">
                {stat.description}
              </p>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
