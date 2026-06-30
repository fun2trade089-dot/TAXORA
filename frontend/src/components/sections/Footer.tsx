import { 
  Mail, 
  MapPin, 
  Phone 
} from 'lucide-react';
import ShinyText from '../text/ShinyText';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="w-full border-t border-slate-900 bg-slate-950/40 backdrop-blur-md pt-16 pb-8 px-6 md:px-12 relative z-10">
      <div className="w-full max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-12 gap-8 md:gap-12 text-left mb-12">
        
        {/* Brand Column (4/12 cols) */}
        <div className="md:col-span-5 flex flex-col gap-4">
          <div className="flex items-center gap-2">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="#c084fc" 
              strokeWidth="2.5" 
              strokeLinecap="round" 
              strokeLinejoin="round"
              className="h-6 w-6"
            >
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
            </svg>
            <span className="text-base font-extrabold text-white tracking-tight">
              <ShinyText text="TAXORA" speed={4} shineColor="#c084fc" color="#ffffff" className="inline" />
            </span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed max-w-sm">
            The Future of Tax Intelligence. The first RAG-powered Virtual CA co-pilot integrated with a deterministic tax engine for AY 2025-26.
          </p>
          {/* Social icons */}
          <div className="flex items-center gap-3.5 mt-2">
            <a 
              href="https://twitter.com" 
              target="_blank" 
              rel="noreferrer"
              className="p-2 bg-slate-900/60 border border-slate-800/80 rounded-lg text-slate-400 hover:text-white hover:border-blue-500/20 transition-all cursor-pointer"
              aria-label="Twitter"
            >
              <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
              </svg>
            </a>
            <a 
              href="https://github.com" 
              target="_blank" 
              rel="noreferrer"
              className="p-2 bg-slate-900/60 border border-slate-800/80 rounded-lg text-slate-400 hover:text-white hover:border-blue-500/20 transition-all cursor-pointer"
              aria-label="GitHub"
            >
              <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
                <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
              </svg>
            </a>
            <a 
              href="https://linkedin.com" 
              target="_blank" 
              rel="noreferrer"
              className="p-2 bg-slate-900/60 border border-slate-800/80 rounded-lg text-slate-400 hover:text-white hover:border-blue-500/20 transition-all cursor-pointer"
              aria-label="LinkedIn"
            >
              <svg className="h-4 w-4 fill-current" viewBox="0 0 24 24">
                <path fillRule="evenodd" d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
              </svg>
            </a>
          </div>
        </div>

        {/* Quick Links Column (2/12 cols) */}
        <div className="md:col-span-3 flex flex-col gap-4">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Quick Links</span>
          <ul className="flex flex-col gap-2.5 text-xs text-slate-400">
            <li>
              <a href="#top" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} className="hover:text-white transition-colors cursor-pointer">Homepage</a>
            </li>
            <li>
              <a href="#demo" onClick={(e) => {
                e.preventDefault();
                document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' });
              }} className="hover:text-white transition-colors cursor-pointer font-medium text-blue-400">Try AI Simulator</a>
            </li>
            <li>
              <a href="#demo" onClick={(e) => {
                e.preventDefault();
                document.getElementById('demo')?.scrollIntoView({ behavior: 'smooth' });
              }} className="hover:text-white transition-colors cursor-pointer">CA Chat Session</a>
            </li>
            <li>
              <a href="#how-it-works" onClick={(e) => {
                e.preventDefault();
                document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' });
              }} className="hover:text-white transition-colors cursor-pointer">Filing Checklist</a>
            </li>
          </ul>
        </div>

        {/* Resources Column (2.5/12 cols) */}
        <div className="md:col-span-3 flex flex-col gap-4">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Legal References</span>
          <ul className="flex flex-col gap-2.5 text-xs text-slate-400">
            <li>
              <a href="#faq" onClick={(e) => {
                e.preventDefault();
                document.getElementById('faq')?.scrollIntoView({ behavior: 'smooth' });
              }} className="hover:text-white transition-colors cursor-pointer">Section 80C Guide</a>
            </li>
            <li>
              <a href="#faq" onClick={(e) => {
                e.preventDefault();
                document.getElementById('faq')?.scrollIntoView({ behavior: 'smooth' });
              }} className="hover:text-white transition-colors cursor-pointer">HRA Exemption Rules</a>
            </li>
            <li>
              <a href="#pricing" onClick={(e) => {
                e.preventDefault();
                document.getElementById('pricing')?.scrollIntoView({ behavior: 'smooth' });
              }} className="hover:text-white transition-colors cursor-pointer">Budget 2024 Slabs</a>
            </li>
            <li>
              <a href="#features" onClick={(e) => {
                e.preventDefault();
                document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
              }} className="hover:text-white transition-colors cursor-pointer">Capital Gains u/s 112A</a>
            </li>
          </ul>
        </div>

        {/* Contact Column (2/12 cols) */}
        <div className="md:col-span-2 flex flex-col gap-4">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Contact</span>
          <ul className="flex flex-col gap-3 text-xs text-slate-400">
            <li className="flex items-center gap-2">
              <Mail className="h-3.5 w-3.5 text-slate-500" />
              <a href="mailto:info@taxora.ai" className="hover:text-white transition-colors cursor-pointer">info@taxora.ai</a>
            </li>
            <li className="flex items-center gap-2">
              <Phone className="h-3.5 w-3.5 text-slate-500" />
              <span className="cursor-default">+91 1800-TAX-ORA</span>
            </li>
            <li className="flex items-start gap-2">
              <MapPin className="h-3.5 w-3.5 text-slate-500 shrink-0 mt-0.5" />
              <span className="cursor-default text-left leading-relaxed">Indiranagar, Bengaluru, India</span>
            </li>
          </ul>
        </div>

      </div>

      {/* Footer Bottom copyright bar */}
      <div className="w-full max-w-5xl mx-auto border-t border-slate-900 pt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <span className="text-xs text-slate-500">
          © {currentYear} TAXORA. All rights reserved.
        </span>
        <div className="flex items-center gap-6 text-xs text-slate-500">
          <a href="#faq" onClick={(e) => {
            e.preventDefault();
            document.getElementById('faq')?.scrollIntoView({ behavior: 'smooth' });
          }} className="hover:text-slate-355 transition-colors cursor-pointer">Privacy Policy</a>
          <a href="#faq" onClick={(e) => {
            e.preventDefault();
            document.getElementById('faq')?.scrollIntoView({ behavior: 'smooth' });
          }} className="hover:text-slate-355 transition-colors cursor-pointer">Terms of Service</a>
          <a href="#faq" onClick={(e) => {
            e.preventDefault();
            document.getElementById('faq')?.scrollIntoView({ behavior: 'smooth' });
          }} className="hover:text-slate-355 transition-colors cursor-pointer">Disclaimer</a>
        </div>
      </div>

    </footer>
  );
}
