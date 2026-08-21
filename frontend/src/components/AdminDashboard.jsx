// frontend/src/components/AdminDashboard.jsx

import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  Users, 
  Activity, 
  AlertTriangle, 
  Eye, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Search, 
  Layers, 
  LogOut,
  RefreshCw,
  Sliders,
  ExternalLink,
  Bot,
  Download,
  Ban,
  CheckCheck,
  ShieldCheck
} from 'lucide-react';

export default function AdminDashboard({ adminUser, onLogout, onLaunchDiffViewer }) {
  const [contests, setContests] = useState([]);
  const [selectedContestId, setSelectedContestId] = useState('');
  const [auditReport, setAuditReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('heatmap'); // 'heatmap' | 'suspects'
  const [selectedProblemIdx, setSelectedProblemIdx] = useState(0);
  const [minSimilarityThreshold, setMinSimilarityThreshold] = useState(60);
  const [actionLoadingId, setActionLoadingId] = useState(null);

  // Fetch Contests List
  const fetchContests = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/admin/contests');
      if (res.ok) {
        const data = await res.json();
        setContests(data);
        if (data.length > 0 && !selectedContestId) {
          setSelectedContestId(data[0].contest_id);
        }
      }
    } catch (err) {
      console.error('Failed to load contests:', err);
    }
  };

  // Fetch Contest Audit Report
  const fetchAuditReport = async (contestId) => {
    if (!contestId) return;
    try {
      setLoading(true);
      const res = await fetch(`http://127.0.0.1:8000/api/contests/${contestId}/audit`);
      if (res.ok) {
        const data = await res.json();
        setAuditReport(data);
      }
    } catch (err) {
      console.error('Failed to load audit report:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContests();
  }, []);

  useEffect(() => {
    if (selectedContestId) {
      fetchAuditReport(selectedContestId);
    }
  }, [selectedContestId]);

  // Dispatch Admin Decisions (CONFIRMED, DISQUALIFIED, CLEARED)
  const handleDecision = async (pair, action, targetUserId) => {
    const pairKey = `${pair.problem_id}_${targetUserId}_${action}`;
    try {
      setActionLoadingId(pairKey);
      const res = await fetch('http://127.0.0.1:8000/api/admin/contests/decision', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contest_id: selectedContestId,
          problem_id: pair.problem_id,
          user_id: targetUserId || pair.user_a_id,
          partner_user_id: targetUserId === pair.user_a_id ? pair.user_b_id : pair.user_a_id,
          action: action,
          reason: `Admin forensic verdict: ${action} applied during contest review.`,
          admin_id: adminUser?.admin_id || 'admin_root_01'
        }),
      });

      if (res.ok) {
        await fetchAuditReport(selectedContestId);
      } else {
        const errData = await res.json();
        alert(`Failed to apply action: ${errData.detail || 'Server error'}`);
      }
    } catch (err) {
      console.error('Failed to submit admin decision:', err);
    } finally {
      setActionLoadingId(null);
    }
  };

  // Download Audit Report CSV
  const handleExportCSV = () => {
    if (!selectedContestId) return;
    window.open(`http://127.0.0.1:8000/api/admin/contests/${selectedContestId}/export/csv`, '_blank');
  };

  const getHeatmapColor = (score) => {
    if (score >= 85) return 'bg-red-500/80 text-white font-bold border-red-400';
    if (score >= 65) return 'bg-amber-500/70 text-black font-semibold border-amber-400';
    if (score >= 40) return 'bg-yellow-500/40 text-yellow-200 border-yellow-500/30';
    if (score > 0) return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/20';
    return 'bg-[#18181b] text-slate-600 border-[#27272a]';
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'DISQUALIFIED':
        return 'bg-red-500/20 text-red-400 border-red-500/40';
      case 'CONFIRMED':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'CLEARED':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
      default:
        return 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40';
    }
  };

  const activeMatrix = auditReport?.similarity_matrices?.[selectedProblemIdx];
  const filteredSuspects = auditReport?.suspect_pairs?.filter(
    (sp) => sp.ast_similarity >= minSimilarityThreshold || sp.suspicion_score >= minSimilarityThreshold
  ) || [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-6">
      
      {/* Top Header */}
      <div className="bg-[#18181b] border border-[#27272a] rounded-2xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-indigo-400">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-100">Forensic Audit & Collusion Radar</h1>
              <p className="text-xs text-slate-400">Automated AST Pairwise Tokenizer • Temporal Anomaly Inspection & Leaderboard Reranking</p>
            </div>
          </div>
        </div>

        {/* Controls / Contest Switcher & Export */}
        <div className="flex flex-wrap items-center gap-2.5">
          <select
            value={selectedContestId}
            onChange={(e) => setSelectedContestId(e.target.value)}
            className="bg-[#121214] border border-[#27272a] text-slate-200 text-xs rounded-xl px-3 py-2 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            {contests.map((c) => (
              <option key={c.contest_id} value={c.contest_id}>
                {c.title} ({c.status})
              </option>
            ))}
          </select>

          <button
            onClick={handleExportCSV}
            title="Download Forensic Audit CSV"
            className="px-3 py-2 bg-[#27272a] hover:bg-[#3f3f46] text-slate-200 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-colors cursor-pointer border border-[#3f3f46]"
          >
            <Download className="w-3.5 h-3.5 text-emerald-400" />
            <span>Export CSV</span>
          </button>

          <button
            onClick={() => fetchAuditReport(selectedContestId)}
            className="p-2 bg-[#27272a] hover:bg-[#3f3f46] text-slate-200 rounded-xl text-xs flex items-center space-x-1.5 transition-colors cursor-pointer"
            title="Re-run Forensic Audit"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-indigo-400' : ''}`} />
          </button>

          <button
            onClick={onLogout}
            className="px-3 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-colors cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Exit Admin</span>
          </button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      {auditReport && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-[#18181b] border border-[#27272a] rounded-xl p-4">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Audited Participants</span>
            <div className="flex items-center space-x-2 mt-1">
              <Users className="w-4 h-4 text-indigo-400" />
              <span className="text-xl font-bold font-mono text-slate-100">{auditReport.total_participants}</span>
            </div>
          </div>

          <div className="bg-[#18181b] border border-[#27272a] rounded-xl p-4">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Submissions Analyzed</span>
            <div className="flex items-center space-x-2 mt-1">
              <Activity className="w-4 h-4 text-emerald-400" />
              <span className="text-xl font-bold font-mono text-slate-100">{auditReport.total_submissions_audited}</span>
            </div>
          </div>

          <div className="bg-[#18181b] border border-[#27272a] rounded-xl p-4">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Flagged Suspect Pairs</span>
            <div className="flex items-center space-x-2 mt-1">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span className="text-xl font-bold font-mono text-amber-400">{auditReport.flagged_pairs_count}</span>
            </div>
          </div>

          <div className="bg-[#18181b] border border-[#27272a] rounded-xl p-4">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Audit State</span>
            <div className="flex items-center space-x-2 mt-1">
              <span className="inline-block w-2.5 h-2.5 rounded-full bg-indigo-500 animate-pulse"></span>
              <span className="text-xs font-bold font-mono text-indigo-400">Review Window Active</span>
            </div>
          </div>
        </div>
      )}

      {/* Tabs & Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#27272a] pb-3">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveTab('heatmap')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'heatmap'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20'
                : 'bg-[#18181b] text-slate-400 hover:text-slate-200 border border-[#27272a]'
            }`}
          >
            Pairwise Heatmap Matrix
          </button>
          <button
            onClick={() => setActiveTab('suspects')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer flex items-center space-x-1.5 ${
              activeTab === 'suspects'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20'
                : 'bg-[#18181b] text-slate-400 hover:text-slate-200 border border-[#27272a]'
            }`}
          >
            <span>Collusion Review Queue</span>
            {auditReport?.suspect_pairs?.length > 0 && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-amber-500/20 text-amber-300 font-mono">
                {auditReport.suspect_pairs.length}
              </span>
            )}
          </button>
        </div>

        {activeTab === 'suspects' && (
          <div className="flex items-center space-x-3 text-xs text-slate-400">
            <span>Min Suspicion Threshold: <strong className="text-slate-200 font-mono">{minSimilarityThreshold}%</strong></span>
            <input
              type="range"
              min="30"
              max="90"
              step="5"
              value={minSimilarityThreshold}
              onChange={(e) => setMinSimilarityThreshold(Number(e.target.value))}
              className="accent-indigo-500 cursor-pointer w-32"
            />
          </div>
        )}
      </div>

      {/* Main Workspace Panels */}
      {loading ? (
        <div className="p-16 text-center text-xs text-slate-500 bg-[#18181b] rounded-2xl border border-[#27272a]">
          Computing AST tokenizations & cross-participant collision graphs...
        </div>
      ) : activeTab === 'heatmap' ? (
        
        /* HEATMAP MATRIX PANEL */
        <div className="bg-[#18181b] border border-[#27272a] rounded-2xl p-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-bold text-slate-100">Participant-to-Participant AST Similarity Matrix</h3>
              <p className="text-xs text-slate-400">Boilerplate code stripped • Pairwise normalized token overlap</p>
            </div>

            {auditReport?.similarity_matrices?.length > 1 && (
              <div className="flex items-center space-x-1.5">
                {auditReport.similarity_matrices.map((m, idx) => (
                  <button
                    key={m.problem_id}
                    onClick={() => setSelectedProblemIdx(idx)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                      selectedProblemIdx === idx ? 'bg-indigo-600 text-white' : 'bg-[#121214] text-slate-400 hover:text-slate-200 border border-[#27272a]'
                    }`}
                  >
                    {m.problem_title}
                  </button>
                ))}
              </div>
            )}
          </div>

          {activeMatrix && activeMatrix.participant_names.length > 0 ? (
            <div className="overflow-x-auto pt-2">
              <table className="border-collapse text-center mx-auto">
                <thead>
                  <tr>
                    <th className="p-2 text-[11px] font-semibold text-slate-500 text-left">Competitor</th>
                    {activeMatrix.participant_names.map((name, i) => (
                      <th key={i} className="p-2 text-[11px] font-semibold text-slate-400 max-w-[90px] truncate" title={name}>
                        {name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {activeMatrix.matrix.map((row, rIdx) => (
                    <tr key={rIdx}>
                      <td className="p-2 text-[11px] font-semibold text-slate-300 text-left whitespace-nowrap pr-4">
                        {activeMatrix.participant_names[rIdx]}
                      </td>
                      {row.map((val, cIdx) => (
                        <td key={cIdx} className="p-1.5">
                          <button
                            onClick={() => {
                              if (rIdx !== cIdx && val >= 50) {
                                const uA = activeMatrix.participant_ids[rIdx];
                                const uB = activeMatrix.participant_ids[cIdx];
                                const foundPair = auditReport.suspect_pairs.find(
                                  sp => (sp.user_a_id === uA && sp.user_b_id === uB) || (sp.user_a_id === uB && sp.user_b_id === uA)
                                );
                                if (foundPair) {
                                  onLaunchDiffViewer(foundPair.user_a_code, foundPair.user_b_code, foundPair.user_a_name, foundPair.user_b_name);
                                }
                              }
                            }}
                            className={`w-14 h-10 rounded-lg text-xs font-mono border transition-transform hover:scale-105 flex items-center justify-center cursor-pointer ${getHeatmapColor(val)}`}
                            title={`Pair: ${activeMatrix.participant_names[rIdx]} vs ${activeMatrix.participant_names[cIdx]} (${val}%)`}
                          >
                            {rIdx === cIdx ? '—' : `${Math.round(val)}%`}
                          </button>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-12 text-center text-xs text-slate-500">
              No participant solutions available yet for this problem.
            </div>
          )}
        </div>

      ) : (

        /* SUSPECT COLLUSION QUEUE WITH ADMIN DECISION ACTIONS */
        <div className="space-y-3">
          {filteredSuspects.length === 0 ? (
            <div className="p-12 text-center text-xs text-slate-500 bg-[#18181b] rounded-2xl border border-[#27272a]">
              No candidate pairs exceeded the {minSimilarityThreshold}% suspicion threshold.
            </div>
          ) : (
            filteredSuspects.map((pair, idx) => (
              <div
                key={idx}
                className="bg-[#18181b] border border-[#27272a] rounded-2xl p-5 hover:border-indigo-500/40 transition-all flex flex-col lg:flex-row lg:items-center justify-between gap-4"
              >
                <div className="space-y-2">
                  <div className="flex items-center space-x-2.5">
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono border ${getStatusBadge(pair.status)}`}>
                      {pair.status}
                    </span>
                    <h4 className="text-sm font-bold text-slate-100">
                      {pair.user_a_name} <span className="text-slate-500 font-normal">vs</span> {pair.user_b_name}
                    </h4>
                    <span className="text-xs text-slate-400 font-mono">• {pair.problem_title}</span>
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    {pair.flags.map((flag, fIdx) => (
                      <span key={fIdx} className="px-2 py-0.5 rounded bg-[#121214] border border-[#27272a] text-[10px] font-mono text-slate-300">
                        • {flag}
                      </span>
                    ))}
                  </div>

                  <div className="flex items-center space-x-4 text-xs font-mono text-slate-400 pt-1">
                    <span>AST Similarity: <strong className="text-red-400">{pair.ast_similarity}%</strong></span>
                    <span>Time Delta: <strong className="text-amber-400">{Math.round(pair.time_delta_seconds)}s</strong></span>
                    <span>Suspicion Score: <strong className="text-indigo-400">{pair.suspicion_score}</strong></span>
                  </div>
                </div>

                {/* Admin Decision Action Controls */}
                <div className="flex flex-wrap items-center gap-2 shrink-0">
                  <button
                    onClick={() => onLaunchDiffViewer(pair.user_a_code, pair.user_b_code, pair.user_a_name, pair.user_b_name)}
                    className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-colors shadow-sm cursor-pointer"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>Diff</span>
                  </button>

                  <button
                    onClick={() => handleDecision(pair, 'CONFIRMED', pair.user_a_id)}
                    disabled={actionLoadingId !== null}
                    className="px-2.5 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-xl text-xs font-semibold flex items-center space-x-1 transition-colors cursor-pointer disabled:opacity-50"
                    title="Confirm Suspicion / Mark Collusion"
                  >
                    <CheckCircle2 className="w-3 h-3 text-amber-400" />
                    <span>Confirm</span>
                  </button>

                  <button
                    onClick={() => handleDecision(pair, 'DISQUALIFIED', pair.user_a_id)}
                    disabled={actionLoadingId !== null}
                    className="px-2.5 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-300 border border-red-500/30 rounded-xl text-xs font-semibold flex items-center space-x-1 transition-colors cursor-pointer disabled:opacity-50"
                    title="Disqualify Participant & Reset Score"
                  >
                    <Ban className="w-3 h-3 text-red-400" />
                    <span>Disqualify A</span>
                  </button>

                  <button
                    onClick={() => handleDecision(pair, 'DISQUALIFIED', pair.user_b_id)}
                    disabled={actionLoadingId !== null}
                    className="px-2.5 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-300 border border-red-500/30 rounded-xl text-xs font-semibold flex items-center space-x-1 transition-colors cursor-pointer disabled:opacity-50"
                    title="Disqualify Partner Participant & Reset Score"
                  >
                    <Ban className="w-3 h-3 text-red-400" />
                    <span>Disqualify B</span>
                  </button>

                  <button
                    onClick={() => handleDecision(pair, 'CLEARED', pair.user_a_id)}
                    disabled={actionLoadingId !== null}
                    className="px-2.5 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-xl text-xs font-semibold flex items-center space-x-1 transition-colors cursor-pointer disabled:opacity-50"
                    title="Clear Flag (False Positive)"
                  >
                    <CheckCheck className="w-3 h-3 text-emerald-400" />
                    <span>Clear</span>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

      )}
    </div>
  );
}