import { motion } from 'framer-motion';
import { 
  ShieldCheck, 
  TrendingUp, 
  FileCheck, 
  Sparkles, 
  CheckCircle,
  Clock,
  ArrowRight
} from 'lucide-react';
import TextReveal from '../text/TextReveal';
import BorderBeam from '../ui/BorderBeam';
import ShinyText from '../text/ShinyText';
import Spotlight from '../backgrounds/Spotlight';

export default function SaaSHero() {
  return (
    <Spotlight className="relative w-full min-h-[calc(100vh-6rem)] flex items-center justify-center py-12 px-6 md:px-12 overflow-hidden">
      {/* Decorative radial gradients for glow effects */}
      <div className="absolute top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 translate-x-1/2 translate-y-1/2 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-12 gap-12 items-center relative z-10">
        
        {/* Left Column: Copy & CTAs */}
        <div className="lg:col-span-6 flex flex-col items-start text-left gap-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-400 text-xs font-semibold tracking-wider">
            <Sparkles className="h-3.5 w-3.5 animate-pulse" />
            <span>EXPERT LEGAL TAX ADVISOR</span>
          </div>

          <div className="flex flex-col gap-3">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-black text-white tracking-tight leading-[1.1] select-none">
              <TextReveal 
                text="AI-Powered" 
                className="bg-gradient-to-r from-blue-400 via-indigo-200 to-teal-300 bg-clip-text text-transparent block" 
                delay={0.1}
              />
              <TextReveal 
                text="Tax Intelligence" 
                className="text-white block mt-1" 
                delay={0.5}
              />
            </h1>
            <p className="text-base md:text-lg text-slate-400 leading-relaxed max-w-lg mt-2">
              The Future of Tax Intelligence.
            </p>
          </div>

          <div className="flex flex-wrap gap-4 mt-4 w-full sm:w-auto">
            {/* Primary Button: Border Beam Effect */}
            <button 
              onClick={() => window.location.hash = '#login'} 
              className="relative px-6 py-3.5 bg-slate-900 border border-slate-800 text-white font-semibold text-sm rounded-xl hover:bg-slate-900/60 transition-all duration-300 shadow-xl shadow-blue-500/5 cursor-pointer overflow-hidden group"
            >
              <BorderBeam 
                size={120} 
                duration={5} 
                borderWidth={2} 
                colorFrom="#2563EB" 
                colorTo="#14B8A6" 
              />
              <span className="relative z-10 flex items-center gap-2">
                Get Started
                <ArrowRight className="h-4 w-4 text-teal-400 group-hover:translate-x-1 transition-transform" />
              </span>
            </button>
          </div>

          <div className="mt-8 flex items-center gap-6 border-t border-slate-800/80 pt-6 w-full">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-green-400" />
              <span className="text-xs text-slate-400 font-medium">100% Compliant</span>
            </div>
            <div className="w-1.5 h-1.5 bg-slate-800 rounded-full" />
            <div className="flex items-center gap-2">
              <FileCheck className="h-5 w-5 text-blue-400" />
              <span className="text-xs text-slate-400 font-medium">Sec. 80C, 24b, 10(13A)</span>
            </div>
          </div>
        </div>

        {/* Right Column: Floating AI Dashboard Mockup */}
        <div className="lg:col-span-6 w-full flex justify-center lg:justify-end relative">
          <motion.div 
            className="w-full max-w-md bg-slate-900/40 border border-slate-800/80 rounded-3xl p-6 shadow-2xl backdrop-blur-xl relative"
            animate={{ y: [0, -12, 0] }}
            transition={{
              duration: 6,
              ease: "easeInOut",
              repeat: Infinity
            }}
          >
            {/* Dashboard Header decoration */}
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-4 mb-6">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 bg-red-500 rounded-full" />
                <span className="w-2.5 h-2.5 bg-yellow-500 rounded-full" />
                <span className="w-2.5 h-2.5 bg-green-500 rounded-full" />
              </div>
              <span className="text-xs text-slate-500 tracking-wider uppercase font-semibold">TAX INTELLIGENCE PLATFORM</span>
            </div>

            {/* Inner Dashboard mock layout */}
            <div className="grid grid-cols-2 gap-4">
              
              {/* Card 1: Refund Estimate */}
              <div className="col-span-2 p-5 bg-gradient-to-tr from-slate-950/60 to-slate-900/60 border border-slate-800/80 rounded-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-24 h-24 bg-green-500/5 rounded-full blur-2xl" />
                <div className="flex flex-col gap-1.5">
                  <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-ping" />
                    Refund Estimate Optimization
                  </span>
                  <div className="flex items-baseline gap-2 mt-1">
                    <span className="text-3xl font-extrabold text-white">₹1,42,500</span>
                    <span className="text-xs text-green-400 font-medium flex items-center gap-0.5">
                      <TrendingUp className="h-3.5 w-3.5" />
                      +42%
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-400 mt-1">Maximized legally u/s 10(13A) & Chapter VI-A</p>
                </div>
              </div>

              {/* Card 2: Tax Score (Radial Circular Gauge) */}
              <div className="p-4 bg-slate-950/50 border border-slate-800/80 rounded-2xl flex flex-col items-center justify-center gap-3">
                <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider text-center">Tax Optimization Score</span>
                <div className="relative w-20 h-20 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <path
                      className="text-slate-800"
                      strokeWidth="2.5"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path
                      className="text-blue-500"
                      strokeWidth="2.5"
                      strokeDasharray="92, 100"
                      strokeLinecap="round"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                  </svg>
                  <div className="absolute text-center flex flex-col">
                    <span className="text-lg font-black text-white leading-none">92</span>
                    <span className="text-[8px] text-slate-500 font-semibold mt-0.5">/100</span>
                  </div>
                </div>
                <span className="text-[9px] text-blue-400 font-semibold px-2 py-0.5 bg-blue-500/10 border border-blue-500/20 rounded-full">Highly Optimized</span>
              </div>

              {/* Card 3: Documents Analyzed */}
              <div className="p-4 bg-slate-950/50 border border-slate-800/80 rounded-2xl flex flex-col gap-2.5">
                <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Indexed Documents</span>
                <div className="flex flex-col gap-2 mt-1">
                  {[
                    { name: 'Form 16 Part A/B', status: 'done' },
                    { name: 'Rent Receipts', status: 'done' },
                    { name: '80C Declarations', status: 'pending' }
                  ].map((doc, idx) => (
                    <div key={idx} className="flex items-center justify-between text-[10px] bg-slate-900/60 p-1.5 rounded-lg border border-slate-850">
                      <span className="text-slate-300 font-medium truncate max-w-[80px]">{doc.name}</span>
                      {doc.status === 'done' ? (
                        <CheckCircle className="h-3.5 w-3.5 text-teal-400 shrink-0" />
                      ) : (
                        <Clock className="h-3.5 w-3.5 text-yellow-500 shrink-0" />
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Card 4: AI recommendation bubble */}
              <div className="col-span-2 p-4 bg-gradient-to-r from-purple-950/10 to-indigo-950/10 border border-purple-900/30 rounded-2xl flex items-start gap-3">
                <div className="p-2 bg-purple-500/10 border border-purple-500/20 rounded-xl text-purple-400 shrink-0">
                  <Sparkles className="h-4 w-4 animate-pulse" />
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-[9px] text-purple-400 font-bold uppercase tracking-wider">AI CA Recommendation</span>
                  <p className="text-[10px] text-slate-300 leading-relaxed font-medium">
                    <ShinyText 
                      text="Claim let-out standard deduction u/s 24(a) to legally reduce net taxable property income by 30%." 
                      speed={5} 
                      color="#cbd5e1" 
                      shineColor="#c084fc" 
                    />
                  </p>
                </div>
              </div>
              
            </div>
          </motion.div>
        </div>

      </div>
    </Spotlight>
  );
}
