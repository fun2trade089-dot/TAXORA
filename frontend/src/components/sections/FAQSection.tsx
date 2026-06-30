import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

interface FAQItem {
  question: string;
  answer: string;
}

export default function FAQSection() {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  const faqs: FAQItem[] = [
    {
      question: 'How does TAXORA guarantee 100% mathematical and tax accuracy?',
      answer: 'We split our advisory system into two distinct parts: a probabilistic LLM chatbot for understanding your language, and a deterministic core tax engine (written in Python) for all math and tax slab calculations. The core engine applies strict statutory formulas (based on the Income Tax Act, 1961) for surcharges, rebates u/s 87A, and deductions, ensuring 100% mathematical precision that is fully auditable.'
    },
    {
      question: 'Are the updated post-Budget 2024 capital gains and slab rates supported?',
      answer: 'Yes. TAXORA is fully updated with the Finance (No. 2) Act, 2024 amendments (Budget 2024). This includes the new 20% STCG rate u/s 111A, the 12.5% flat LTCG rate u/s 112A/112 (without indexation), the increased ₹1,25,000 tax-free threshold for listed equities, and the revised slabs and ₹75,000 standard deduction under the New Regime (u/s 115BAC).'
    },
    {
      question: 'What documents can the smart scanner read and parse?',
      answer: 'Our document analysis pipeline can read salary Form 16, capital gains ledger spreadsheets, rent receipts, stock transaction summaries, and Section 80C/80D investment proofs. It supports text PDFs, scanned PDFs, and raw images (JPEG/PNG), extracting relevant financial figures automatically.'
    },
    {
      question: 'How does the legal search engine cite tax provisions?',
      answer: 'When you ask a legal or compliance question, our RAG (Retrieval-Augmented Generation) pipeline queries our structured database of the Income Tax Act, CBDT circulars, and notifications. The AI co-pilot extracts relevant clauses and provides direct, clickable statutory citations (e.g., Section 10(13A), Section 24(b)) in its CA advisory memos.'
    },
    {
      question: 'Can I legally claim HRA by paying rent to my parents?',
      answer: 'Yes, paying rent to parents is legally permissible u/s 10(13A) if they own the property and declare the rent as rental income in their tax returns. However, if the annual rent exceeds ₹1,00,000, you are strictly required to declare your parents PAN in Form 12BB. We recommend formalizing a rent agreement and executing transactions via bank transfers to satisfy audits.'
    },
    {
      question: 'Is my personal and financial data secure?',
      answer: 'Security is our core priority. All uploaded files and parsed outputs are encrypted at rest and in transit. Standard calculations are processed locally inside sandbox environments. Taxpayer PANs are masked, and we do not store raw document data longer than necessary to compile your optimization report.'
    }
  ];

  const toggleFAQ = (index: number) => {
    setActiveIndex(activeIndex === index ? null : index);
  };

  return (
    <section id="faq" className="w-full py-16 px-6 md:px-12 relative flex flex-col items-center justify-center">
      
      {/* Title Header */}
      <div className="text-center flex flex-col items-center gap-3 max-w-xl mb-16 relative z-10">
        <span className="text-xs font-semibold tracking-wider text-teal-400 uppercase">HELP & SUPPORT</span>
        <h2 className="text-3xl md:text-4xl font-bold text-white tracking-tight">
          Frequently Asked Questions
        </h2>
        <p className="text-sm text-slate-400 leading-relaxed mt-1">
          Have queries about slabs, regimes, or compliance? Review the answers below to see how TAXORA manages legal parameters.
        </p>
      </div>

      {/* FAQ Accordion container */}
      <div className="w-full max-w-3xl flex flex-col gap-4 relative z-10">
        {faqs.map((faq, idx) => {
          const isOpen = activeIndex === idx;

          return (
            <div
              key={idx}
              className="bg-slate-900/20 border border-slate-800/60 rounded-2xl overflow-hidden backdrop-blur-md transition-colors duration-300 hover:border-slate-700/50"
            >
              {/* Question toggle header button */}
              <button
                onClick={() => toggleFAQ(idx)}
                className="w-full py-5 px-6 flex items-center justify-between text-left focus:outline-none cursor-pointer group"
              >
                <span className="text-sm font-bold text-slate-200 group-hover:text-white transition-colors tracking-tight pr-4">
                  {faq.question}
                </span>
                <span className="shrink-0 p-1.5 rounded-lg bg-slate-950/40 border border-slate-850/50 text-slate-400 group-hover:text-white transition-colors">
                  <motion.div
                    animate={{ rotate: isOpen ? 180 : 0 }}
                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                  >
                    <ChevronDown className="h-4 w-4" />
                  </motion.div>
                </span>
              </button>

              {/* Collapsible Answer area */}
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    initial={{ height: 0 }}
                    animate={{ height: 'auto' }}
                    exit={{ height: 0 }}
                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                    className="overflow-hidden"
                  >
                    <div className="px-6 pb-6 pt-1 text-xs text-slate-400 leading-relaxed text-left border-t border-slate-900/60">
                      {faq.answer}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>

    </section>
  );
}
