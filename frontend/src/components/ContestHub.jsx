// frontend/src/components/ContestHub.jsx

import React, { useState, useEffect } from 'react';
import { 
  Trophy, 
  Timer, 
  ArrowRight, 
  CheckCircle2, 
  Circle, 
  Lock, 
  Clock, 
  ArrowLeft,
  Medal,
  RefreshCw,
  LogIn
} from 'lucide-react';

export default function ContestHub({ currentUser, onRequestAuth, onSelectContestProblem }) {
  const [contests, setContests] = useState([]);
  const [activeContestId, setActiveContestId] = useState(null);
  const [contestDetail, setContestDetail] = useState(null);
  const [activeTab, setActiveTab] = useState('problems'); // 'problems' | 'leaderboard'
  const [leaderboard, setLeaderboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingLeaderboard, setLoadingLeaderboard] = useState(false);
  const [timeLeft, setTimeLeft] = useState('');

  const activeUserId = currentUser?.user_id || 'guest_user';
  const activeUserName = currentUser?.user_name || 'Guest';

  const fetchContests = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://127.0.0.1:8000/api/contests');
      if (res.ok) {
        const data = await res.json();
        setContests(data);
      }
    } catch (err) {
      console.error('Failed to load contests:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchContestDetail = async (cid) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/contests/${cid}?user_id=${activeUserId}`);
      if (res.ok) {
        const data = await res.json();
        setContestDetail(data);
        setActiveContestId(cid);
      }
    } catch (err) {
      console.error('Failed to load contest detail:', err);
    }
  };

  const fetchLeaderboard = async (cid) => {
    try {
      setLoadingLeaderboard(true);
      const res = await fetch(`http://127.0.0.1:8000/api/contests/${cid}/leaderboard`);
      if (res.ok) {
        const data = await res.json();
        setLeaderboard(data);
      }
    } catch (err) {
      console.error('Failed to load leaderboard:', err);
    } finally {
      setLoadingLeaderboard(false);
    }
  };

  useEffect(() => {
    fetchContests();
  }, []);

  useEffect(() => {
    if (activeContestId) {
      fetchContestDetail(activeContestId);
      if (activeTab === 'leaderboard') {
        fetchLeaderboard(activeContestId);
      }
    }
  }, [activeUserId, activeContestId, activeTab]);

  // Timer countdown
  useEffect(() => {
    if (!contestDetail) return;

    const parseTargetTime = () => {
      let targetStr = contestDetail.status === 'Upcoming' ? contestDetail.start_time : contestDetail.end_time;
      if (!targetStr.endsWith('Z') && !targetStr.includes('+')) {
        targetStr += 'Z';
      }
      return new Date(targetStr).getTime();
    };

    const updateTimer = () => {
      const target = parseTargetTime();
      const now = new Date().getTime();
      const diff = target - now;

      if (diff <= 0) {
        if (contestDetail.status === 'Upcoming') {
          setTimeLeft('Starting Now...');
          fetchContestDetail(contestDetail.contest_id);
        } else {
          setTimeLeft('Contest Finished');
        }
      } else {
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        setTimeLeft(`${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
      }
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    return () => clearInterval(interval);
  }, [contestDetail]);

  const handleRegister = async () => {
    if (!currentUser) {
      if (onRequestAuth) onRequestAuth();
      return;
    }
    if (!contestDetail) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/contests/${contestDetail.contest_id}/register?user_id=${activeUserId}&user_name=${encodeURIComponent(activeUserName)}`, {
        method: 'POST'
      });
      if (res.ok) {
        fetchContestDetail(contestDetail.contest_id);
      }
    } catch (err) {
      console.error('Failed to register:', err);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Live':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30 animate-pulse';
      case 'Upcoming':
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

  const getRankBadge = (rank) => {
    if (rank === 1) return <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px] font-bold">🥇 1st</span>;
    if (rank === 2) return <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full bg-slate-300/10 border border-slate-300/30 text-slate-200 text-[11px] font-bold">🥈 2nd</span>;
    if (rank === 3) return <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full bg-amber-700/10 border border-amber-700/30 text-amber-500 text-[11px] font-bold">🥉 3rd</span>;
    return <span className="font-mono text-xs font-semibold text-slate-400">#{rank}</span>;
  };

  if (loading) {
    return (
      <div className="p-16 text-center text-xs text-slate-500 bg-[#1e1e1e] rounded-2xl border border-[#2a2a2a]">
        Loading competitive contests...
      </div>
    );
  }

  // --- View 1: Contest Arena ---
  if (activeContestId && contestDetail) {
    const isLive = contestDetail.status === 'Live';
    const isUpcoming = contestDetail.status === 'Upcoming';
    const isFinished = contestDetail.status === 'Finished';

    return (
      <div className="space-y-6">
        {/* Top Back Nav */}
        <button
          onClick={() => { setActiveContestId(null); setContestDetail(null); fetchContests(); }}
          className="inline-flex items-center space-x-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Contests List</span>
        </button>

        {/* Hero Contest Banner */}
        <div className="bg-gradient-to-r from-indigo-950/70 via-slate-900 to-slate-900 border border-indigo-500/30 rounded-2xl p-6 relative overflow-hidden shadow-xl space-y-6">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="space-y-2 max-w-2xl">
              <div className="flex items-center space-x-2.5">
                <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getStatusBadge(contestDetail.status)}`}>
                  ● {contestDetail.status}
                </span>
                <span className="text-xs text-slate-400 font-mono flex items-center space-x-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{contestDetail.duration_minutes} Mins Duration</span>
                </span>
              </div>
              <h2 className="text-2xl font-extrabold text-white flex items-center space-x-2.5">
                <Trophy className="w-6 h-6 text-amber-400 shrink-0" />
                <span>{contestDetail.title}</span>
              </h2>
              <p className="text-xs text-slate-300 leading-relaxed">
                {contestDetail.description}
              </p>
            </div>

            {/* Live Clock Panel */}
            <div className="bg-slate-950/80 border border-slate-800 px-6 py-4 rounded-xl text-center shrink-0 min-w-[200px]">
              <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                {isUpcoming ? 'Starts In' : isLive ? 'Time Remaining' : 'Contest Status'}
              </span>
              <div className="text-2xl font-mono font-extrabold text-indigo-400 flex items-center space-x-2 justify-center">
                <Timer className="w-5 h-5 text-indigo-400" />
                <span>{timeLeft || '00:00:00'}</span>
              </div>
            </div>
          </div>

          {/* Participant Metrics Dashboard */}
          <div className="pt-5 border-t border-slate-800/80 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl">
              <span className="text-[10px] text-slate-500 uppercase font-semibold block">Your Score</span>
              <span className="text-base font-bold text-amber-400 font-mono mt-0.5 block">
                {contestDetail.user_score} <span className="text-xs text-slate-500 font-normal">pts</span>
              </span>
            </div>

            <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl">
              <span className="text-[10px] text-slate-500 uppercase font-semibold block">Solved</span>
              <span className="text-base font-bold text-emerald-400 font-mono mt-0.5 block">
                {contestDetail.user_solved_count} / {contestDetail.problems.length}
              </span>
            </div>

            <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl">
              <span className="text-[10px] text-slate-500 uppercase font-semibold block">Penalty / Time</span>
              <span className="text-base font-bold text-slate-300 font-mono mt-0.5 block">
                {contestDetail.user_penalty_minutes} <span className="text-xs text-slate-500 font-normal">min</span>
              </span>
            </div>

            <div className="bg-slate-950/60 border border-slate-800 p-3 rounded-xl flex items-center justify-between">
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-semibold block">Player Profile</span>
                <span className="text-xs font-semibold text-slate-200 mt-0.5 block line-clamp-1">
                  {currentUser ? currentUser.user_name : 'Guest'}
                </span>
              </div>
              {!contestDetail.user_registered && !isFinished ? (
                <button
                  onClick={handleRegister}
                  className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition-colors cursor-pointer"
                >
                  {currentUser ? 'Join' : 'Sign In'}
                </button>
              ) : (
                <span className="text-[11px] text-emerald-400 font-semibold">Active</span>
              )}
            </div>
          </div>
        </div>

        {/* Contest Arena Tabs */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-2">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveTab('problems')}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition-colors cursor-pointer ${
                activeTab === 'problems'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 bg-slate-900 border border-slate-800'
              }`}
            >
              Problems Set ({contestDetail.problems.length})
            </button>
            <button
              onClick={() => { setActiveTab('leaderboard'); fetchLeaderboard(contestDetail.contest_id); }}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition-colors cursor-pointer flex items-center space-x-1.5 ${
                activeTab === 'leaderboard'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 bg-slate-900 border border-slate-800'
              }`}
            >
              <Medal className="w-3.5 h-3.5 text-amber-400" />
              <span>Leaderboard</span>
            </button>
          </div>

          {activeTab === 'leaderboard' && (
            <button
              onClick={() => fetchLeaderboard(contestDetail.contest_id)}
              disabled={loadingLeaderboard}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 rounded-lg text-xs font-medium transition-colors cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingLeaderboard ? 'animate-spin text-indigo-400' : ''}`} />
              <span>Refresh Standings</span>
            </button>
          )}
        </div>

        {/* Tab Content 1: Problems List */}
        {activeTab === 'problems' && (
          <div className="space-y-4">
            {isUpcoming ? (
              <div className="p-12 text-center bg-slate-900/40 rounded-2xl border border-dashed border-slate-800 space-y-3">
                <Lock className="w-8 h-8 text-amber-400 mx-auto" />
                <h4 className="text-sm font-bold text-slate-200">Problem Set is Locked</h4>
                <p className="text-xs text-slate-500 max-w-md mx-auto">
                  The problem statements will unlock automatically when the contest starts.
                </p>
              </div>
            ) : (
              <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden divide-y divide-slate-800">
                {contestDetail.problems.map((prob, idx) => (
                  <div
                    key={prob.problem_id}
                    onClick={() => onSelectContestProblem(prob.slug, contestDetail.contest_id, contestDetail.title)}
                    className="p-4 flex items-center justify-between hover:bg-slate-800/40 transition-colors cursor-pointer group"
                  >
                    <div className="flex items-center space-x-3.5">
                      <div className="shrink-0">
                        {prob.is_solved ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                        ) : (
                          <Circle className="w-5 h-5 text-slate-600 group-hover:text-slate-400 transition-colors" />
                        )}
                      </div>
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-mono text-slate-500">#{idx + 1}</span>
                          <h4 className="font-semibold text-sm text-slate-200 group-hover:text-indigo-400 transition-colors">
                            {prob.title}
                          </h4>
                        </div>
                        <span className="text-[11px] text-slate-500">100 Points • Submissions: {prob.submission_count}</span>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${getDifficultyColor(prob.difficulty)}`}>
                        {prob.difficulty}
                      </span>
                      <button className="inline-flex items-center space-x-1 px-3 py-1.5 bg-indigo-600/10 hover:bg-indigo-600 text-indigo-400 hover:text-white rounded-lg text-xs font-medium transition-colors cursor-pointer">
                        <span>{prob.is_solved ? 'Review' : 'Solve'}</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab Content 2: Live Leaderboard Standings Table */}
        {activeTab === 'leaderboard' && (
          <div className="space-y-4">
            {loadingLeaderboard && !leaderboard ? (
              <div className="p-12 text-center text-xs text-slate-500 bg-slate-900/40 rounded-xl border border-slate-800">
                Calculating live rankings and penalty scores...
              </div>
            ) : !leaderboard || leaderboard.standings.length === 0 ? (
              <div className="p-12 text-center text-xs text-slate-500 bg-slate-900/40 rounded-xl border border-slate-800">
                No participant submissions logged yet for this contest.
              </div>
            ) : (
              <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 bg-slate-950/80 text-slate-400 font-mono text-[11px]">
                        <th className="py-3 px-4 w-16 text-center">Rank</th>
                        <th className="py-3 px-4">Competitor</th>
                        <th className="py-3 px-4 text-center">Score</th>
                        <th className="py-3 px-4 text-center">Solved</th>
                        <th className="py-3 px-4 text-center">Penalty</th>
                        {leaderboard.problems.map((p, idx) => (
                          <th key={p.problem_id} className="py-3 px-3 text-center min-w-[90px]">
                            <span className="block text-slate-200">#{idx + 1}</span>
                            <span className="block text-[9px] text-slate-500 font-normal truncate max-w-[80px]">{p.title}</span>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/80">
                      {leaderboard.standings.map((row) => {
                        const isSelf = currentUser && row.user_id === currentUser.user_id;
                        return (
                          <tr
                            key={row.user_id}
                            className={`transition-colors ${
                              isSelf
                                ? 'bg-indigo-950/40 font-semibold'
                                : 'hover:bg-slate-800/30'
                            }`}
                          >
                            <td className="py-3.5 px-4 text-center">
                              {getRankBadge(row.rank)}
                            </td>

                            <td className="py-3.5 px-4">
                              <div className="flex items-center space-x-2">
                                <span className={`text-xs ${isSelf ? 'text-indigo-300 font-bold' : 'text-slate-200'}`}>
                                  {row.user_name}
                                </span>
                                {isSelf && (
                                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-indigo-600 text-white">
                                    YOU
                                  </span>
                                )}
                              </div>
                              <span className="text-[10px] font-mono text-slate-500">{row.user_id}</span>
                            </td>

                            <td className="py-3.5 px-4 text-center font-mono font-bold text-amber-400">
                              {row.score}
                            </td>

                            <td className="py-3.5 px-4 text-center font-mono text-emerald-400 font-semibold">
                              {row.problems_solved} / {leaderboard.problems.length}
                            </td>

                            <td className="py-3.5 px-4 text-center font-mono text-slate-400">
                              {row.total_penalty_min}m
                            </td>

                            {leaderboard.problems.map((p) => {
                              const cell = row.problem_results[p.problem_id];
                              if (!cell || cell.status === 'UNTOUCHED') {
                                return (
                                  <td key={p.problem_id} className="py-3.5 px-3 text-center text-slate-700 font-mono text-xs">
                                    -
                                  </td>
                                );
                              }

                              if (cell.status === 'SOLVED') {
                                return (
                                  <td key={p.problem_id} className="py-3.5 px-3 text-center">
                                    <span className="inline-block px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-[10px] font-bold">
                                      +{cell.attempts_count} <span className="text-[9px] text-slate-400 font-normal">({cell.solved_time_min}m)</span>
                                    </span>
                                  </td>
                                );
                              }

                              return (
                                <td key={p.problem_id} className="py-3.5 px-3 text-center">
                                  <span className="inline-block px-2 py-0.5 rounded bg-red-500/10 border border-red-500/30 text-red-400 font-mono text-[10px] font-bold">
                                    -{cell.attempts_count}
                                  </span>
                                </td>
                              );
                            })}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  // --- View 2: Contests List ---
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-slate-100">Coding Contests</h2>
          <p className="text-xs text-slate-400">Join scheduled contests, test your algorithms, and climb the live rankings</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {contests.map((c) => (
          <div
            key={c.contest_id}
            onClick={() => fetchContestDetail(c.contest_id)}
            className="bg-slate-900/80 border border-slate-800 hover:border-indigo-500/50 p-6 rounded-2xl transition-all cursor-pointer space-y-4 group hover:shadow-xl hover:shadow-indigo-950/40"
          >
            <div className="flex items-start justify-between">
              <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getStatusBadge(c.status)}`}>
                ● {c.status}
              </span>
              <span className="text-xs font-mono text-slate-500 flex items-center space-x-1">
                <Clock className="w-3.5 h-3.5" />
                <span>{c.duration_minutes} mins</span>
              </span>
            </div>

            <div>
              <h3 className="text-base font-bold text-slate-100 group-hover:text-indigo-300 transition-colors">
                {c.title}
              </h3>
              <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                {c.description}
              </p>
            </div>

            <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
              <span className="font-mono text-slate-500">{c.problem_count} Problems • {c.participant_count} Registered</span>
              <button className="inline-flex items-center space-x-1 text-indigo-400 group-hover:text-indigo-300 font-semibold cursor-pointer">
                <span>Enter Arena</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}