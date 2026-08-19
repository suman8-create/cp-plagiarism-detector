// frontend/src/components/ProfileDashboard.jsx

import React, { useState, useEffect } from 'react';
import { 
  User, 
  MapPin, 
  CheckCircle2, 
  Calendar, 
  Flame, 
  Clock, 
  Cpu, 
  Eye, 
  Code2,
  FileCode,
  ArrowRight,
  TrendingUp
} from 'lucide-react';
import SubmissionModal from './SubmissionModal';

export default function ProfileDashboard({ currentUser, onSelectProblem }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSubmission, setSelectedSubmission] = useState(null);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const res = await fetch(`http://127.0.0.1:8000/api/users/${currentUser.user_id}/profile?user_name=${encodeURIComponent(currentUser.user_name)}&handle=${encodeURIComponent(currentUser.handle)}`);
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

  if (loading) {
    return (
      <div className="p-16 text-center text-xs text-slate-500 bg-[#1e1e1e] rounded-2xl border border-[#2a2a2a]">
        Loading profile stats...
      </div>
    );
  }

  if (!profile) return null;

  // Generate 52 weeks (364 days) of activity for the heatmap
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const today = new Date();
  const dayCells = [];
  for (let i = 363; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const dateKey = d.toISOString().split('T')[0];
    const count = profile.heatmap_activity[dateKey] || 0;
    dayCells.push({ date: dateKey, count });
  }

  return (
    <div className="space-y-6">
      {/* Top Grid: User Info Card + Circular Solve Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        
        {/* Left: User Profile Summary */}
        <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-2xl p-6 space-y-5">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 to-indigo-400 text-white font-extrabold text-2xl flex items-center justify-center shadow-lg shadow-indigo-600/30">
              {currentUser.user_name.charAt(0)}
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-100">{currentUser.user_name}</h2>
              <p className="text-xs text-slate-400 font-mono">{currentUser.handle}</p>
              <span className="inline-block mt-1 text-[11px] font-mono text-slate-500 bg-[#141414] px-2 py-0.5 rounded border border-[#2a2a2a]">
                Rank ~{profile.rank.toLocaleString()}
              </span>
            </div>
          </div>

          <div className="pt-4 border-t border-[#2a2a2a] space-y-2 text-xs text-slate-400">
            <div className="flex items-center space-x-2">
              <MapPin className="w-3.5 h-3.5 text-slate-500" />
              <span>India</span>
            </div>
            <div className="flex items-center justify-between pt-1">
              <span>Acceptance Rate</span>
              <span className="font-mono font-bold text-emerald-400">{profile.acceptance_rate}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Total Submissions</span>
              <span className="font-mono font-semibold text-slate-200">{profile.total_submissions}</span>
            </div>
          </div>
        </div>

        {/* Right: LeetCode Donut / Solve Breakdown */}
        <div className="lg:col-span-2 bg-[#1e1e1e] border border-[#2a2a2a] rounded-2xl p-6 flex flex-col md:flex-row items-center justify-around gap-6">
          {/* Big Circular Counter */}
          <div className="text-center relative flex flex-col items-center justify-center w-36 h-36 rounded-full border-4 border-emerald-500/30 bg-[#141414]">
            <span className="text-2xl font-extrabold text-white font-mono">{profile.total_solved}</span>
            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Solved</span>
            <span className="text-[9px] text-slate-600 font-mono">/ {profile.total_problems} Total</span>
          </div>

          {/* Difficulty Counters */}
          <div className="space-y-3 w-full max-w-xs text-xs font-mono">
            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-emerald-400 font-semibold">Easy</span>
                <span className="text-slate-300">{profile.easy_solved} / {profile.easy_total}</span>
              </div>
              <div className="w-full bg-[#141414] h-2 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full rounded-full transition-all" style={{ width: `${(profile.easy_solved / profile.easy_total) * 100}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-amber-400 font-semibold">Medium</span>
                <span className="text-slate-300">{profile.medium_solved} / {profile.medium_total}</span>
              </div>
              <div className="w-full bg-[#141414] h-2 rounded-full overflow-hidden">
                <div className="bg-amber-500 h-full rounded-full transition-all" style={{ width: `${(profile.medium_solved / profile.medium_total) * 100}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-[11px] mb-1">
                <span className="text-red-400 font-semibold">Hard</span>
                <span className="text-slate-300">{profile.hard_solved} / {profile.hard_total}</span>
              </div>
              <div className="w-full bg-[#141414] h-2 rounded-full overflow-hidden">
                <div className="bg-red-500 h-full rounded-full transition-all" style={{ width: `${(profile.hard_solved / profile.hard_total) * 100}%` }} />
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Contribution Heatmap Grid (365 Days) */}
      <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Flame className="w-4 h-4 text-amber-500" />
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
              {profile.total_submissions} Submissions in the past year
            </h3>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">365-Day Activity Grid</span>
        </div>

        <div className="overflow-x-auto pb-2">
          <div className="grid grid-flow-col grid-rows-7 gap-1.5 min-w-[700px]">
            {dayCells.map((day, idx) => {
              let bg = 'bg-[#141414] border-[#222]';
              if (day.count >= 3) bg = 'bg-emerald-500 border-emerald-400';
              else if (day.count === 2) bg = 'bg-emerald-600/80 border-emerald-500';
              else if (day.count === 1) bg = 'bg-emerald-800/60 border-emerald-700';

              return (
                <div
                  key={idx}
                  title={`${day.date}: ${day.count} submissions`}
                  className={`w-3 h-3 rounded-sm border ${bg} transition-colors`}
                />
              );
            })}
          </div>
        </div>
      </div>

      {/* Practice Submissions History Table */}
      <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-2xl overflow-hidden shadow-xl space-y-0">
        <div className="p-4 border-b border-[#2a2a2a] bg-[#171717] flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Practice & Contest History</h3>
          <span className="text-[11px] font-mono text-slate-500">{profile.recent_submissions.length} Recorded Submissions</span>
        </div>

        {profile.recent_submissions.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500">
            No submissions recorded yet. Open a problem from the catalog to submit your solution!
          </div>
        ) : (
          <div className="divide-y divide-[#2a2a2a]">
            {profile.recent_submissions.map((sub) => (
              <div
                key={sub.submission_id}
                onClick={() => setSelectedSubmission(sub)}
                className="p-4 flex items-center justify-between hover:bg-[#252525] transition-colors cursor-pointer group"
              >
                <div className="flex items-center space-x-3.5">
                  <span className={`px-2.5 py-0.5 rounded text-[11px] font-semibold border ${
                    sub.status === 'Accepted'
                      ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                      : 'bg-red-500/10 border-red-500/30 text-red-400'
                  }`}>
                    {sub.status}
                  </span>
                  <div>
                    <h4 className="text-xs font-bold text-slate-200 group-hover:text-indigo-400 transition-colors">
                      {sub.problem_title || sub.problem_id}
                    </h4>
                    <span className="text-[10px] text-slate-500">
                      Time to solve: {Math.round(sub.time_taken_seconds)}s • Runtime: {sub.execution_time_ms} ms
                    </span>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <span className="text-[11px] font-mono text-slate-500">
                    {new Date(sub.submitted_at).toLocaleDateString()}
                  </span>
                  <button className="p-1.5 text-slate-500 hover:text-white rounded hover:bg-[#333] transition-colors">
                    <Eye className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Detailed LeetCode Submission Modal */}
      {selectedSubmission && (
        <SubmissionModal
          submission={selectedSubmission}
          onClose={() => setSelectedSubmission(null)}
        />
      )}
    </div>
  );
}