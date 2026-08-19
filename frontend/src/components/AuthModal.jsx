// frontend/src/components/AuthModal.jsx

import React, { useState } from 'react';
import { 
  Eye, 
  EyeOff, 
  ArrowRight, 
  Sparkles, 
  X, 
  ShieldCheck, 
  LogOut
} from 'lucide-react';

export default function AuthModal({ currentUser, onLoginSuccess, onLogout, onClose }) {
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [username, setUsername] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const endpoint = mode === 'register' 
      ? 'http://127.0.0.1:8000/api/auth/register' 
      : 'http://127.0.0.1:8000/api/auth/login';
      
    const payload = mode === 'register'
      ? { username: username.trim(), display_name: displayName.trim(), password }
      : { username: username.trim(), password };

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Authentication failed.');
      }

      onLoginSuccess({
        user_id: data.user_id,
        user_name: data.display_name,
        handle: data.username,
      });
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemoSelect = (uname, dname) => {
    setUsername(uname);
    setDisplayName(dname);
    setPassword('password123');
    setMode('login');
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-[#18181b] border border-[#27272a] rounded-3xl w-full max-w-4xl overflow-hidden grid grid-cols-1 md:grid-cols-2 shadow-2xl relative min-h-[520px]">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 p-2 text-slate-400 hover:text-white rounded-full bg-slate-900/60 border border-slate-700/60 hover:bg-slate-800 transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Left Panel: Hero Banner */}
        <div className="relative bg-gradient-to-br from-indigo-950 via-slate-900 to-[#101014] p-8 md:p-10 flex flex-col justify-between overflow-hidden border-r border-[#27272a]">
          <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
          
          <div className="space-y-3 z-10">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[11px] font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Competitive Engine v4.0</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              CodeArena
            </h2>
          </div>

          <div className="space-y-4 z-10 my-auto py-8">
            <div className="space-y-2">
              <h3 className="text-xl font-bold text-white leading-snug">
                Master Algorithms.<br />Compete in Live Contests.
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Benchmark execution telemetry, trace AST similarity fingerprints, and track problem milestones.
              </p>
            </div>

            {/* Quick Demo Credentials */}
            <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-2xl space-y-2 text-xs">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider block">
                Quick Demo Accounts (pw: password123)
              </span>
              <div className="flex flex-wrap gap-1.5">
                <button
                  type="button"
                  onClick={() => handleQuickDemoSelect('suman', 'Suman')}
                  className="px-2.5 py-1 bg-slate-800 hover:bg-indigo-600/30 text-indigo-300 rounded-lg text-[11px] font-mono transition-colors cursor-pointer border border-slate-700"
                >
                  @suman
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickDemoSelect('alex', 'Alex Developer')}
                  className="px-2.5 py-1 bg-slate-800 hover:bg-indigo-600/30 text-indigo-300 rounded-lg text-[11px] font-mono transition-colors cursor-pointer border border-slate-700"
                >
                  @alex
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickDemoSelect('priya', 'Priya Sharma')}
                  className="px-2.5 py-1 bg-slate-800 hover:bg-indigo-600/30 text-indigo-300 rounded-lg text-[11px] font-mono transition-colors cursor-pointer border border-slate-700"
                >
                  @priya
                </button>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2 z-10 text-[11px] text-slate-500 font-mono">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Encrypted SQLite Persistent Auth</span>
          </div>
        </div>

        {/* Right Panel: Form */}
        <div className="p-8 md:p-10 flex flex-col justify-between bg-[#18181b]">
          <div>
            <div className="space-y-1 mb-6">
              <h3 className="text-xl font-extrabold text-white">
                {mode === 'register' ? 'Create an account' : 'Welcome back'}
              </h3>
              <p className="text-xs text-slate-400">
                {mode === 'register' ? 'Already have an account? ' : "Don't have an account? "}
                <button
                  type="button"
                  onClick={() => { setMode(mode === 'register' ? 'login' : 'register'); setError(''); }}
                  className="text-indigo-400 hover:text-indigo-300 font-semibold cursor-pointer underline"
                >
                  {mode === 'register' ? 'Log in' : 'Create account'}
                </button>
              </p>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-xs">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {mode === 'register' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">Full Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Suman Panigrahi"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    className="w-full bg-[#121214] border border-[#2e2e33] focus:border-indigo-500 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none transition-colors"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Username (Handle)</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. suman"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-[#121214] border border-[#2e2e33] focus:border-indigo-500 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none transition-colors font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-[#121214] border border-[#2e2e33] focus:border-indigo-500 rounded-xl pl-3.5 pr-10 py-2.5 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none transition-colors"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300 cursor-pointer"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 rounded-xl text-xs transition-all shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2 cursor-pointer disabled:opacity-50"
              >
                <span>{loading ? 'Processing...' : mode === 'register' ? 'Create account' : 'Sign in'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
          </div>

          {/* Session Footer */}
          {currentUser && (
            <div className="mt-6 pt-4 border-t border-[#27272a] flex items-center justify-between text-xs">
              <div className="flex items-center space-x-2">
                <div className="w-6 h-6 rounded-full bg-indigo-600/20 text-indigo-400 font-bold text-[10px] flex items-center justify-center border border-indigo-500/30">
                  {currentUser.user_name ? currentUser.user_name.charAt(0) : 'U'}
                </div>
                <span className="text-slate-400">Signed in as <strong className="text-slate-200">{currentUser.user_name}</strong></span>
              </div>
              <button
                type="button"
                onClick={() => {
                  onLogout();
                  onClose();
                }}
                className="text-red-400 hover:text-red-300 font-semibold flex items-center space-x-1 cursor-pointer"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Log out</span>
              </button>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}