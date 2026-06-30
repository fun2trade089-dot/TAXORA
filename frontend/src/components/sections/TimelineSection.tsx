import { motion } from 'framer-motion';
import { 
  UploadCloud, 
  Binary, 
  BookOpen, 
  Calculator, 
  Lightbulb, 
  FileCheck2 
} from 'lucide-react';

export default function TimelineSection() {
  const steps = [
    {
      icon: <UploadCloud className="h-5 w-5 text-blue-400" />,
      title: 'Upload Documents',
      description: 'Securely upload your Form 16, rent receipts, investment proofs, or capital gains statements in PDF or image format.',
      accent: 'border-blue-500/30 bg-blue-500/5 text-blue-400'
    },
    {
      icon: <Binary className="h-5 w-5 text-teal-400" />,
      title: 'AI Reads Financial Records',
      description: 'Our intelligent parser structures salary heads, let-out properties, capital gains, and deductions without manual inputs.',
      accent: 'border-teal-500/30 bg-teal-500/5 text-teal-400'
    },
    {
      icon: <BookOpen className="h-5 w-5 text-purple-400" />,
      title: 'Search Tax Laws',
      description: 'RAG crawler searches the legal database of the Income Tax Act, circulars, notifications, and case laws for relevant sections.',
      accent: 'border-purple-500/30 bg-purple-500/5 text-purple-400'
    },
    {
      icon: <Calculator className="h-5 w-5 text-indigo-400" />,
      title: 'Calculate Tax Liability',
      description: 'The deterministic Python tax engine calculates slabs, 87A rebates, surcharges with marginal relief, and cess for both tax regimes.',
      accent: 'border-indigo-500/30 bg-indigo-500/5 text-indigo-400'
    },
    {
      icon: <Lightbulb className="h-5 w-5 text-yellow-400" />,
      title: 'Find Legal Deductions',
      description: 'An optimization gap analysis maps unclaimed deductions u/s 80C, 80D, 80CCD(1B), and HRA rules to legally minimize tax.',
      accent: 'border-yellow-500/30 bg-yellow-500/5 text-yellow-400'
    },
    {
      icon: <FileCheck2 className="h-5 w-5 text-emerald-400" />,
      title: 'Generate Optimization Report',
      description: 'Export a structured CA Advisory Memo containing computation details, regime comparison tables, and filing checklists.',
      accent: 'border-emerald-500/30 bg-emerald-500/5 text-emerald-400'
    }
  ];

  return (
    <section id="how-it-works" className="w-full py-16 px-6 md:px-12 relative flex flex-col items-center justify-center">
      {/* Title Header */}
      <div className="text-center flex flex-col items-center gap-3 max-w-xl mb-20">
        <span className="text-xs font-semibold tracking-wider text-purple-400 uppercase">THE ADVISORY WORKFLOW</span>
        <h2 className="text-3xl md:text-4xl font-bold text-white tracking-tight">
          How TAXORA optimizes your filings
        </h2>
        <p className="text-sm text-slate-400 leading-relaxed mt-1">
          A step-by-step walk through the technology pipeline that reads documents, validates laws, and structures your tax optimization.
        </p>
      </div>

      {/* Timeline Wrapper */}
      <div className="w-full max-w-4xl relative">
        
        {/* Clean central connecting line (hidden on mobile, centered on desktop) */}
        <div className="absolute left-4 md:left-1/2 top-0 bottom-0 w-[1.5px] bg-gradient-to-b from-blue-500 via-purple-500 to-emerald-500 transform -translate-x-[0.75px] pointer-events-none opacity-40 z-0" />

        {/* Steps loop */}
        <div className="flex flex-col gap-12 md:gap-8">
          {steps.map((step, idx) => {
            const isEven = idx % 2 === 0;

            return (
              <motion.div
                key={idx}
                className={`relative w-full flex flex-col md:flex-row items-start md:items-center justify-start md:justify-center z-10`}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-80px' }}
                transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
              >
                {/* Left pane: empty on desktop for odd, contains card on desktop for even */}
                <div className={`w-full md:w-1/2 flex justify-start md:justify-end pr-0 md:pr-12 pl-12 md:pl-0 order-2 md:order-1 ${isEven ? 'md:flex' : 'md:hidden'}`}>
                  <div className="p-6 bg-slate-900/20 border border-slate-800/60 rounded-2xl hover:border-blue-500/20 shadow-lg backdrop-blur-md transition-all duration-300 max-w-md text-left relative overflow-hidden group hover:bg-slate-900/30">
                    <div className="absolute top-0 right-0 w-12 h-12 bg-blue-500/5 rounded-full blur-xl group-hover:bg-blue-500/10 transition-colors" />
                    <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                      <span className="text-xs text-slate-500 font-mono">0{idx + 1}.</span>
                      {step.title}
                    </h3>
                    <p className="text-xs text-slate-400 leading-relaxed mt-2.5">
                      {step.description}
                    </p>
                  </div>
                </div>

                {/* Center node: connecting node circle */}
                <div className="absolute left-0 md:left-1/2 transform -translate-x-[7px] md:-translate-x-1/2 z-20 order-1 md:order-2 flex items-center justify-center">
                  <div className={`p-2.5 rounded-full border shadow-lg backdrop-blur-md transition-all duration-300 ${step.accent} scale-100 hover:scale-110`}>
                    {step.icon}
                  </div>
                </div>

                {/* Right pane: empty on desktop for even, contains card on desktop for odd */}
                <div className={`w-full md:w-1/2 flex justify-start pl-12 pr-0 md:pr-0 order-2 md:order-3 ${!isEven ? 'md:flex' : 'md:hidden'}`}>
                  <div className="p-6 bg-slate-900/20 border border-slate-800/60 rounded-2xl hover:border-teal-500/20 shadow-lg backdrop-blur-md transition-all duration-300 max-w-md text-left relative overflow-hidden group hover:bg-slate-900/30">
                    <div className="absolute top-0 right-0 w-12 h-12 bg-teal-500/5 rounded-full blur-xl group-hover:bg-teal-500/10 transition-colors" />
                    <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
                      <span className="text-xs text-slate-500 font-mono">0{idx + 1}.</span>
                      {step.title}
                    </h3>
                    <p className="text-xs text-slate-400 leading-relaxed mt-2.5">
                      {step.description}
                    </p>
                  </div>
                </div>

              </motion.div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
