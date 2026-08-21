// frontend/src/App.jsx

import React, { useState, useEffect } from 'react';
import { 
  Flame, 
  Trophy, 
  Code2, 
  User, 
  ShieldCheck, 
  Search, 
  Upload, 
  Layers, 
  AlertCircle,
  FileCode,
  ArrowRight,
  ShieldAlert
} from 'lucide-react';

import DiffViewer from './components/DiffViewer';
import ProblemWorkspace from './components/ProblemWorkspace';
import ContestHub from './components/ContestHub';
import ProfileDashboard from './components/ProfileDashboard';
import AuthModal from './components/AuthModal';
import AdminDashboard from './components/AdminDashboard';
import AdminLoginModal from './components/AdminLoginModal';

export default function App() {
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem('cp_active_user');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    return null;
  });

  const [showAuthModal, setShowAuthModal] = useState(false);
  const [currentView, setCurrentView] = useState('problems'); // 'problems' | 'contests' | 'profile' | 'integrity' | 'problem_workspace' | 'admin'
  
  const [problems, setProblems] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState('All Topics');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProblemSlug, setSelectedProblemSlug] = useState(null);
  const [activeContestId, setActiveContestId] = useState(null);
  const [activeContestTitle, setActiveContestTitle] = useState(null);
  const [loadingProblems, setLoadingProblems] = useState(false);

  // Scanner & DiffViewer State
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [activeComparison, setActiveComparison] = useState(null);

  // Admin Portal State
  const [adminUser, setAdminUser] = useState(null);
  const [showAdminLoginModal, setShowAdminLoginModal] = useState(false);

  useEffect(() => {
    if (currentUser) {
      localStorage.setItem('cp_active_user', JSON.stringify(currentUser));
    } else {
      localStorage.removeItem('cp_active_user');
    }
  }, [currentUser]);

  const fetchProblems = async () => {
    try {
      setLoadingProblems(true);
      const uidParam = currentUser ? `?user_id=${currentUser.user_id}` : '';
      const res = await fetch(`http://127.0.0.1:8000/api/problems${uidParam}`);
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

  const handleLogout = () => {
    localStorage.removeItem('cp_active_user');
    setCurrentUser(null);
    setShowAuthModal(false);
    if (currentView === 'profile') {
      setCurrentView('problems');
    }
  };

  const handleProblemClick = (slug) => {
    if (!currentUser) {
      setShowAuthModal(true);
      return;
    }
    setSelectedProblemSlug(slug);
    setActiveContestId(null);
    setCurrentView('problem_workspace');
  };

  // 1-Click Launch DiffViewer Handler from Admin Dashboard
  const handleLaunchDiffViewerFromAdmin = (codeA, codeB, nameA, nameB) => {
    setActiveComparison({
      file1: nameA ? `${nameA}.cpp` : 'Competitor_A.cpp',
      file2: nameB ? `${nameB}.cpp` : 'Competitor_B.cpp',
      code1: codeA,
      code2: codeB,
      similarity_score: 95.0,
      confidence_score: 0.92,
      ast_similarity: 95.0,
      llm_forensic_score: 88.0,
      classification: 'Suspicious Collusion',
      flags: ['Matched via Contest Batch Audit Matrix']
    });
    setCurrentView('integrity');
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

  const topicsList = ['All Topics', 'Array', 'String', 'Hash Table', 'Math', 'Dynamic Programming', 'Simulation', 'Two Pointers'];

  const filteredProblems = problems.filter((p) => {
    const matchesSearch = p.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTopic = selectedTopic === 'All Topics' || (p.topic_tags && p.topic_tags.includes(selectedTopic));
    return matchesSearch && matchesTopic;
  });

  return (
    <div className="min-h-screen bg-[#121212] text-slate-100 font-sans flex flex-col justify-between">
      
      {/* Global Navigation Header */}
      <div>
        <header className="border-b border-[#27272a] bg-[#18181b]/80 backdrop-blur sticky top-0 z-40 px-6 py-3">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            
            {/* Brand Logo & Main Nav Tabs */}
            <div className="flex items-center space-x-8">
              <div 
                onClick={() => setCurrentView('problems')} 
                className="flex items-center space-x-2 cursor-pointer select-none"
              >
                <div className="p-1.5 bg-gradient-to-tr from-amber-500 to-orange-500 rounded-lg shadow-sm">
                  <Flame className="w-5 h-5 text-white" />
                </div>
                <span className="font-extrabold text-base tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                  CodeArena
                </span>
              </div>

              <nav className="flex items-center space-x-2 text-xs font-semibold">
                <button
                  onClick={() => setCurrentView('problems')}
                  className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                    currentView === 'problems' || currentView === 'problem_workspace'
                      ? 'bg-[#27272a] text-emerald-400'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-[#27272a]/50'
                  }`}
                >
                  Problems
                </button>

                <button
                  onClick={() => setCurrentView('contests')}
                  className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                    currentView === 'contests'
                      ? 'bg-[#27272a] text-emerald-400'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-[#27272a]/50'
                  }`}
                >
                  Contests
                </button>

                <button
                  onClick={() => {
                    if (!currentUser) {
                      setShowAuthModal(true);
                      return;
                    }
                    setCurrentView('profile');
                  }}
                  className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                    currentView === 'profile'
                      ? 'bg-[#27272a] text-emerald-400'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-[#27272a]/50'
                  }`}
                >
                  Profile
                </button>

                <button
                  onClick={() => setCurrentView('integrity')}
                  className={`px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
                    currentView === 'integrity'
                      ? 'bg-[#27272a] text-emerald-400'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-[#27272a]/50'
                  }`}
                >
                  Integrity Scanner
                </button>
              </nav>
            </div>

            {/* Right Header Controls (Auth & Admin Radar) */}
            <div className="flex items-center space-x-3">
              
              {/* Admin Radar Launch Button */}
              <button
                onClick={() => {
                  if (adminUser) {
                    setCurrentView('admin');
                  } else {
                    setShowAdminLoginModal(true);
                  }
                }}
                className={`px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center space-x-1.5 transition-all cursor-pointer ${
                  currentView === 'admin'
                    ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/30'
                    : 'bg-[#18181b] text-indigo-400 border-indigo-500/30 hover:bg-indigo-500/10'
                }`}
              >
                <ShieldAlert className="w-3.5 h-3.5" />
                <span>Admin Radar</span>
              </button>

              {/* User Account / Guest Trigger */}
              {currentUser ? (
                <div className="flex items-center space-x-2 bg-[#18181b] border border-[#27272a] px-3 py-1.5 rounded-xl">
                  <div className="w-6 h-6 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-xs font-bold text-emerald-400">
                    {currentUser.display_name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <div className="text-left">
                    <p className="text-[11px] font-bold text-slate-200 leading-tight">{currentUser.display_name}</p>
                    <p className="text-[9px] text-slate-500 font-mono">@{currentUser.username}</p>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="ml-2 text-[10px] text-slate-500 hover:text-red-400 transition-colors cursor-pointer"
                  >
                    Logout
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold transition-colors shadow-sm cursor-pointer"
                >
                  Sign In
                </button>
              )}
            </div>

          </div>
        </header>

        {/* Dynamic Main Views */}
        <main className="max-w-7xl mx-auto px-4 py-6">
          
          {/* 1. ADMIN DASHBOARD VIEW */}
          {currentView === 'admin' && adminUser && (
            <AdminDashboard
              adminUser={adminUser}
              onLogout={() => {
                setAdminUser(null);
                setCurrentView('problems');
              }}
              onLaunchDiffViewer={handleLaunchDiffViewerFromAdmin}
            />
          )}

          {/* 2. PROBLEMS CATALOG VIEW */}
          {currentView === 'problems' && (
            <div className="space-y-6">
              
              {/* Problem Filter & Search Bar */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex flex-wrap gap-1.5">
                  {topicsList.map((tag) => (
                    <button
                      key={tag}
                      onClick={() => setSelectedTopic(tag)}
                      className={`px-3 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                        selectedTopic === tag
                          ? 'bg-emerald-600 text-white shadow-sm'
                          : 'bg-[#1e1e1e] text-slate-400 hover:text-slate-200 border border-[#2a2a2a]'
                      }`}
                    >
                      {tag}
                    </button>
                  ))}
                </div>

                <div className="relative w-full md:w-64">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-slate-500" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search problems..."
                    className="w-full bg-[#1e1e1e] border border-[#2a2a2a] rounded-xl pl-8 pr-3 py-2 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              {/* Problems Table */}
              <div className="bg-[#18181b] border border-[#27272a] rounded-2xl overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#121214] border-b border-[#27272a] text-slate-400 uppercase tracking-wider font-semibold text-[10px]">
                    <tr>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4">Title</th>
                      <th className="py-3 px-4">Difficulty</th>
                      <th className="py-3 px-4">Topics</th>
                      <th className="py-3 px-4 text-right">Submissions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#27272a]">
                    {filteredProblems.map((p) => (
                      <tr
                        key={p.problem_id}
                        onClick={() => handleProblemClick(p.slug)}
                        className="hover:bg-[#222226] cursor-pointer transition-colors"
                      >
                        <td className="py-3 px-4">
                          {p.solved ? (
                            <span className="text-emerald-400 font-bold">Solved</span>
                          ) : (
                            <span className="text-slate-600">—</span>
                          )}
                        </td>
                        <td className="py-3 px-4 font-semibold text-slate-100 hover:text-emerald-400">
                          {p.title}
                        </td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                            p.difficulty === 'Easy'
                              ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
                              : p.difficulty === 'Medium'
                              ? 'text-amber-400 bg-amber-500/10 border-amber-500/30'
                              : 'text-red-400 bg-red-500/10 border-red-500/30'
                          }`}>
                            {p.difficulty}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex flex-wrap gap-1">
                            {p.topic_tags?.map((t, idx) => (
                              <span key={idx} className="px-1.5 py-0.5 rounded bg-[#121214] text-[10px] text-slate-400 border border-[#27272a]">
                                {t}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="py-3 px-4 text-right font-mono text-slate-400">
                          {p.submission_count || 0}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

            </div>
          )}

          {/* 3. PROBLEM WORKSPACE VIEW */}
          {currentView === 'problem_workspace' && (
            <ProblemWorkspace
              problemSlug={selectedProblemSlug}
              contestId={activeContestId}
              contestTitle={activeContestTitle}
              currentUser={currentUser}
              onBack={() => setCurrentView(activeContestId ? 'contests' : 'problems')}
            />
          )}

          {/* 4. CONTEST HUB VIEW */}
          {currentView === 'contests' && (
            <ContestHub
              currentUser={currentUser}
              onSelectProblem={(slug, contestId, contestTitle) => {
                setSelectedProblemSlug(slug);
                setActiveContestId(contestId);
                setActiveContestTitle(contestTitle);
                setCurrentView('problem_workspace');
              }}
            />
          )}

          {/* 5. PROFILE DASHBOARD VIEW */}
          {currentView === 'profile' && currentUser && (
            <ProfileDashboard
              currentUser={currentUser}
              onSelectProblem={(slug) => handleProblemClick(slug)}
            />
          )}

          {/* 6. INTEGRITY SCANNER & DIFFVIEWER VIEW */}
          {currentView === 'integrity' && (
            <div className="space-y-6">
              {activeComparison ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <button
                      onClick={() => setActiveComparison(null)}
                      className="text-xs text-slate-400 hover:text-white flex items-center space-x-1.5 cursor-pointer"
                    >
                      <span>← Back to Scanner Overview</span>
                    </button>
                  </div>
                  <DiffViewer
                    initialCodeA={activeComparison.code1}
                    initialCodeB={activeComparison.code2}
                    labelA={activeComparison.file1}
                    labelB={activeComparison.file2}
                  />
                </div>
              ) : (
                /* Standalone Multi-File Quick Upload Box */
                <div className="bg-[#18181b] border border-[#27272a] rounded-2xl p-8 max-w-xl mx-auto text-center space-y-4">
                  <div className="p-3 bg-indigo-500/10 border border-indigo-500/30 rounded-2xl text-indigo-400 w-12 h-12 mx-auto flex items-center justify-center">
                    <Upload className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-100">Upload C++ Files for Instant AST Audit</h3>
                    <p className="text-xs text-slate-400 mt-1">Upload multiple C++ source files or a .zip archive</p>
                  </div>

                  <input
                    type="file"
                    multiple
                    accept=".cpp,.hpp,.cc,.h,.zip"
                    onChange={(e) => setSelectedFiles(Array.from(e.target.files))}
                    className="block w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 file:cursor-pointer"
                  />

                  {error && (
                    <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-xs flex items-center space-x-2">
                      <AlertCircle className="w-4 h-4 shrink-0" />
                      <span>{error}</span>
                    </div>
                  )}

                  <button
                    onClick={handleQuickUpload}
                    disabled={analyzing || selectedFiles.length === 0}
                    className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-all shadow-sm cursor-pointer disabled:opacity-50"
                  >
                    {analyzing ? 'Tokenizing ASTs & Running Scans...' : 'Scan Submissions'}
                  </button>
                </div>
              )}
            </div>
          )}

        </main>
      </div>

      {/* Modals */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onLoginSuccess={(user) => {
          setCurrentUser(user);
          setShowAuthModal(false);
        }}
      />

      <AdminLoginModal
        isOpen={showAdminLoginModal}
        onClose={() => setShowAdminLoginModal(false)}
        onLoginSuccess={(adminData) => {
          setAdminUser(adminData);
          setCurrentView('admin');
        }}
      />
    </div>
  );
}