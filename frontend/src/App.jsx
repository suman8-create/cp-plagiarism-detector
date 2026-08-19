// frontend/src/App.jsx

import React, { useState, useEffect } from 'react';
import { 
  Upload, 
  FileCode, 
  Sparkles, 
  ArrowRight, 
  RefreshCw, 
  AlertCircle, 
  ShieldCheck, 
  Bot, 
  Trophy, 
  User, 
  Check, 
  Flame, 
  Search,
  CheckCircle2,
  LogOut,
  LogIn,
  UserPlus
} from 'lucide-react';
import DiffViewer from './components/DiffViewer';
import ProblemWorkspace from './components/ProblemWorkspace';
import ContestHub from './components/ContestHub';
import ProfileDashboard from './components/ProfileDashboard';

const DEFAULT_USER = {
  user_id: 'std_suman_01',
  user_name: 'Suman',
  handle: '@suman'
};

export default function App() {
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem('cp_active_user');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    return DEFAULT_USER;
  });

  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login'); // 'login' | 'register'
  const [authUsername, setAuthUsername] = useState('');
  const [authDisplayName, setAuthDisplayName] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);

  // 'problems' | 'contests' | 'profile' | 'quick_scan' | 'problem_workspace'
  const [currentView, setCurrentView] = useState('problems');
  
  const [problems, setProblems] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState('All Topics');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProblemSlug, setSelectedProblemSlug] = useState(null);
  const [activeContestId, setActiveContestId] = useState(null);
  const [activeContestTitle, setActiveContestTitle] = useState(null);
  const [loadingProblems, setLoadingProblems] = useState(false);

  // Ad-Hoc Scanner State
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [activeComparison, setActiveComparison] = useState(null);

  useEffect(() => {
    localStorage.setItem('cp_active_user', JSON.stringify(currentUser));
  }, [currentUser]);

  const fetchProblems = async () => {
    try {
      setLoadingProblems(true);
      const res = await fetch(`http://127.0.0.1:8000/api/problems?user_id=${currentUser.user_id}`);
      if (res.ok) {
        const data = await res.json();
        setProblems(data);
      }
    } catch (err) {
      console.error('Failed to load problems:', err);
    } finally {
      setLoadingProblems(false);
    }
  };

  useEffect(() => {
    fetchProblems();
  }, [currentUser]);

  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    setAuthError('');
    setAuthLoading(true);

    const endpoint = authMode === 'register' ? 'http://127.0.0.1:8000/api/auth/register' : 'http://127.0.0.1:8000/api/auth/login';
    const payload = authMode === 'register'
      ? { username: authUsername, display_name: authDisplayName, password: authPassword }
      : { username: authUsername, password: authPassword };

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }

      const activeUserObj = {
        user_id: data.user_id,
        user_name: data.display_name,
        handle: data.username,
      };

      setCurrentUser(activeUserObj);
      setShowAuthModal(false);
      setAuthUsername('');
      setAuthDisplayName('');
      setAuthPassword('');
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('cp_active_user');
    setCurrentUser(DEFAULT_USER);
  };

  const handleQuickUpload = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least 2 .cpp files or a .zip file.');
      return;
    }

    setAnalyzing(true);
    setError('');

    const formData = new FormData();
    selectedFiles.forEach((file) => formData.append('files', file));

    try {
      const response = await fetch('http://127.0.0.1:8000/api/check-plagiarism', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to analyze files.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to connect to backend.');
    } finally {
      setAnalyzing(false);
    }
  };

  const topicsList = ['All Topics', 'Array', 'String', 'Hash Table', 'Math', 'Dynamic Programming', 'Simulation'];

  const filteredProblems = problems.filter((p) => {
    const matchesSearch = p.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTopic = selectedTopic === 'All Topics' || (p.topic_tags && p.topic_tags.includes(selectedTopic));
    return matchesSearch && matchesTopic;
  });

  return (
    <div className="min-h-screen bg-[#121212] text-slate-100 font-sans">
      
      {/* Top Header */}
      <header className="border-b border-[#282828] bg-[#1a1a1a] px-6 py-2.5 sticky top-0 z-40">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-2 font-extrabold text-sm text-amber-500 cursor-pointer" onClick={() => setCurrentView('problems')}>
              <span className="text-lg">⚡</span>
              <span className="text-white tracking-tight">Code<span className="text-amber-500">Arena</span></span>
            </div>

            <nav className="flex items-center space-x-6 text-xs font-semibold">
              <button
                onClick={() => { setCurrentView('problems'); setSelectedProblemSlug(null); }}
                className={`transition-colors cursor-pointer ${currentView === 'problems' || currentView === 'problem_workspace' ? 'text-white border-b-2 border-amber-500 pb-1 mt-1' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Problems
              </button>
              <button
                onClick={() => { setCurrentView('contests'); setSelectedProblemSlug(null); }}
                className={`transition-colors cursor-pointer ${currentView === 'contests' ? 'text-white border-b-2 border-amber-500 pb-1 mt-1' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Contests
              </button>
              <button
                onClick={() => { setCurrentView('profile'); setSelectedProblemSlug(null); }}
                className={`transition-colors cursor-pointer ${currentView === 'profile' ? 'text-white border-b-2 border-amber-500 pb-1 mt-1' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Profile
              </button>
              <button
                onClick={() => { setCurrentView('quick_scan'); setSelectedProblemSlug(null); }}
                className={`transition-colors cursor-pointer ${currentView === 'quick_scan' ? 'text-white border-b-2 border-amber-500 pb-1 mt-1' : 'text-slate-400 hover:text-slate-200'}`}
              >
                Integrity Scanner
              </button>
            </nav>
          </div>

          <div className="flex items-center space-x-4 text-xs">
            <div className="flex items-center space-x-1 text-amber-500 font-mono font-bold bg-[#262626] px-2.5 py-1 rounded-full border border-[#333]">
              <Flame className="w-3.5 h-3.5 fill-amber-500" />
              <span>0</span>
            </div>

            {/* User Account Controls */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowAuthModal(true)}
                className="flex items-center space-x-2 bg-[#262626] hover:bg-[#333] border border-[#333] px-3 py-1.5 rounded-xl cursor-pointer transition-colors"
              >
                <div className="w-5 h-5 rounded-full bg-amber-600 text-white font-bold text-[10px] flex items-center justify-center">
                  {currentUser.user_name.charAt(0)}
                </div>
                <div className="text-left">
                  <span className="font-semibold text-slate-200 text-xs block leading-tight">{currentUser.user_name}</span>
                  <span className="text-[10px] font-mono text-slate-500 block leading-tight">{currentUser.handle}</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Page Content */}
      <main className="max-w-6xl mx-auto p-6 md:p-8">
        
        {/* VIEW 1: Problems Table */}
        {currentView === 'problems' && (
          <div className="space-y-6">
            
            {/* Topic Pills */}
            <div className="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-none text-xs">
              {topicsList.map((topic) => (
                <button
                  key={topic}
                  onClick={() => setSelectedTopic(topic)}
                  className={`px-3.5 py-1.5 rounded-full font-medium transition-colors shrink-0 cursor-pointer ${
                    selectedTopic === topic
                      ? 'bg-slate-100 text-slate-900 font-bold'
                      : 'bg-[#222] text-slate-400 hover:bg-[#2a2a2a] hover:text-slate-200 border border-[#333]'
                  }`}
                >
                  {topic}
                </button>
              ))}
            </div>

            {/* Search Bar */}
            <div className="relative max-w-sm">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search questions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#1e1e1e] border border-[#2e2e2e] rounded-xl pl-9 pr-4 py-2 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>

            {/* Problem Table */}
            <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-2xl overflow-hidden shadow-xl">
              {loadingProblems ? (
                <div className="p-12 text-center text-xs text-slate-500">
                  Loading problem library...
                </div>
              ) : filteredProblems.length === 0 ? (
                <div className="p-12 text-center text-xs text-slate-500">
                  No problems found.
                </div>
              ) : (
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-[#2a2a2a] bg-[#171717] text-slate-400 font-mono text-[11px]">
                      <th className="py-3 px-4 w-12 text-center">Status</th>
                      <th className="py-3 px-4">Title</th>
                      <th className="py-3 px-4 text-center">Acceptance</th>
                      <th className="py-3 px-4 text-center">Difficulty</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#2a2a2a]">
                    {filteredProblems.map((prob, idx) => (
                      <tr
                        key={prob.problem_id}
                        onClick={() => { setSelectedProblemSlug(prob.slug); setCurrentView('problem_workspace'); }}
                        className="hover:bg-[#252525] transition-colors cursor-pointer group"
                      >
                        <td className="py-3.5 px-4 text-center">
                          {prob.is_solved ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-400 mx-auto" />
                          ) : (
                            <span className="text-slate-700 font-mono">-</span>
                          )}
                        </td>

                        <td className="py-3.5 px-4">
                          <span className="font-semibold text-slate-200 group-hover:text-amber-400 transition-colors">
                            {idx + 1}. {prob.title}
                          </span>
                        </td>

                        <td className="py-3.5 px-4 text-center font-mono text-slate-400">
                          {prob.acceptance_rate}%
                        </td>

                        <td className="py-3.5 px-4 text-center font-semibold">
                          <span className={
                            prob.difficulty === 'Easy' ? 'text-emerald-400' : prob.difficulty === 'Hard' ? 'text-red-400' : 'text-amber-400'
                          }>
                            {prob.difficulty}
                          </span>
                        </td>

                        <td className="py-3.5 px-4 text-right">
                          <button className="inline-flex items-center space-x-1 text-slate-400 group-hover:text-amber-400 transition-colors">
                            <span>Solve</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

          </div>
        )}

        {/* VIEW 2: Problem Workspace */}
        {currentView === 'problem_workspace' && selectedProblemSlug && (
          <ProblemWorkspace
            problemSlug={selectedProblemSlug}
            contestId={activeContestId}
            contestTitle={activeContestTitle}
            currentUser={currentUser}
            onBack={() => {
              if (activeContestId) setCurrentView('contests');
              else setCurrentView('problems');
              setSelectedProblemSlug(null);
              fetchProblems();
            }}
          />
        )}

        {/* VIEW 3: Contests Hub */}
        {currentView === 'contests' && (
          <ContestHub
            currentUser={currentUser}
            onSelectContestProblem={(slug, cid, title) => {
              setSelectedProblemSlug(slug);
              setActiveContestId(cid);
              setActiveContestTitle(title);
              setCurrentView('problem_workspace');
            }}
          />
        )}

        {/* VIEW 4: Profile Dashboard */}
        {currentView === 'profile' && (
          <ProfileDashboard
            currentUser={currentUser}
            onSelectProblem={(slug) => {
              setSelectedProblemSlug(slug);
              setCurrentView('problem_workspace');
            }}
          />
        )}

        {/* VIEW 5: Integrity Scanner */}
        {currentView === 'quick_scan' && (
          <div className="space-y-6">
            <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-2xl p-8 space-y-4">
              <div className="border-2 border-dashed border-[#3a3a3a] hover:border-amber-500/60 transition-colors rounded-xl p-8 text-center flex flex-col items-center justify-center space-y-3 cursor-pointer relative bg-[#141414]">
                <input 
                  type="file" 
                  multiple 
                  accept=".cpp,.cc,.cxx,.zip"
                  onChange={(e) => { setSelectedFiles(Array.from(e.target.files)); setError(''); }}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
                <div className="p-3 bg-amber-500/10 text-amber-400 rounded-xl">
                  <Upload className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-200">
                    {selectedFiles.length > 0 ? `${selectedFiles.length} files selected` : "Upload C++ files or .zip for Plagiarism & AI Detection"}
                  </p>
                </div>
              </div>

              {error && (
                <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-xs">
                  {error}
                </div>
              )}

              <button
                onClick={handleQuickUpload}
                disabled={analyzing || selectedFiles.length === 0}
                className="w-full bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white font-semibold py-2.5 rounded-xl transition-all flex items-center justify-center space-x-2 text-xs cursor-pointer"
              >
                {analyzing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <span>Run Forensic Scan</span>}
              </button>
            </div>

            {/* Results Table */}
            {result && (
              <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-2xl overflow-hidden p-6 space-y-4">
                <h3 className="text-xs font-bold text-slate-200 uppercase">Analysis Results ({result.total_files_analyzed} Files)</h3>
                <div className="divide-y divide-[#2a2a2a]">
                  {result.comparisons.map((comp, idx) => (
                    <div key={idx} className="py-3 flex items-center justify-between text-xs">
                      <span>{comp.file_a} & {comp.file_b}</span>
                      <div className="flex items-center space-x-3">
                        <span className="font-mono text-amber-400 font-bold">{comp.similarity_score}% Match</span>
                        <button onClick={() => setActiveComparison(comp)} className="text-slate-400 hover:text-white underline cursor-pointer">Diff</button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

      </main>

      {/* Login / Register / Account Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-2xl w-full max-w-md p-6 space-y-5 shadow-2xl">
            
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-[#2a2a2a] pb-3">
              <div className="flex items-center space-x-2">
                <User className="w-5 h-5 text-amber-500" />
                <h3 className="text-base font-bold text-white">
                  {authMode === 'login' ? 'Account Login' : 'Create New Account'}
                </h3>
              </div>
              <button onClick={() => setShowAuthModal(false)} className="text-xs text-slate-400 hover:text-white">
                ✕
              </button>
            </div>

            {/* Current Active Account Card */}
            <div className="bg-[#141414] border border-[#2a2a2a] p-3.5 rounded-xl flex items-center justify-between">
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-bold block">Current Session</span>
                <span className="text-xs font-bold text-slate-200">{currentUser.user_name}</span>
                <span className="text-[10px] font-mono text-slate-400 block">{currentUser.handle}</span>
              </div>
              <button
                onClick={handleLogout}
                className="px-2.5 py-1 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 rounded-lg text-xs font-semibold flex items-center space-x-1 cursor-pointer transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Log Out</span>
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleAuthSubmit} className="space-y-3">
              {authError && (
                <div className="p-2.5 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-xs">
                  {authError}
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Username (Handle)</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. suman or alex"
                  value={authUsername}
                  onChange={(e) => setAuthUsername(e.target.value)}
                  className="w-full bg-[#141414] border border-[#2a2a2a] rounded-lg px-3 py-2 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-amber-500 font-mono"
                />
              </div>

              {authMode === 'register' && (
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Full Display Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Suman Panigrahi"
                    value={authDisplayName}
                    onChange={(e) => setAuthDisplayName(e.target.value)}
                    className="w-full bg-[#141414] border border-[#2a2a2a] rounded-lg px-3 py-2 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-amber-500"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={authPassword}
                  onChange={(e) => setAuthPassword(e.target.value)}
                  className="w-full bg-[#141414] border border-[#2a2a2a] rounded-lg px-3 py-2 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-amber-500"
                />
              </div>

              <button
                type="submit"
                disabled={authLoading}
                className="w-full bg-amber-600 hover:bg-amber-500 text-white font-semibold py-2 rounded-lg text-xs transition-colors cursor-pointer"
              >
                {authLoading ? 'Authenticating...' : authMode === 'login' ? 'Sign In' : 'Create Account'}
              </button>
            </form>

            {/* Toggle Login/Register */}
            <div className="text-center pt-2 border-t border-[#2a2a2a] text-xs text-slate-400">
              {authMode === 'login' ? (
                <p>
                  Don't have an account?{' '}
                  <button onClick={() => { setAuthMode('register'); setAuthError(''); }} className="text-amber-400 hover:underline font-semibold">
                    Sign up
                  </button>
                </p>
              ) : (
                <p>
                  Already have an account?{' '}
                  <button onClick={() => { setAuthMode('login'); setAuthError(''); }} className="text-amber-400 hover:underline font-semibold">
                    Sign in
                  </button>
                </p>
              )}
            </div>

          </div>
        </div>
      )}

      {/* Diff Viewer Modal */}
      {activeComparison && result && (
        <DiffViewer
          comparison={activeComparison}
          filesContent={result.files_content}
          boilerplateSpans={result.file_boilerplate_spans}
          onClose={() => setActiveComparison(null)}
        />
      )}

    </div>
  );
}