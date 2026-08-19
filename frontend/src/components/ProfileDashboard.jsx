// frontend/src/components/ProfileDashboard.jsx

import React, { useState, useEffect } from 'react';
import { 
  MapPin, 
  Eye, 
  LogIn,
  RefreshCw,
  Code2,
  Tag,
  CheckCircle2
} from 'lucide-react';
import SubmissionModal from './SubmissionModal';

export default function ProfileDashboard({ currentUser, onRequestAuth, onSelectProblem }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSubmission, setSelectedSubmission] = useState(null);

  const fetchProfile = async () => {
    if (!currentUser || !currentUser.user_id) {
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      const uName = encodeURIComponent(currentUser.user_name || 'User');
      const uHandle = encodeURIComponent(currentUser.handle || '@user');
      const res = await fetch(`http://127.0.0.1:8000/api/users/${currentUser.user_id}/profile?user_name=${uName}&handle=${uHandle}`);
      
      if (res.ok) {
        const data = await res.json();
        setProfile(data);
      }
    } catch (err) {
      console.error('Failed to load profile:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, [currentUser]);

  if (!currentUser) {
    return (
      <div className="p-16 text-center bg-[#1e1e1e] rounded-2xl border border-[#2a2a2a] space-y-4 max-w-md mx-auto my-12 shadow-2xl">
        <div className="w-14 h-14 rounded-2xl bg-indigo-600/10 text-indigo-400 flex items-center justify-center mx-auto border border-indigo-500/20">
          <LogIn className="w-7 h-7" />
        </div>
        <div className="space-y-1">
          <h3 className="text-base font-bold text-white">Sign In Required</h3>
          <p className="text-xs text-slate-400">
            Please log in to your account to view your submissions history, skill stats, and performance metrics.
          </p>
        </div>
        <button
          onClick={onRequestAuth}
          className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors cursor-pointer shadow-lg shadow-indigo-600/20"
        >
          Sign In / Create Account
        </button>
      </div>
    );
  }

  if (loading && !profile) {
    return (
      <div className="p-16 text-center text-xs text-slate-400 bg-[#1e1e1e] rounded-2xl border border-[#2a2a2a] flex flex-col items-center justify-center space-y-3">
        <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
        <span>Loading profile metrics...</span>
      </div>
    );
  }

  const userStats = profile || {
    user_id: currentUser.user_id,
    user_name: currentUser.user_name,
    handle: currentUser.handle,
    total_solved: 0,
    total_problems: 15,
    easy_solved: 0,
    easy_total: 10,
    medium_solved: 0,
    medium_total: 4,
    hard_solved: 0,
    hard_total: 1,
    accuracy_percentage: 0.0,
    total_submissions: 0,
    skills_breakdown: {},
    recent_submissions: [],
  };

  const totalSolved = userStats.total_solved || 0;
  const totalProblems = userStats.total_problems || 15;
  const easySolved = userStats.easy_solved || 0;
  const easyTotal = userStats.easy_total || 10;
  const mediumSolved = userStats.medium_solved || 0;
  const mediumTotal = userStats.medium_total || 4;
  const hardSolved = userStats.hard_solved || 0;
  const hardTotal = userStats.hard_total || 1;
  const accuracy = userStats.accuracy_percentage || 0.0;
  const totalSubmissions = userStats.total_submissions || 0;
  const recentSubs = userStats.recent_submissions || [];
  const skills = userStats.skills_breakdown || {};

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 max-w-6xl mx-auto">
      
      {/* LEFT COLUMN: User Profile, Languages & Dynamic Skills */}
      <div className="lg:col-span-4 space-y-4">
        
        {/* Profile Card */}
        <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-2xl p-5 space-y-4 shadow-lg">
          <div className="flex items-center space-x-3.5">
            <div className="w-14 h-14 rounded-2xl bg-indigo-600 text-white font-extrabold text-2xl flex items-center justify-center shadow-lg shadow-indigo-600/30">
              {currentUser.user_name ? currentUser.user_name.charAt(0) : 'U'}
            </div>
            <div>
              <h2 className="text-base font-bold text-white leading-tight">{currentUser.user_name}</h2>
              <p className="text-xs text-slate-400 font-mono">{currentUser.handle}</p>
            </div>
          </div>

          <div className="pt-3 border-t border-[#2a2a2a] space-y-2 text-xs text-slate-400">
            <div className="flex items-center space-x-2">
              <MapPin className="w-3.5 h-3.5 text-slate-500" />
              <span>India</span>
            </div>
          </div>
        </div>

        {/* Languages */}
        <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-2xl p-5 space-y-3 shadow-lg">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
            <Code2 className="w-3.5 h-3.5 text-indigo-400" />
            <span>Languages</span>
          </h3>
          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="px-2 py-0.5 rounded-full bg-[#141414] border border-[#2a2a2a] text-slate-300 font-mono text-[11px]">C++</span>
              <span className="text-slate-300 font-mono font-semibold">{totalSolved} problems solved</span>
            </div>
            <div className="flex items-center justify-between text-slate-600">
              <span className="px-2 py-0.5 rounded-full bg-[#141414] border border-[#2a2a2a] font-mono text-[11px]">Java</span>
              <span className="font-mono">0 problems solved</span>
            </div>
            <div className="flex items-center justify-between text-slate-600">
              <span className="px-2 py-0.5 rounded-full bg-[#141414] border border-[#2a2a2a] font-mono text-[11px]">Python</span>
              <span className="font-mono">0 problems solved</span>
            </div>
          </div>
        </div>

        {/* Dynamic Skills (Based on Solved Question Tags) */}
        <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-2xl p-5 space-y-3 shadow-lg">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
            <Tag className="w-3.5 h-3.5 text-indigo-400" />
            <span>Skills Acquired</span>
          </h3>

          {Object.keys(skills).length === 0 ? (
            <p className="text-[11px] text-slate-500 italic">
              Solve problems to build and display your skills proficiency breakdown.
            </p>
          ) : (
            <div className="flex flex-wrap gap-1.5 text-[11px]">
              {Object.entries(skills).map(([tagName, count]) => (
                <span
                  key={tagName}
                  className="px-2.5 py-1 rounded-full bg-[#141414] border border-[#2a2a2a] text-slate-300 font-mono"
                >
                  {tagName} <strong className="text-indigo-400 font-bold">x{count}</strong>
                </span>
              ))}
            </div>
          )}
        </div>

      </div>

      {/* RIGHT COLUMN: Gauge, Accuracy, Total Attempts & Submissions List */}
      <div className="lg:col-span-8 space-y-4">
        
        {/* Gauge + Accuracy + Attempts Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          
          {/* Circular Solve Gauge Card */}
          <div className="md:col-span-2 bg-[#1e1e1e] border border-[#2a2a2a] rounded-2xl p-5 flex items-center justify-around shadow-lg">
            <div className="text-center relative flex flex-col items-center justify-center w-32 h-32 rounded-full border-4 border-indigo-500/40 bg-[#141414]">
              <span className="text-2xl font-extrabold text-white font-mono">{totalSolved}</span>
              <span className="text-[10px] uppercase font-bold text-slate-400">Solved</span>
              <span className="text-[9px] text-slate-500 font-mono">/ {totalProblems}</span>
            </div>

            <div className="space-y-2.5 w-44 text-xs font-mono">
              <div>
                <div className="flex justify-between text-[11px] mb-1">
                  <span className="text-emerald-400 font-semibold">Easy</span>
                  <span className="text-slate-300">{easySolved} / {easyTotal}</span>
                </div>
                <div className="w-full bg-[#141414] h-1.5 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full rounded-full transition-all" style={{ width: `${(easySolved / Math.max(1, easyTotal)) * 100}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[11px] mb-1">
                  <span className="text-amber-400 font-semibold">Med.</span>
                  <span className="text-slate-300">{mediumSolved} / {mediumTotal}</span>
                </div>
                <div className="w-full bg-[#141414] h-1.5 rounded-full overflow-hidden">
                  <div className="bg-amber-500 h-full rounded-full transition-all" style={{ width: `${(mediumSolved / Math.max(1, mediumTotal)) * 100}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-[11px] mb-1">
                  <span className="text-red-400 font-semibold">Hard</span>
                  <span className="text-slate-300">{hardSolved} / {hardTotal}</span>
                </div>
                <div className="w-full bg-[#141414] h-1.5 rounded-full overflow-hidden">
                  <div className="bg-red-500 h-full rounded-full transition-all" style={{ width: `${(hardSolved / Math.max(1, hardTotal)) * 100}%` }} />
                </div>
              </div>
            </div>
          </div>

          {/* Accuracy & Total Attempts */}
          <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-2xl p-5 flex flex-col justify-between shadow-lg">
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">Accuracy</span>
              <span className="text-2xl font-extrabold text-emerald-400 font-mono">{accuracy}%</span>
            </div>
            <div className="pt-3 border-t border-[#2a2a2a]">
              <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">Total Submissions</span>
              <span className="text-base font-bold text-slate-200 font-mono">{totalSubmissions}</span>
            </div>
          </div>

        </div>

        {/* All Submissions History */}
        <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-2xl overflow-hidden shadow-xl">
          <div className="p-4 border-b border-[#2a2a2a] bg-[#171717] flex items-center justify-between text-xs">
            <h3 className="font-bold text-slate-200 uppercase tracking-wider">All Submissions</h3>
            <span className="text-slate-500 font-mono">{recentSubs.length} Recorded</span>
          </div>

          {recentSubs.length === 0 ? (
            <div className="p-12 text-center text-xs text-slate-500">
              No submissions recorded yet for {currentUser.user_name}. Open any problem to submit your code!
            </div>
          ) : (
            <div className="divide-y divide-[#2a2a2a]">
              {recentSubs.map((sub) => (
                <div
                  key={sub.submission_id}
                  onClick={() => setSelectedSubmission(sub)}
                  className="p-3.5 flex items-center justify-between hover:bg-[#252525] transition-colors cursor-pointer group"
                >
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                      sub.status === 'Accepted'
                        ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                        : 'bg-red-500/10 border-red-500/30 text-red-400'
                    }`}>
                      {sub.status}
                    </span>
                    <div>
                      <h4 className="text-xs font-semibold text-slate-200 group-hover:text-indigo-400 transition-colors">
                        {sub.problem_title || sub.problem_id}
                      </h4>
                      <span className="text-[10px] text-slate-500">
                        {Math.round(sub.time_taken_seconds || 0)}s to solve • {sub.execution_time_ms} ms
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 text-xs">
                    <span className="text-[11px] font-mono text-slate-500">
                      {new Date(sub.submitted_at).toLocaleDateString()}
                    </span>
                    <button className="p-1 text-slate-500 hover:text-white transition-colors">
                      <Eye className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

      {selectedSubmission && (
        <SubmissionModal
          submission={selectedSubmission}
          onClose={() => setSelectedSubmission(null)}
        />
      )}
    </div>
  );
}