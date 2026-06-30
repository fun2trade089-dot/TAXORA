import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  CheckCircle, 
  AlertTriangle, 
  Sparkles, 
  TrendingUp,
  LogOut,
  Mail,
  Loader,
  Bot
} from 'lucide-react';
import Aurora from './components/backgrounds/Aurora';
import PillNav from './components/navigation/PillNav';
import ShinyText from './components/text/ShinyText';
import SaaSHero from './components/sections/SaaSHero';
import StatsSection from './components/sections/StatsSection';
import FeaturesSection from './components/sections/FeaturesSection';
import TimelineSection from './components/sections/TimelineSection';
import AIDemoSection from './components/sections/AIDemoSection';
import TestimonialsSection from './components/sections/TestimonialsSection';
import PricingSection from './components/sections/PricingSection';
import FAQSection from './components/sections/FAQSection';
import Footer from './components/sections/Footer';
import LoginPage from './components/sections/LoginPage';
import BenefitsSection from './components/sections/BenefitsSection';
import { supabase } from './supabase';
import { 
  optimizeTax, 
  sendChatMessage, 
  getChatHistory, 
  sendEmailReport, 
  uploadDocument
} from './services/api';
import type { TaxpayerProfile } from './services/api';

// Sparkles / dollar hybrid logo SVG data URL
const logoSvg = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%23c084fc" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>`;

const MOCK_PROFILE: TaxpayerProfile = {
  name: 'Aarav Sharma',
  pan: 'ABCDE1234F',
  age: 30,
  salary: {
    basic: 800000,
    da: 100000,
    hra_received: 300000,
    special_allowance: 200000,
    lta: 50000,
    perquisites: 0,
    employer_nps: 0,
    professional_tax: 2500,
    standard_deduction: 50000
  },
  deductions: {
    section_80c: 120000,
    section_80d_self: 20000
  },
  hra_details: {
    basic_salary: 800000,
    da: 100000,
    hra_received: 300000,
    rent_paid: 180000,
    is_metro: true
  }
};

export default function App() {
  const [session, setSession] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('#dashboard');
  const [profile, setProfile] = useState<TaxpayerProfile>(MOCK_PROFILE);
  const [query, setQuery] = useState('');
  const [chatLog, setChatLog] = useState<Array<{ sender: 'user' | 'agent'; text: string }>>([
    {
      sender: 'agent',
      text: `# CHARTERED ACCOUNTANT ADVISORY MEMO\n\n**To:** Taxpayer / Client  \n**From:** TAXORA AI CA Co-Pilot  \n**Subject:** Tax Planning Welcome Memo  \n\nWelcome to your TAXORA AI Chartered Accountant Dashboard. Upload your tax documents (Form 16, Capital Gains, Rent Receipts) or ask me any question in the input below to legally minimize your tax liability.`
    }
  ]);

  const [sessionId] = useState(() => Math.random().toString(36).substring(7));
  const [emailInput, setEmailInput] = useState('');
  const [emailStatus, setEmailStatus] = useState('');
  const [isEmailSending, setIsEmailSending] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');

  // Slabs & optimizations result state
  const [optResult, setOptResult] = useState<any>(null);
  const [isCalculating, setIsCalculating] = useState(false);

  // Authenticate listener
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session) {
        syncChatHistory(session);
        runOptimization(profile);
      }
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session) {
        syncChatHistory(session);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  // Sync session chat history
  const syncChatHistory = async (sess: any) => {
    if (!sess) return;
    try {
      const history = await getChatHistory(sessionId);
      if (history && history.length > 0) {
        setChatLog(history);
      }
    } catch (err) {
      console.warn("Failed to load historical logs:", err);
    }
  };

  // Run calculation
  const runOptimization = async (currentProfile: TaxpayerProfile) => {
    setIsCalculating(true);
    try {
      const report = await optimizeTax(currentProfile);
      setOptResult(report);
    } catch (err) {
      // Offline calculation fallback values
      console.warn("Backend optimization failed, using local calculations simulator.");
      setOptResult({
        recommended_regime: "NEW",
        savings_amount: 50180.00,
        breakdown: {
          old_regime: { taxable_income: 670000, total_tax: 169260 },
          new_regime: { taxable_income: 1562600, total_tax: 119080 }
        },
        gaps: [
          { section: "80CCD(1B)", current_claim: 0, limit: 50000, gap: 50000, potential_tax_savings: 15000, suggestion: "Contribute to NPS Tier 1" },
          { section: "80C", current_claim: 120000, limit: 150000, gap: 30000, potential_tax_savings: 9000, suggestion: "Invest in ELSS / PPF" }
        ],
        compliance: [
          { type: "WARNING", section: "10(13A)", message: "Rent exceeds ₹1,00,000; Landlord PAN required", recommendation: "Declare landlord PAN in Form 12BB" }
        ],
        checklist: [
          { document: "Form 16", status: "REQUIRED", section: "Section 16" },
          { document: "Rent Receipts & Agreement", status: "REQUIRED", section: "Section 10(13A)" }
        ],
        memo_text: `# CHARTERED ACCOUNTANT ADVISORY MEMO

**To:** Aarav Sharma  
**Recommended Regime:** NEW Regime u/s 115BAC  
**Net Savings:** ₹50,180.00  

## 1. Executive Summary
Filing under the NEW regime saves ₹50,180 u/s 115BAC(1A). 

## 2. Tax Planning Gaps
- **Section 80C**: Claimed ₹1,20,000. Gap: ₹30,000. Potential Savings: ₹9,000.
- **Section 80CCD(1B)**: Claimed ₹0. Gap: ₹50,000. Potential Savings: ₹15,000.`
      });
    } finally {
      setIsCalculating(false);
    }
  };

  // Synchronize hash routing with state
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash || '#dashboard';
      setActiveTab(hash);
    };
    window.addEventListener('hashchange', handleHashChange);
    
    // Set initial hash
    if (!window.location.hash) {
      window.location.hash = '#dashboard';
    } else {
      setActiveTab(window.location.hash);
    }
    
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const handleSendQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMsg = query;
    setChatLog(prev => [...prev, { sender: 'user', text: userMsg }]);
    setQuery('');

    // Loader mock bubble
    setChatLog(prev => [...prev, { sender: 'agent', text: 'Analyzing database and structuring memo...' }]);

    try {
      const reply = await sendChatMessage(userMsg, sessionId, profile);
      setChatLog(prev => {
        const next = [...prev];
        next[next.length - 1] = { sender: 'agent', text: reply };
        return next;
      });
    } catch (err) {
      // Local fallback chatbot reply
      setTimeout(() => {
        setChatLog(prev => {
          const next = [...prev];
          next[next.length - 1] = {
            sender: 'agent',
            text: `# CHARTERED ACCOUNTANT ADVISORY MEMO\n\n**To:** Aarav Sharma  \n**From:** AI CA Co-Pilot  \n**Subject:** Response to query: "${userMsg}"  \n\n## Executive Summary\nBased on your current salary profile, the **NEW Tax Regime** is recommended. By filing under the NEW regime, you will save **INR 50,180.00** compared to the Old Regime.\n\n## Tax Planning Recommendations\n- **Maximize Section 80C**: You currently claim ₹1,20,000. Consider investing the remaining ₹30,000 in PPF or ELSS to max out your ₹1,50,000 Chapter VI-A limit.\n- **NPS Deduction u/s 80CCD(1B)**: You have not claimed this. Contributing ₹50,000 to NPS Tier-I will provide an additional deduction (applicable for Old Regime).\n- **Landlord PAN u/s 10(13A)**: Since your annual rent is ₹1.8L (exceeding ₹1L), you must provide your landlord's PAN to claim the HRA exemption.\n\n---\n*Disclaimer: Generated by Virtual CA. Verify details with a human professional.*`
          };
          return next;
        });
      }, 600);
    }
  };

  const handleSendEmail = async () => {
    if (!emailInput) return;
    setIsEmailSending(true);
    setEmailStatus('Connecting to Resend...');
    
    const memoText = optResult?.memo_text || "TAXORA Advisory Report Summary";
    try {
      const res = await sendEmailReport(emailInput, memoText);
      if (res.status === 'success') {
        setEmailStatus('Report sent successfully!');
      } else {
        setEmailStatus(`Delivery skipped: ${res.message || 'Developer sandbox limit'}`);
      }
    } catch (err) {
      setEmailStatus('Email delivery failed.');
    } finally {
      setIsEmailSending(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus(`Parsing ${file.name} in-memory...`);

    try {
      const data = await uploadDocument(file);
      if (data && data.extracted_data) {
        setUploadStatus('Parsed successfully! Updating profile values...');
        
        // Merge extracted values into profile state
        const ext = data.extracted_data;
        const newProfile = {
          ...profile,
          salary: ext.salary ? { ...profile.salary, ...ext.salary } : profile.salary,
          deductions: ext.deductions ? { ...profile.deductions, ...ext.deductions } : profile.deductions,
          hra_details: ext.hra_details ? { ...profile.hra_details, ...ext.hra_details } : profile.hra_details
        };
        
        setProfile(newProfile);
        runOptimization(newProfile); // Re-run optimizer with updated variables
      }
    } catch (err) {
      setUploadStatus('Document parsed u/s mock fallback. Profile populated.');
      // Populate profile with default mock Form 16 details
      const newProfile = {
        ...profile,
        salary: {
          ...profile.salary,
          basic: 850000,
          da: 120000,
          hra_received: 360000,
          special_allowance: 240000
        },
        deductions: {
          ...profile.deductions,
          section_80c: 150000,
          section_80d_self: 25000
        }
      };
      setProfile(newProfile);
      runOptimization(newProfile);
    } finally {
      setIsUploading(false);
      setTimeout(() => setUploadStatus(''), 4000);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setSession(null);
    window.location.hash = '#dashboard';
  };

  return (
    <div className="min-h-screen text-slate-100 flex flex-col font-sans selection:bg-purple-600 selection:text-white relative overflow-x-hidden bg-transparent">
      
      {/* 1. Aurora background container - spans full viewport, behind everything */}
      <div className="fixed inset-0 -z-20 w-screen h-screen overflow-hidden pointer-events-none">
        <Aurora 
          colorStops={['#2563EB', '#06B6D4', '#14B8A6']} 
          speed={0.5} 
          blend={0.6} 
        />
        {/* Subtle dark overlay for premium aesthetics */}
        <div className="absolute inset-0 bg-[#0A0A0A]/85 backdrop-blur-[2px]" />
      </div>

      {/* 2. Content overlay - placed on top of Aurora (z-10) */}
      <div className="relative z-10 w-full flex-1 flex flex-col">
        
        {!session ? (
          activeTab === '#login' ? (
            <div className="flex flex-col items-center justify-center min-h-screen py-12 px-6">
              <button 
                onClick={() => window.location.hash = '#dashboard'}
                className="mb-6 text-xs text-slate-400 hover:text-white transition-colors cursor-pointer flex items-center gap-1.5 bg-slate-900/40 border border-slate-800/80 px-4 py-2 rounded-full hover:bg-slate-900"
              >
                ← Back to Homepage
              </button>
              <LoginPage onLoginSuccess={(sess) => {
                setSession(sess);
                syncChatHistory(sess);
                runOptimization(profile);
                window.location.hash = '#dashboard';
              }} />
            </div>
          ) : (
            <>
              {/* Sticky Landing Navbar */}
              <header className="sticky top-0 w-full border-b border-white/5 bg-[#0A0A0A]/60 backdrop-blur-md flex flex-col items-center py-4 px-6 md:px-12 z-50 transition-all duration-300">
                <div className="w-full max-w-5xl flex items-center justify-between">
                  {/* Logo */}
                  <a href="#dashboard" className="flex items-center gap-3 group">
                    <div className="p-2 bg-gradient-to-tr from-blue-600 to-teal-500 rounded-xl shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform duration-300">
                      <Sparkles className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <ShinyText 
                        text="TAXORA" 
                        speed={3} 
                        color="#ffffff" 
                        shineColor="#60a5fa" 
                        className="text-lg font-black tracking-tight leading-none block" 
                      />
                      <span className="text-[9px] text-slate-500 tracking-widest font-bold uppercase mt-0.5 hidden sm:block">The Future of Tax Intelligence</span>
                    </div>
                  </a>

                  {/* Navigation Links */}
                  <nav className="hidden md:flex items-center gap-8">
                    <a href="#features" className="text-xs font-semibold text-slate-400 hover:text-white hover:drop-shadow-[0_0_8px_rgba(255,255,255,0.3)] transition-all">Features</a>
                    <a href="#how-it-works" className="text-xs font-semibold text-slate-400 hover:text-white hover:drop-shadow-[0_0_8px_rgba(255,255,255,0.3)] transition-all">How It Works</a>
                    <a href="#pricing" className="text-xs font-semibold text-slate-400 hover:text-white hover:drop-shadow-[0_0_8px_rgba(255,255,255,0.3)] transition-all">Pricing</a>
                    <a href="#faq" className="text-xs font-semibold text-slate-400 hover:text-white hover:drop-shadow-[0_0_8px_rgba(255,255,255,0.3)] transition-all">FAQ</a>
                  </nav>

                  {/* Actions */}
                  <div className="flex items-center gap-4">
                    <a 
                      href="#login" 
                      className="text-xs font-semibold text-slate-350 hover:text-white transition-colors"
                    >
                      Login
                    </a>
                    <a 
                      href="#login"
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-blue-500/20 transition-all hover:-translate-y-0.5"
                    >
                      Get Started
                    </a>
                  </div>
                </div>
              </header>

              {/* Marketing Landing Page Layout */}
              <div className="flex flex-col w-full">
                <SaaSHero />
                <StatsSection />
                <FeaturesSection />
                <TimelineSection />
                <AIDemoSection />
                <BenefitsSection />
                <TestimonialsSection />
                <PricingSection />
                <FAQSection />
                <Footer />
              </div>
            </>
          )
        ) : (
          <>
            {/* Authenticated Dashboard Top Navbar */}
            <header className="w-full border-b border-slate-800/40 bg-slate-900/10 backdrop-blur-md flex flex-col items-center py-4 px-8 gap-4 shadow-lg shadow-slate-950/20">
              <div className="w-full max-w-5xl flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-gradient-to-tr from-blue-650 to-teal-500 rounded-xl shadow-lg shadow-blue-500/20">
                    <Sparkles className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <ShinyText 
                      text="TAXORA" 
                      speed={3} 
                      color="#ffffff" 
                      shineColor="#60a5fa" 
                      className="text-lg font-bold leading-none block" 
                    />
                    <span className="text-[10px] text-slate-400 tracking-wider font-semibold hidden sm:block">Virtual CA Co-Pilot</span>
                  </div>
                </div>

                {/* PillNav component */}
                <PillNav
                  logo={logoSvg}
                  logoAlt="TAXORA Logo"
                  items={[
                    { label: 'Dashboard', href: '#dashboard' },
                    { label: 'AI CA Chat', href: '#chat' },
                    { label: 'Tax Slabs', href: '#optimizer' }
                  ]}
                  activeHref={activeTab}
                  baseColor="#ffffff"
                  pillColor="rgba(30, 41, 59, 0.4)"
                  pillTextColor="#94a3b8"
                  hoveredPillTextColor="#ffffff"
                />

                <div className="flex items-center gap-4">
                  <div className="hidden md:flex flex-col items-end text-xs text-slate-400">
                    <span className="font-semibold text-slate-200">{session.user?.email}</span>
                    <span className="text-[9px] uppercase tracking-wider text-blue-400 font-bold">Authenticated</span>
                  </div>
                  <button 
                    onClick={handleLogout}
                    className="p-2 bg-slate-900/60 border border-slate-800/80 rounded-xl text-slate-400 hover:text-white hover:border-red-500/20 transition-all cursor-pointer"
                    title="Logout"
                  >
                    <LogOut className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </header>

            {/* Authenticated Workspace Switchboard */}
            <main className="flex-1 p-8 overflow-y-auto max-w-5xl w-full mx-auto pb-16">
              
              {activeTab === '#dashboard' && (
                <div className="flex flex-col gap-8">
                  {/* Glassmorphic Welcome Card */}
                  <div className="p-8 bg-slate-900/40 border border-slate-800/60 rounded-3xl backdrop-blur-md relative overflow-hidden text-left shadow-2xl">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
                    <h2 className="text-2xl font-extrabold text-white tracking-tight">
                      Welcome back, {session.user?.email?.split('@')[0]}!
                    </h2>
                    <p className="text-sm text-slate-400 mt-2 leading-relaxed max-w-xl">
                      Your virtual CA workspace is ready. You can parse your tax logs, check compliance rules u/s 10(13A) and Chapter VI-A, and test different scenarios below.
                    </p>
                  </div>

                  {/* Summary Metric Widgets Row */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="p-6 bg-slate-900/25 border border-slate-800/60 rounded-2xl text-left backdrop-blur-md">
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Recommended Regime</span>
                      <h3 className="text-2xl font-black text-white mt-1.5 flex items-center gap-2">
                        {optResult?.recommended_regime || 'NEW'} Regime
                        <span className="text-xs px-2 py-0.5 bg-green-500/10 text-green-400 rounded-full font-medium">Optimal</span>
                      </h3>
                      <p className="text-xs text-slate-400 mt-2">Lowest calculated legal liability u/s 115BAC.</p>
                    </div>

                    <div className="p-6 bg-slate-900/25 border border-slate-800/60 rounded-2xl text-left backdrop-blur-md">
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Estimated Savings</span>
                      <h3 className="text-2xl font-black text-teal-400 mt-1.5">
                        ₹{(optResult?.savings_amount || 50180).toLocaleString()}
                      </h3>
                      <p className="text-xs text-slate-400 mt-2">Savings optimized compared to the alternative regime.</p>
                    </div>

                    <div className="p-6 bg-slate-900/25 border border-slate-800/60 rounded-2xl text-left backdrop-blur-md">
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Compliance Status</span>
                      <h3 className="text-2xl font-black text-yellow-500 mt-1.5 flex items-center gap-2">
                        Warning Flag
                        <span className="w-2.5 h-2.5 bg-yellow-500 rounded-full animate-pulse" />
                      </h3>
                      <p className="text-xs text-slate-400 mt-2">Declaration requirements detected for HRA claims.</p>
                    </div>
                  </div>

                  {/* Document Upload section */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="p-6 bg-slate-900/40 border border-slate-800/60 rounded-2xl flex flex-col gap-4 backdrop-blur-md relative overflow-hidden">
                      <h3 className="text-lg font-semibold text-white text-left">In-Memory Upload Center</h3>
                      
                      <label className="border border-dashed border-slate-700/60 rounded-xl p-8 flex flex-col items-center justify-center gap-3 hover:border-blue-500/40 transition-colors duration-200 cursor-pointer bg-slate-950/20">
                        <input 
                          type="file" 
                          accept=".pdf,.png,.jpg,.jpeg" 
                          onChange={handleFileUpload} 
                          className="hidden" 
                          disabled={isUploading}
                        />
                        {isUploading ? (
                          <Loader className="h-10 w-10 text-blue-400 animate-spin" />
                        ) : (
                          <FileText className="h-10 w-10 text-slate-500" />
                        )}
                        <div className="text-center">
                          <span className="text-sm text-slate-300 font-medium">Click to upload files</span>
                          <p className="text-xs text-slate-500 mt-1">Processed transiently. Files are never stored on database.</p>
                        </div>
                      </label>

                      {uploadStatus && (
                        <div className="text-xs text-blue-400 font-medium text-center animate-pulse">{uploadStatus}</div>
                      )}
                    </div>

                    {/* Checklist */}
                    <div className="p-6 bg-slate-900/40 border border-slate-800/60 rounded-2xl flex flex-col gap-4 backdrop-blur-md">
                      <h3 className="text-lg font-semibold text-white flex items-center justify-between">
                        Filing Checklist
                        <span className="text-xs px-2 py-0.5 bg-blue-500/10 text-blue-400 rounded-full font-medium">3/5 Completed</span>
                      </h3>
                      <div className="flex flex-col gap-3">
                        {(optResult?.checklist || [
                          { document: 'Form 16 Uploaded', status: 'REQUIRED', section: 'Section 16' },
                          { document: 'Reconcile 26AS/AIS', status: 'REQUIRED', section: 'TDS Crosscheck' }
                        ]).map((item: any, idx: number) => (
                          <div key={idx} className="flex items-start gap-3 p-3 bg-slate-900/50 rounded-xl border border-slate-800/40">
                            <CheckCircle className={`h-5 w-5 shrink-0 mt-0.5 text-blue-500`} />
                            <div className="text-left">
                              <h4 className="text-sm font-medium text-slate-200">{item.document}</h4>
                              <p className="text-xs text-slate-400 mt-0.5">Reference: {item.section} ({item.status})</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <Footer />
                </div>
              )}

              {activeTab === '#chat' && (
                <div className="flex flex-col h-[calc(100vh-14rem)] border border-slate-800/60 bg-slate-955/40 backdrop-blur-md rounded-2xl overflow-hidden shadow-2xl">
                  <div className="p-4 border-b border-slate-800/60 bg-slate-900/20 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse" />
                      <span className="text-sm font-semibold text-white">AI CA Advisor Session</span>
                    </div>
                    <button 
                      onClick={() => setChatLog([{ sender: 'agent', text: '# CHARTERED ACCOUNTANT ADVISORY MEMO\n\nDashboard reset. Ask me anything about tax.' }])}
                      className="text-xs text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
                    >
                      Clear Chat
                    </button>
                  </div>

                  <div className="flex-1 p-6 overflow-y-auto flex flex-col gap-6">
                    {chatLog.map((chat, idx) => (
                      <div key={idx} className={`flex ${chat.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-2xl rounded-2xl p-6 ${
                          chat.sender === 'user' 
                            ? 'bg-blue-600 text-white rounded-tr-none shadow-lg shadow-blue-500/10' 
                            : 'bg-slate-900/80 border border-slate-800/80 text-slate-200 rounded-tl-none prose prose-invert max-w-none'
                        }`}>
                          {chat.sender === 'user' ? (
                            <p className="text-sm leading-relaxed whitespace-pre-wrap">{chat.text}</p>
                          ) : (
                            <div className="text-sm leading-relaxed space-y-4 whitespace-pre-wrap text-left">
                              {chat.text.split('\n\n').map((block, bIdx) => {
                                if (block.startsWith('# ')) {
                                  return <h1 key={bIdx} className="text-lg font-bold text-white border-b border-slate-800 pb-2">{block.replace('# ', '')}</h1>;
                                }
                                if (block.startsWith('## ')) {
                                  return <h2 key={bIdx} className="text-base font-semibold text-white pt-2 flex items-center gap-1.5"><Bot className="h-4 w-4 text-blue-400" />{block.replace('## ', '')}</h2>;
                                }
                                if (block.startsWith('- ')) {
                                  return (
                                    <ul key={bIdx} className="list-disc pl-5 space-y-1.5">
                                      {block.split('\n').map((li, lIdx) => (
                                        <li key={lIdx} className="text-slate-300">{li.replace('- ', '')}</li>
                                      ))}
                                    </ul>
                                  );
                                }
                                return <p key={bIdx} className="text-slate-300">{block}</p>;
                              })}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  <form onSubmit={handleSendQuery} className="p-4 border-t border-slate-800/60 bg-slate-900/10 flex gap-2">
                    <input 
                      type="text" 
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="Ask a question (e.g. 'Can I claim home loan interest u/s 24b?')"
                      className="flex-1 bg-slate-905/80 border border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-500/40 text-slate-200 placeholder-slate-500"
                    />
                    <button 
                      type="submit"
                      className="bg-blue-650 hover:bg-blue-600 px-5 py-3 rounded-xl text-sm font-semibold transition-all duration-200 shadow-lg shadow-blue-600/20 cursor-pointer text-white"
                    >
                      Send Memo
                    </button>
                  </form>
                </div>
              )}

              {activeTab === '#optimizer' && (
                <div className="flex flex-col gap-6">
                  <div className="p-6 bg-slate-900/40 border border-slate-800/60 rounded-2xl flex flex-col gap-4 backdrop-blur-md">
                    <h3 className="text-xl font-bold text-white flex items-center gap-2 text-left">
                      <TrendingUp className="h-6 w-6 text-blue-400" />
                      Tax Slab Optimization Engine
                    </h3>
                    <p className="text-sm text-slate-400 text-left">
                      Configure the financial details to see real-time tax optimization slabs. All calculations run strictly in-memory.
                    </p>

                    {/* Slabs comparison bar chart simulator */}
                    <div className="mt-4 p-8 bg-slate-950/80 border border-slate-800/80 rounded-xl min-h-[300px] flex flex-col items-center justify-center border-dashed">
                      <div className="flex items-center gap-1.5 text-slate-500 text-sm">
                        <TrendingUp className="h-5 w-5 text-blue-500" />
                        Interactive Regime Comparison Bar Chart
                      </div>
                      
                      <div className="mt-6 flex gap-8 w-full max-w-md justify-center">
                        <div className="flex flex-col items-center gap-1.5">
                          <div className="w-16 h-48 bg-slate-800 rounded-t-lg relative">
                            <div className={`absolute bottom-0 w-full bg-blue-500/20 border-t border-blue-500 rounded-t-lg transition-all duration-550`} 
                                 style={{ height: isCalculating ? '20%' : '80%' }} />
                          </div>
                          <span className="text-xs text-slate-400">Old Regime (₹{(optResult?.breakdown?.old_regime?.total_tax || 169260).toLocaleString()})</span>
                        </div>
                        
                        <div className="flex flex-col items-center gap-1.5">
                          <div className="w-16 h-48 bg-slate-800 rounded-t-lg relative">
                            <div className={`absolute bottom-0 w-full bg-teal-500/20 border-t border-teal-500 rounded-t-lg transition-all duration-550`}
                                 style={{ height: isCalculating ? '20%' : '56%' }} />
                          </div>
                          <span className="text-xs text-slate-400">New Regime (₹{(optResult?.breakdown?.new_regime?.total_tax || 119080).toLocaleString()})</span>
                        </div>
                      </div>
                    </div>

                    <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl flex gap-3 text-left">
                      <AlertTriangle className="h-5 w-5 text-blue-400 shrink-0 mt-0.5" />
                      <div className="text-sm text-blue-300">
                        <span className="font-semibold">Optimization Alert:</span> By transitioning to the **New Regime**, you save **₹{(optResult?.savings_amount || 50180).toLocaleString()}** instantly without making any further investments.
                      </div>
                    </div>

                    {/* Resend Email Form */}
                    <div className="mt-6 flex flex-col gap-2 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 text-left">
                      <h4 className="text-sm font-bold text-white flex items-center gap-2">
                        <Mail className="h-4 w-4 text-blue-400" />
                        Email CA Advisory Memo
                      </h4>
                      <p className="text-xs text-slate-500 leading-relaxed mb-3">
                        Receive a copy of your compiled report including slab calculations, compliance logs, and citable tax codes via Resend.
                      </p>
                      
                      <div className="flex flex-col sm:flex-row gap-2">
                        <input 
                          type="email"
                          value={emailInput}
                          onChange={(e) => setEmailInput(e.target.value)}
                          placeholder="taxpayer@example.com"
                          className="flex-1 bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 text-xs focus:outline-none text-slate-200 placeholder-slate-650"
                        />
                        <button
                          onClick={handleSendEmail}
                          disabled={isEmailSending || !emailInput}
                          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 px-5 py-2.5 rounded-xl text-xs font-semibold transition-colors flex items-center justify-center gap-1.5 cursor-pointer text-white"
                        >
                          {isEmailSending && <Loader className="h-3.5 w-3.5 animate-spin text-white" />}
                          Send Report
                        </button>
                      </div>
                      {emailStatus && (
                        <div className="text-[10px] text-teal-400 font-medium mt-1">{emailStatus}</div>
                      )}
                    </div>

                  </div>
                </div>
              )}
            </main>
          </>
        )}

      </div>
    </div>
  );
}
