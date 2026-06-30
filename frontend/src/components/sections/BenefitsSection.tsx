import { motion } from 'framer-motion';
import { Shield, Lock, TrendingUp } from 'lucide-react';

export default function BenefitsSection() {
  const benefits = [
    {
      title: "Guaranteed Legal Compliance",
      description: "Automatically validates every claim against the latest provisions of the Indian Income Tax Act, 1961, updated for the FY 2024-25 (AY 2025-26) Finance Act. Rest easy knowing your tax optimizations are 100% legal, correct, and cite the exact tax codes.",
      icon: <Shield className="h-6 w-6 text-blue-400" />,
      illustration: (
        <svg className="w-full h-32 text-blue-500/20" viewBox="0 0 200 100" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="10" y="10" width="180" height="80" rx="12" fill="currentColor" stroke="rgba(255,255,255,0.05)" strokeWidth="2" />
          <line x1="30" y1="35" x2="170" y2="35" stroke="rgba(255,255,255,0.1)" strokeWidth="2" />
          <line x1="30" y1="50" x2="140" y2="50" stroke="rgba(255,255,255,0.1)" strokeWidth="2" />
          <line x1="30" y1="65" x2="100" y2="65" stroke="rgba(255,255,255,0.1)" strokeWidth="2" />
          <circle cx="160" cy="58" r="16" fill="#2563EB" fillOpacity="0.2" />
          <path d="M154 58L158 62L166 54" stroke="#3B82F6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      )
    },
    {
      title: "Transient Privacy Protection",
      description: "Our strict 'Transient In-Memory Processing' pipeline guarantees that your uploaded documents and raw salary details are parsed in-memory, processed instantly for reports, and immediately wiped. No financial data is ever stored in our database.",
      icon: <Lock className="h-6 w-6 text-teal-400" />,
      illustration: (
        <svg className="w-full h-32 text-teal-500/20" viewBox="0 0 200 100" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="20" y="20" width="60" height="60" rx="8" fill="currentColor" stroke="rgba(255,255,255,0.05)" strokeWidth="2" />
          <rect x="120" y="20" width="60" height="60" rx="8" fill="currentColor" stroke="rgba(255,255,255,0.05)" strokeWidth="2" />
          <path d="M80 50H120" stroke="rgba(255,255,255,0.1)" strokeWidth="2" strokeDasharray="4 4" />
          <circle cx="100" cy="50" r="12" fill="#14B8A6" fillOpacity="0.2" />
          <path d="M96 50H104" stroke="#14B8A6" strokeWidth="2" strokeLinecap="round" />
          <path d="M100 46V54" stroke="#14B8A6" strokeWidth="2" strokeLinecap="round" />
          <rect x="42" y="42" width="16" height="16" rx="4" fill="#14B8A6" />
          <path d="M142 42C142 42 147 47 150 42C153 37 158 42 158 42" stroke="#14B8A6" strokeWidth="2" />
        </svg>
      )
    },
    {
      title: "Optimized Wealth Strategy",
      description: "Stop missing out on critical savings. We automatically scan for gaps across Section 80C, 80D, 80CCD, 24(b) home loans, and capital gains exemptions, providing direct recommendations and comparison indices that guide you to the highest legal refunds.",
      icon: <TrendingUp className="h-6 w-6 text-cyan-400" />,
      illustration: (
        <svg className="w-full h-32 text-cyan-500/20" viewBox="0 0 200 100" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M20 80C50 60 80 75 110 40C140 5 170 20 180 15" stroke="#06B6D4" strokeWidth="3" strokeLinecap="round" />
          <circle cx="110" cy="40" r="4" fill="#06B6D4" />
          <circle cx="180" cy="15" r="4" fill="#06B6D4" />
          <line x1="20" y1="80" x2="180" y2="80" stroke="rgba(255,255,255,0.05)" strokeWidth="2" />
          <line x1="20" y1="20" x2="20" y2="80" stroke="rgba(255,255,255,0.05)" strokeWidth="2" />
        </svg>
      )
    }
  ];

  return (
    <section id="benefits" className="py-24 max-w-5xl mx-auto px-6 border-t border-slate-900">
      <div className="text-center max-w-2xl mx-auto mb-16">
        <h2 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
          Designed for Total Peace of Mind
        </h2>
        <p className="mt-4 text-base text-slate-400">
          We combine maximum financial efficiency with robust privacy safeguards, ensuring a high-performance advisory experience.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {benefits.map((benefit, index) => (
          <motion.div
            key={index}
            className="flex flex-col justify-between bg-slate-900/35 border border-slate-800/60 rounded-3xl p-6 backdrop-blur-xl relative overflow-hidden group hover:border-slate-700/80 transition-all duration-300"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: index * 0.15 }}
          >
            <div>
              {/* Header */}
              <div className="flex items-center gap-3.5 mb-4">
                <div className="p-2.5 bg-slate-950/80 border border-slate-800/80 rounded-2xl">
                  {benefit.icon}
                </div>
                <h3 className="text-base font-bold text-white text-left">{benefit.title}</h3>
              </div>

              {/* Description */}
              <p className="text-sm text-slate-400 leading-relaxed text-left mb-6">
                {benefit.description}
              </p>
            </div>

            {/* Illustration */}
            <div className="w-full bg-slate-950/40 rounded-2xl border border-slate-900/60 p-4 mt-auto">
              {benefit.illustration}
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
