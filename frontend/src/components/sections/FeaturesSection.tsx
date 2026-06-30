import { 
  Bot, 
  FileText, 
  Scale, 
  Search, 
  Coins, 
  ShieldCheck 
} from 'lucide-react';
import TiltCard from '../ui/TiltCard';

export default function FeaturesSection() {
  const features = [
    {
      icon: <Bot className="h-6 w-6 text-blue-400" />,
      title: 'AI Tax Advisor',
      description: 'Conversational Chartered Accountant copilot trained on statutory rules, answering complex tax structuring queries.',
      glow: 'rgba(59, 130, 246, 0.15)' // Blue glow
    },
    {
      icon: <FileText className="h-6 w-6 text-teal-400" />,
      title: 'Smart Document Analysis',
      description: 'Auto-extract taxable components, exemptions, and deductions from Form 16, rent receipts, and capital gain ledgers.',
      glow: 'rgba(20, 184, 166, 0.15)' // Teal glow
    },
    {
      icon: <Scale className="h-6 w-6 text-purple-400" />,
      title: 'Legal Tax Optimization',
      description: 'Run automatic comparisons of Old vs. New tax regimes and optimize Chapter VI-A deductions u/s 80C and 80D.',
      glow: 'rgba(168, 85, 247, 0.15)' // Purple glow
    },
    {
      icon: <Search className="h-6 w-6 text-indigo-400" />,
      title: 'Tax Law Search',
      description: 'Query statutory provisions, circulars, and judicial rulings with official source links and amendment dates.',
      glow: 'rgba(99, 102, 241, 0.15)' // Indigo glow
    },
    {
      icon: <Coins className="h-6 w-6 text-green-400" />,
      title: 'Refund Prediction',
      description: 'Estimate net tax liabilities, surcharges, rebates u/s 87A, and projected refunds dynamically with visual charts.',
      glow: 'rgba(34, 197, 94, 0.15)' // Green glow
    },
    {
      icon: <ShieldCheck className="h-6 w-6 text-sky-400" />,
      title: 'Compliance Monitoring',
      description: 'Monitor PAN declarations, house property loss limits, and receive audit warning flags for high-risk filings.',
      glow: 'rgba(14, 165, 233, 0.15)' // Sky glow
    }
  ];

  return (
    <section id="features" className="w-full py-16 px-6 md:px-12 relative flex flex-col items-center justify-center">
      {/* Title Header */}
      <div className="text-center flex flex-col items-center gap-3 max-w-xl mb-16">
        <span className="text-xs font-semibold tracking-wider text-teal-400 uppercase">PLATFORM CAPABILITIES</span>
        <h2 className="text-3xl md:text-4xl font-bold text-white tracking-tight">
          Everything you need for expert tax advising
        </h2>
        <p className="text-sm text-slate-400 leading-relaxed mt-1">
          Explore the automated features designed to keep your tax filings 100% compliant, fully optimized, and legally minimized.
        </p>
      </div>

      {/* Features Grid */}
      <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 relative z-10">
        {features.map((feature, idx) => (
          <TiltCard
            key={idx}
            glowColor={feature.glow}
            className="w-full min-h-[220px]"
          >
            {/* Icon */}
            <div className="p-3 bg-slate-950/40 border border-slate-800/60 rounded-xl shadow-inner mb-2">
              {feature.icon}
            </div>
            
            {/* Title */}
            <h3 className="text-lg font-bold text-white tracking-tight">
              {feature.title}
            </h3>
            
            {/* Description */}
            <p className="text-xs text-slate-400 leading-relaxed mt-1">
              {feature.description}
            </p>
          </TiltCard>
        ))}
      </div>
    </section>
  );
}
