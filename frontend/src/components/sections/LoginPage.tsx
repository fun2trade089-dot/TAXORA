import React, { useState } from 'react';
import { supabase } from '../../supabase';
import BorderBeam from '../ui/BorderBeam';
import ShinyText from '../text/ShinyText';
import { Mail, Lock, ShieldAlert, Sparkles, Loader } from 'lucide-react';

interface LoginPageProps {
  onLoginSuccess: (session: any) => void;
}

export default function LoginPage({ onLoginSuccess }: LoginPageProps) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setInfoMessage(null);
    if (!email || !password) return;

    setLoading(true);
    try {
      if (isSignUp) {
        const { data, error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        if (data?.session) {
          onLoginSuccess(data.session);
        } else {
          setInfoMessage("Registration successful! Please check your email inbox to confirm your account verification link.");
        }
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        if (data?.session) {
          onLoginSuccess(data.session);
        }
      }
    } catch (err: any) {
      setErrorMessage(err.message || "An authentication error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleAuth = async () => {
    setErrorMessage(null);
    setInfoMessage(null);
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: window.location.origin
        }
      });
      if (error) throw error;
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to initialize Google Login.");
    }
  };

  // Mock offline test bypass
  const handleOfflineBypass = () => {
    onLoginSuccess({
      access_token: 'mock-offline-token',
      user: {
        id: 'mock-uuid',
        email: email || 'aarav.sharma@example.com',
      }
    });
  };

  return (
    <div className="min-h-[calc(100vh-6rem)] flex items-center justify-center py-12 px-6 relative overflow-hidden">
      
      {/* Background gradients */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-purple-650/10 rounded-full blur-3xl pointer-events-none z-0" />
      
      <div className="relative z-10 w-full max-w-md bg-slate-900/30 border border-slate-800/80 rounded-3xl shadow-2xl backdrop-blur-xl p-8 overflow-hidden group select-none">
        
        {/* Border Beam decoration */}
        <BorderBeam 
          size={160} 
          duration={6} 
          borderWidth={2} 
          colorFrom="#a855f7" 
          colorTo="#3b82f6" 
        />

        {/* Brand Logo Header */}
        <div className="flex flex-col items-center gap-3 text-center mb-8">
          <div className="p-3 bg-gradient-to-tr from-purple-500/20 to-blue-500/20 border border-purple-500/30 rounded-2xl shadow-inner">
            <Sparkles className="h-6 w-6 text-purple-400" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight">
              <ShinyText text="TAXORA" speed={4} shineColor="#c084fc" color="#ffffff" className="inline" />
            </h1>
            <p className="text-xs text-slate-400 mt-1.5 font-medium tracking-wide uppercase">
              The Future of Tax Intelligence
            </p>
          </div>
        </div>

        {/* Message banners */}
        {errorMessage && (
          <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex gap-3 text-left mb-6">
            <ShieldAlert className="h-5 w-5 text-red-400 shrink-0 mt-0.5" />
            <div className="text-xs text-red-300 leading-normal">{errorMessage}</div>
          </div>
        )}

        {infoMessage && (
          <div className="p-4 bg-purple-500/10 border border-purple-500/20 rounded-xl flex gap-3 text-left mb-6">
            <Sparkles className="h-5 w-5 text-purple-400 shrink-0 mt-0.5" />
            <div className="text-xs text-purple-300 leading-normal">{infoMessage}</div>
          </div>
        )}

        {/* Credentials Form */}
        <form onSubmit={handleEmailAuth} className="flex flex-col gap-4 text-left">
          
          {/* Email Input */}
          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] text-slate-400 font-bold uppercase tracking-wider pl-1">Email Address</label>
            <div className="relative">
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-11 pr-4 py-3 text-sm focus:outline-none focus:border-purple-500/40 text-slate-200"
              />
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            </div>
          </div>

          {/* Password Input */}
          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] text-slate-400 font-bold uppercase tracking-wider pl-1">Password</label>
            <div className="relative">
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl pl-11 pr-4 py-3 text-sm focus:outline-none focus:border-purple-500/40 text-slate-200"
              />
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            </div>
          </div>

          {/* Submit Action Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-semibold text-xs rounded-xl flex items-center justify-center gap-2 transition-all duration-300 shadow shadow-purple-500/20 cursor-pointer"
          >
            {loading ? (
              <Loader className="h-4 w-4 animate-spin text-white" />
            ) : (
              <span>{isSignUp ? 'Sign Up with Email' : 'Login with Email'}</span>
            )}
          </button>
        </form>

        {/* Divider */}
        <div className="relative flex items-center justify-center my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-800" />
          </div>
          <span className="relative px-3 bg-slate-950/20 text-[10px] text-slate-500 font-bold uppercase tracking-wider backdrop-blur-md">
            OR CONTINUE WITH
          </span>
        </div>

        {/* OAuth Buttons */}
        <div className="flex flex-col gap-3">
          <button
            onClick={handleGoogleAuth}
            className="w-full py-3 bg-slate-950/60 hover:bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl flex items-center justify-center gap-3 text-xs font-semibold text-slate-200 transition-all duration-300 cursor-pointer"
          >
            {/* Google Logo G SVG */}
            <svg className="h-4 w-4 shrink-0" viewBox="0 0 24 24">
              <path
                fill="#EA4335"
                d="M5.266 9.765A7.077 7.077 0 0112 4.909c1.69 0 3.218.6 4.418 1.582l3.51-3.51C17.764.95 14.982 0 12 0 7.355 0 3.307 2.673 1.34 6.573l3.926 3.192z"
              />
              <path
                fill="#4285F4"
                d="M23.49 12.273c0-.818-.073-1.609-.209-2.373H12v4.509h6.445a5.506 5.506 0 01-2.39 3.618l3.782 2.927c2.21-2.036 3.655-5.036 3.655-8.682z"
              />
              <path
                fill="#34A853"
                d="M12 24c3.24 0 5.955-1.073 7.936-2.918l-3.782-2.927c-1.045.7-2.382 1.118-4.154 1.118-3.2 0-5.918-2.155-6.882-5.055L1.192 17.31A11.968 11.968 0 0012 24z"
              />
              <path
                fill="#FBBC05"
                d="M5.118 14.218a7.148 7.148 0 010-4.455l-3.926-3.19A11.972 11.972 0 000 12c0 1.918.455 3.727 1.255 5.345l3.863-3.127z"
              />
            </svg>
            Sign in with Google
          </button>

          {/* Local Developer Test Bypass Option */}
          <button
            onClick={handleOfflineBypass}
            className="w-full text-slate-500 hover:text-slate-400 text-[10px] tracking-wide font-medium transition-colors underline cursor-pointer"
          >
            Offline developer bypass (run mock dashboard session)
          </button>
        </div>

        {/* Toggle link */}
        <div className="mt-8 text-center">
          <button
            onClick={() => setIsSignUp(!isSignUp)}
            className="text-xs text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            {isSignUp ? (
              <span>Already have an account? <strong className="text-purple-400 font-bold underline">Login</strong></span>
            ) : (
              <span>Don't have an account? <strong className="text-purple-400 font-bold underline">Create one</strong></span>
            )}
          </button>
        </div>

      </div>
    </div>
  );
}
