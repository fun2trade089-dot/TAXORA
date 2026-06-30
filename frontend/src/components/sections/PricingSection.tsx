import { useState } from 'react';
import { Check, HelpCircle, ArrowRight, Minus } from 'lucide-react';
import BorderBeam from '../ui/BorderBeam';

interface Tier {
  name: string;
  price: string;
  period?: string;
  badge?: string;
  description: string;
  features: string[];
  cta: string;
  highlighted: boolean;
}

export default function PricingSection() {
  const [showComparison, setShowComparison] = useState(false);

  const tiers: Tier[] = [
    {
      name: 'Starter',
      price: 'Free',
      period: '',
      description: 'For individuals filing single salary income profiles u/s 16.',
      features: [
        'Salary Income parsing & mapping',
        'Section 80C & HRA exemptions',
        'Standard Old vs. New comparison',
        'Filing document checklists',
        'Email customer support'
      ],
      cta: 'Choose Starter',
      highlighted: false
    },
    {
      name: 'Professional',
      price: '₹499',
      period: '/ Financial Year',
      badge: 'RECOMMENDED / CA CO-PILOT',
      description: 'For professionals, traders, freelancers, and let-out property owners.',
      features: [
        'All Starter capabilities',
        'Capital Gains tracking u/s 111A/112A',
        'House Property let-out deductions',
        'Unlimited AI CA Advisor chat sessions',
        'Section 80D, 80G, and 80GG audits',
        'Full PDF Advisory Memo exports'
      ],
      cta: 'Upgrade to Pro',
      highlighted: true
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      description: 'For tax consultants, accounting firms, and startup founders.',
      features: [
        'All Professional capabilities',
        'Presumptive Business Income u/s 44AD/44ADA',
        'Multi-PAN taxpayer profiles',
        'Custom corporate API access',
        'Priority human CA callback support',
        'SLA guaranteed compliance'
      ],
      cta: 'Contact Sales',
      highlighted: false
    }
  ];

  const comparisonFeatures = [
    { category: 'Income Heads Mapping', name: 'Salary Income (Heads 1)', starter: true, pro: true, ent: true },
    { category: 'Income Heads Mapping', name: 'House Property let-out (Heads 2)', starter: false, pro: true, ent: true },
    { category: 'Income Heads Mapping', name: 'Capital Gains stock/property (Heads 3)', starter: false, pro: true, ent: true },
    { category: 'Income Heads Mapping', name: 'Business Presumptive 44AD/ADA (Heads 4)', starter: false, pro: false, ent: true },
    { category: 'Optimization & RAG', name: 'Old vs New Regime slabs comparison', starter: true, pro: true, ent: true },
    { category: 'Optimization & RAG', name: 'Chapter VI-A Gap recommendations', starter: true, pro: true, ent: true },
    { category: 'Optimization & RAG', name: 'AI CA Chatbot sessions', starter: '10 queries', pro: 'Unlimited', ent: 'Unlimited + API' },
    { category: 'Audit & Compliance', name: 'Filing checklists', starter: true, pro: true, ent: true },
    { category: 'Audit & Compliance', name: 'Compliance warnings (PAN/Exclusion flags)', starter: false, pro: true, ent: true },
    { category: 'Support', name: 'Customer Support channels', starter: 'Email', pro: 'Priority Email/Chat', ent: '24/7 Phone & CA Callback' }
  ];

  return (
    <section id="pricing" className="w-full py-16 px-6 md:px-12 relative flex flex-col items-center justify-center">
      
      {/* Title Header */}
      <div className="text-center flex flex-col items-center gap-3 max-w-xl mb-16 relative z-10">
        <span className="text-xs font-semibold tracking-wider text-blue-400 uppercase">PRICING TIERS</span>
        <h2 className="text-3xl md:text-4xl font-bold text-white tracking-tight">
          Flexible plans for legal tax savings
        </h2>
        <p className="text-sm text-slate-400 leading-relaxed mt-1">
          Pick a plan that matches your income heads. Scale up as you acquire let-out properties, execute stock trades, or manage business profiles.
        </p>
      </div>

      {/* Cards Grid */}
      <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-3 gap-8 relative z-10 items-stretch mb-12">
        {tiers.map((tier, idx) => (
          <div
            key={idx}
            className={`flex flex-col justify-between p-8 bg-slate-900/25 border rounded-3xl shadow-xl backdrop-blur-md transition-all duration-300 relative group select-none ${
              tier.highlighted 
                ? 'border-blue-500/40 bg-slate-900/40 md:-translate-y-4 scale-100 hover:scale-[1.02]' 
                : 'border-slate-800/60 hover:border-slate-700/50 hover:bg-slate-900/30 scale-100 hover:scale-[1.02]'
            }`}
          >
            {/* Spotlight Border Beam overlay on highlighted Pro card */}
            {tier.highlighted && (
              <>
                <BorderBeam 
                  size={180} 
                  duration={4} 
                  borderWidth={2} 
                  colorFrom="#3b82f6" 
                  colorTo="#14b8a6" 
                />
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-gradient-to-r from-blue-600 to-indigo-600 text-[9px] font-bold tracking-widest text-white rounded-full uppercase shadow">
                  {tier.badge}
                </span>
              </>
            )}

            {/* Header info */}
            <div className="flex flex-col gap-4">
              <div className="flex flex-col text-left">
                <span className="text-lg font-bold text-slate-200">{tier.name}</span>
                <p className="text-xs text-slate-400 mt-1.5 leading-relaxed min-h-[40px]">
                  {tier.description}
                </p>
              </div>

              <div className="flex items-baseline gap-1.5 py-4 border-y border-slate-800/60 text-left">
                <span className="text-4xl font-extrabold text-white tracking-tight">{tier.price}</span>
                {tier.period && (
                  <span className="text-xs text-slate-500 font-medium">{tier.period}</span>
                )}
              </div>

              {/* Features checklist */}
              <ul className="flex flex-col gap-3.5 my-6 text-left">
                {tier.features.map((feat, fIdx) => (
                  <li key={fIdx} className="flex items-start gap-2.5 text-xs text-slate-300 leading-tight">
                    <Check className="h-4 w-4 text-teal-400 shrink-0 mt-0.5" />
                    <span>{feat}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* CTA action button */}
            <button className={`w-full py-3 px-4 font-semibold text-xs rounded-xl flex items-center justify-center gap-2 transition-all duration-300 shadow cursor-pointer ${
              tier.highlighted 
                ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-500/20' 
                : 'bg-slate-950/60 hover:bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-200'
            }`}>
              {tier.cta}
              <ArrowRight className="h-4 w-4" />
            </button>

          </div>
        ))}
      </div>

      {/* Comparison Expand Button */}
      <div className="w-full max-w-5xl flex justify-center z-10 mb-8">
        <button
          onClick={() => setShowComparison(!showComparison)}
          className="text-xs font-bold text-slate-400 hover:text-white px-4 py-2 border border-slate-800 rounded-full hover:bg-slate-900/60 transition-colors cursor-pointer flex items-center gap-2"
        >
          {showComparison ? 'Hide Features Comparison' : 'Compare All Features'}
          <HelpCircle className="h-4 w-4 text-blue-400" />
        </button>
      </div>

      {/* Comparison Grid table layout */}
      {showComparison && (
        <div className="w-full max-w-5xl z-10 border border-slate-800 bg-slate-950/40 rounded-2xl overflow-hidden shadow-2xl backdrop-blur-md p-6 text-left animate-fade-in">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-slate-300">
              <thead>
                <tr className="border-b border-slate-800 text-slate-500 font-bold uppercase tracking-wider">
                  <th className="py-4 px-4 w-[40%]">Feature Name</th>
                  <th className="py-4 px-4 text-center">Starter</th>
                  <th className="py-4 px-4 text-center">Pro</th>
                  <th className="py-4 px-4 text-center">Enterprise</th>
                </tr>
              </thead>
              <tbody>
                {comparisonFeatures.map((row, rIdx) => (
                  <tr 
                    key={rIdx} 
                    className="border-b border-slate-900 hover:bg-slate-900/10 transition-colors"
                  >
                    <td className="py-3.5 px-4 font-semibold text-slate-200 flex items-center gap-2">
                      <span className="text-[10px] uppercase font-bold text-slate-500 mr-2 tracking-wide block max-w-[120px] truncate md:max-w-none">
                        [{row.category.split(' ')[0]}]
                      </span>
                      {row.name}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      {typeof row.starter === 'boolean' ? (
                        row.starter ? <Check className="h-4 w-4 text-teal-400 mx-auto" /> : <Minus className="h-4 w-4 text-slate-700 mx-auto" />
                      ) : (
                        <span className="font-medium text-slate-400">{row.starter}</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-center font-bold text-blue-400">
                      {typeof row.pro === 'boolean' ? (
                        row.pro ? <Check className="h-4 w-4 text-blue-400 mx-auto" /> : <Minus className="h-4 w-4 text-slate-700 mx-auto" />
                      ) : (
                        <span>{row.pro}</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      {typeof row.ent === 'boolean' ? (
                        row.ent ? <Check className="h-4 w-4 text-teal-400 mx-auto" /> : <Minus className="h-4 w-4 text-slate-700 mx-auto" />
                      ) : (
                        <span className="font-medium text-slate-350">{row.ent}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </section>
  );
}
