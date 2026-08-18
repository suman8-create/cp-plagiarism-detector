// frontend/src/components/ContestHub.jsx

import React, { useState, useEffect } from 'react';
import { 
  Trophy, 
  Timer, 
  Calendar, 
  Users, 
  ArrowRight, 
  CheckCircle2, 
  Lock, 
  Play, 
  Sparkles,
  ArrowLeft
} from 'lucide-react';

export default function ContestHub({ onSelectProblem }) {
  const [contests, setContests] = useState([]);
  const [selectedContest, setSelectedContest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeLeft, setTimeLeft] = useState('');

  const fetchContests = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://127.0.0.1:8000/api/contests');
      if (res.ok) {
        const data = await res.json();
        setContests(data);
        if (data.length > 0 && !selectedContest) {
          fetchContestDetail(data[0].contest_id);
        }
      }
    } catch (err) {
      console.error('Failed to load contests:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchContestDetail = async (cid) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/contests/${cid}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedContest(data);
      }
    } catch (err) {
      console.error('Failed to load contest detail:', err);
    }
  };

  useEffect(() => {
    fetchContests();
  }, []);

  // Timer countdown
  useEffect(() => {
    if (!selectedContest) return;

    const interval = setInterval(() => {
      const end = new Date(selectedContest.end_time).getTime();
      const now = new Date().getTime();
      const diff = end - now;

      if (diff <= 0) {
        setTimeLeft('Contest Ended');
      } else {
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        setTimeLeft(`${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [selectedContest]);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'ACTIVE':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30 animate-pulse';
      case 'UPCOMING':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      default:
        return 'text-slate-400 bg-slate-800 border-slate-700';
    }
  };

  const getDifficultyColor = (diff) => {
    switch (diff?.toLowerCase()) {
      case 'easy':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'hard':
        return 'text-red-400 bg-red-500/10 border-red-500/20';
      default:
        return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
    }
  };

  if (loading) {
    return (
      <div className="p-16 text-center text-xs text-slate-500 bg-slate-900/40 rounded-2xl border border-slate-800">
        Loading competitive contests...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Active Contest Banner */}
      {selectedContest && (
        <div className="bg-gradient-to-r from-indigo-950/60 via-slate-900 to-slate-900 border border-indigo-500/30 rounded-2xl p-6 relative overflow-hidden shadow-xl">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getStatusBadge(selectedContest.status)}`}>
                  ● {selectedContest.status}
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  {selectedContest.duration_minutes} Mins Duration
                </span>
              </div>
              <h2 className="text-xl font-extrabold text-white flex items-center space-x-2">
                <Trophy className="w-5 h-5 text-amber-400" />
                <span>{selectedContest.title}</span>
              </h2>
              <p className="text-xs text-slate-300 max-w-xl">
                {selectedContest.description}
              </p>
            </div>

            {/* Countdown Clock */}
            <div className="bg-slate-950/80 border border-slate-800 px-5 py-3 rounded-xl text-center shrink-0">
              <span className="text-[10px] uppercase font-semibold text-slate-500 block mb-1">Time Remaining</span>
              <div className="text-xl font-mono font-bold text-indigo-400 flex items-center space-x-1 justify-center">
                <Timer className="w-4 h-4 text-slate-400" />
                <span>{timeLeft || '00:00:00'}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: Contest Problem Set */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-200">Contest Problem Set</h3>
          <span className="text-xs text-slate-500 font-mono">
            {selectedContest?.problems?.length || 0} Problems
          </span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden divide-y divide-slate-800">
          {selectedContest?.problems?.map((prob, idx) => (
            <div
              key={prob.problem_id}
              onClick={() => onSelectProblem(prob.slug)}
              className="p-4 flex items-center justify-between hover:bg-slate-800/40 transition-colors cursor-pointer group"
            >
              <div className="flex items-center space-x-3.5">
                <span className="text-xs font-mono text-slate-500 w-6">#{idx + 1}</span>
                <div>
                  <h4 className="font-semibold text-sm text-slate-200 group-hover:text-indigo-400 transition-colors">
                    {prob.title}
                  </h4>
                  <span className="text-[11px] text-slate-500">100 Points</span>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${getDifficultyColor(prob.difficulty)}`}>
                  {prob.difficulty}
                </span>
                <button className="inline-flex items-center space-x-1 px-3 py-1.5 bg-indigo-600/10 hover:bg-indigo-600 text-indigo-400 hover:text-white rounded-lg text-xs font-medium transition-colors">
                  <span>Solve</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}