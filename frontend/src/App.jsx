// frontend/src/App.jsx

import React, { useState, useEffect } from 'react';
import { 
  FolderGit2, 
  Plus, 
  Upload, 
  FileCode, 
  Sparkles, 
  ArrowRight, 
  RefreshCw, 
  AlertCircle, 
  ShieldCheck, 
  Bot, 
  ChevronDown, 
  ChevronUp, 
  Layers 
} from 'lucide-react';
import DiffViewer from './components/DiffViewer';
import AssessmentDetail from './components/AssessmentDetail';

export default function App() {
  // Navigation State
  const [currentView, setCurrentView] = useState('assessments'); // 'assessments' | 'assessment_detail' | 'quick_scan'
  const [assessments, setAssessments] = useState([]);
  const [selectedAssessment, setSelectedAssessment] = useState(null);
  const [loadingAssessments, setLoadingAssessments] = useState(false);

  // New Assessment Form Modal
  const [showNewModal, setShowNewModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [creating, setCreating] = useState(false);

  // Quick Scan / Single-batch Upload State
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [activeComparison, setActiveComparison] = useState(null);
  const [expandedForensics, setExpandedForensics] = useState({});

  const fetchAssessments = async () => {
    try {
      setLoadingAssessments(true);
      const res = await fetch('http://127.0.0.1:8000/api/assessments');
      if (res.ok) {
        const data = await res.json();
        setAssessments(data);
      }
    } catch (err) {
      console.error('Failed to load assessments:', err);
    } finally {
      setLoadingAssessments(false);
    }
  };

  useEffect(() => {
    fetchAssessments();
  }, []);

  const handleCreateAssessment = async (e) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    setCreating(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/assessments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle, description: newDesc }),
      });
      if (res.ok) {
        setNewTitle('');
        setNewDesc('');
        setShowNewModal(false);
        fetchAssessments();
      }
    } catch (err) {
      console.error('Error creating assessment:', err);
    } finally {
      setCreating(false);
    }
  };

  const handleQuickUpload = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least 2 .cpp files or a .zip file.');
      return;
    }

    setAnalyzing(true);
    setError('');

    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append('files', file);
    });

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
      setError(err.message || 'Failed to connect to backend server.');
    } finally {
      setAnalyzing(false);
    }
  };

  const getBadgeColor = (score) => {
    if (score >= 70) return 'bg-red-500/10 text-red-400 border-red-500/30';
    if (score >= 40) return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  };

  const getAiScoreBadge = (score) => {
    if (score >= 60) return { bg: 'bg-red-500/10 border-red-500/30 text-red-400', label: 'High AI Probability' };
    if (score >= 25) return { bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400', label: 'Suspicious Artifacts' };
    return { bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400', label: 'Human Authored' };
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-12">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Main Navbar */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div className="space-y-1">
            <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 bg-indigo-500/10 border border-indigo-500/30 rounded-full text-indigo-400 text-xs font-medium">
              <Sparkles className="w-3 h-3" />
              <span>Assessment-Aware Integrity Platform</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white">
              Code Assessment Integrity Platform
            </h1>
          </div>

          {/* View Mode Switcher */}
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 p-1 rounded-xl text-xs">
            <button
              onClick={() => { setCurrentView('assessments'); setSelectedAssessment(null); }}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                currentView === 'assessments' || currentView === 'assessment_detail'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Assessments Workspace
            </button>
            <button
              onClick={() => setCurrentView('quick_scan')}
              className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                currentView === 'quick_scan'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Ad-Hoc File Scanner
            </button>
          </div>
        </div>

        {/* View 1: Assessment Detail View */}
        {currentView === 'assessment_detail' && selectedAssessment && (
          <AssessmentDetail
            assessment={selectedAssessment}
            onBack={() => { setCurrentView('assessments'); setSelectedAssessment(null); fetchAssessments(); }}
            onSelectQuestion={(q) => {
              // Switches to Quick Scan with question context for now (Phase 3 will enhance this)
              setCurrentView('quick_scan');
            }}
          />
        )}

        {/* View 2: Assessments List View */}
        {currentView === 'assessments' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-slate-100">Assessments & Exams</h2>
                <p className="text-xs text-slate-400">Manage cohorts, problem baselines, and submission integrity</p>
              </div>

              <button
                onClick={() => setShowNewModal(true)}
                className="inline-flex items-center space-x-1.5 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-medium transition-all shadow-md shadow-indigo-600/20 cursor-pointer"
              >
                <Plus className="w-4 h-4" />
                <span>Create Assessment</span>
              </button>
            </div>

            {loadingAssessments ? (
              <div className="p-12 text-center text-xs text-slate-500 bg-slate-900/40 rounded-2xl border border-slate-800">
                Loading assessments...
              </div>
            ) : assessments.length === 0 ? (
              <div className="p-12 text-center bg-slate-900/40 rounded-2xl border border-dashed border-slate-800 space-y-3">
                <Layers className="w-10 h-10 text-slate-600 mx-auto" />
                <h3 className="text-sm font-semibold text-slate-300">No assessments created yet</h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">
                  Create your first assessment to organize problem statements and monitor cohort similarity baselines.
                </p>
                <button
                  onClick={() => setShowNewModal(true)}
                  className="px-4 py-2 bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 rounded-lg text-xs font-medium hover:bg-indigo-600/30 transition-colors"
                >
                  Create Assessment Now
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                {assessments.map((asm) => (
                  <div
                    key={asm.assessment_id}
                    onClick={() => { setSelectedAssessment(asm); setCurrentView('assessment_detail'); }}
                    className="bg-slate-900/80 border border-slate-800 hover:border-indigo-500/50 p-5 rounded-2xl transition-all cursor-pointer space-y-4 group hover:shadow-lg"
                  >
                    <div className="flex items-start justify-between">
                      <div className="p-2.5 bg-indigo-600/10 text-indigo-400 rounded-xl group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                        <FolderGit2 className="w-5 h-5" />
                      </div>
                      <span className="text-[11px] font-mono text-slate-500 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                        {asm.assessment_id}
                      </span>
                    </div>

                    <div>
                      <h3 className="font-bold text-slate-100 group-hover:text-indigo-300 transition-colors">
                        {asm.title}
                      </h3>
                      <p className="text-xs text-slate-400 line-clamp-2 mt-1">
                        {asm.description || 'No description provided.'}
                      </p>
                    </div>

                    <div className="pt-3 border-t border-slate-800/80 grid grid-cols-2 gap-2 text-xs text-slate-400">
                      <div>
                        <span className="text-slate-500 block text-[10px] uppercase">Questions</span>
                        <span className="font-semibold text-slate-200">{asm.question_count}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[10px] uppercase">Submissions</span>
                        <span className="font-semibold text-slate-200">{asm.total_submissions}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* View 3: Ad-Hoc / Quick Scan View (Preserves existing working flow) */}
        {currentView === 'quick_scan' && (
          <div className="space-y-8">
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-4">
              <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500/60 transition-colors rounded-xl p-8 text-center flex flex-col items-center justify-center space-y-3 cursor-pointer relative bg-slate-900/30">
                <input 
                  type="file" 
                  multiple 
                  accept=".cpp,.cc,.cxx,.zip"
                  onChange={(e) => { setSelectedFiles(Array.from(e.target.files)); setError(''); }}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
                <div className="p-3 bg-indigo-600/10 text-indigo-400 rounded-xl">
                  <Upload className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-200">
                    {selectedFiles.length > 0 ? `${selectedFiles.length} files selected` : "Click or drag C++ files / .zip archive here"}
                  </p>
                  <p className="text-xs text-slate-500 mt-1">Supports batch .cpp files or single contest .zip</p>
                </div>
              </div>

              {selectedFiles.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-2">
                  {selectedFiles.map((file, idx) => (
                    <span key={idx} className="px-2.5 py-1 bg-slate-800 border border-slate-700 text-slate-300 text-xs rounded-md">
                      {file.name}
                    </span>
                  ))}
                </div>
              )}

              {error && (
                <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-xs flex items-center space-x-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <button
                onClick={handleQuickUpload}
                disabled={analyzing || selectedFiles.length === 0}
                className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium py-3 rounded-xl transition-all shadow-lg shadow-indigo-600/20 flex items-center justify-center space-x-2 cursor-pointer"
              >
                {analyzing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Running AST & AI Forensic Analysis...</span>
                  </>
                ) : (
                  <span>Run Plagiarism & AI Detection</span>
                )}
              </button>
            </div>

            {/* Results Section */}
            {result && (
              <div className="space-y-8">
                {/* Stats Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                    <p className="text-xs text-slate-400">Total Submissions</p>
                    <p className="text-2xl font-bold text-white mt-1">{result.total_files_analyzed}</p>
                  </div>
                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                    <div className="flex items-center justify-between">
                      <p className="text-xs text-slate-400">Purged Template Hashes</p>
                      <span className="flex items-center space-x-1 text-xs text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/30">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        <span>Auto-Ignored</span>
                      </span>
                    </div>
                    <p className="text-2xl font-bold text-indigo-400 mt-1">{result.boilerplate_hashes_filtered}</p>
                  </div>
                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                    <p className="text-xs text-slate-400">Flagged Comparisons</p>
                    <p className="text-2xl font-bold text-white mt-1">{result.comparisons.length}</p>
                  </div>
                </div>

                {/* AI Ghostwriter & Watermark Forensic Audit Section */}
                {result.forensics && (
                  <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                    <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
                      <div className="flex items-center space-x-2">
                        <Bot className="w-5 h-5 text-indigo-400" />
                        <h3 className="font-semibold text-slate-200">AI Ghostwriter & Watermark Forensic Audit</h3>
                      </div>
                      <span className="text-xs text-slate-500">Zero-width characters, LLM docstrings & markdown checks</span>
                    </div>
                    <div className="divide-y divide-slate-800/60">
                      {Object.entries(result.forensics).map(([fname, report]) => {
                        const badge = getAiScoreBadge(report.ai_confidence_score);
                        const isExpanded = !!expandedForensics[fname];

                        return (
                          <div key={fname} className="p-4 space-y-2 hover:bg-slate-800/20 transition-colors">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <FileCode className="w-4 h-4 text-slate-400" />
                                <span className="font-mono text-sm text-slate-200">{fname}</span>
                              </div>
                              <div className="flex items-center space-x-3">
                                <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${badge.bg}`}>
                                  {report.ai_confidence_score}% — {badge.label}
                                </span>
                                {report.flags.length > 0 && (
                                  <button
                                    onClick={() => setExpandedForensics(p => ({ ...p, [fname]: !p[fname] }))}
                                    className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800 transition-colors cursor-pointer"
                                  >
                                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                                  </button>
                                )}
                              </div>
                            </div>

                            {isExpanded && report.flags.length > 0 && (
                              <div className="mt-3 p-3 bg-slate-950/80 border border-slate-800 rounded-lg space-y-1.5 text-xs font-mono">
                                <p className="text-slate-400 font-sans font-medium text-xs mb-1">Detected Forensic Signatures:</p>
                                {report.flags.map((flag, idx) => (
                                  <div key={idx} className="flex items-start space-x-2 text-red-300/90">
                                    <span className="text-red-500 shrink-0">•</span>
                                    <span>{flag}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Leaderboard Table */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                  <div className="p-4 border-b border-slate-800 bg-slate-950/60">
                    <h3 className="font-semibold text-slate-200">Plagiarism Comparison Leaderboard</h3>
                  </div>
                  <div className="divide-y divide-slate-800">
                    {result.comparisons.map((comp, idx) => (
                      <div key={idx} className="p-4 flex items-center justify-between hover:bg-slate-800/40 transition-colors">
                        <div className="flex items-center space-x-4">
                          <FileCode className="w-5 h-5 text-slate-500" />
                          <div>
                            <p className="font-medium text-slate-200 text-sm">
                              {comp.file_a} <span className="text-slate-500 font-normal">and</span> {comp.file_b}
                            </p>
                            <p className="text-xs text-slate-500 mt-0.5">
                              {comp.shared_fingerprints_count} matching Winnowed fingerprints
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center space-x-4">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${getBadgeColor(comp.similarity_score)}`}>
                            {comp.similarity_score}% Match
                          </span>
                          <button
                            onClick={() => setActiveComparison(comp)}
                            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg transition-colors flex items-center space-x-1 cursor-pointer"
                          >
                            <span>View Diff</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Create Assessment Modal */}
        {showNewModal && (
          <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md p-6 space-y-4 shadow-2xl">
              <h3 className="text-base font-bold text-white">Create New Assessment</h3>
              <form onSubmit={handleCreateAssessment} className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Assessment Title</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. CS201 Data Structures Lab Exam"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Description (Optional)</label>
                  <textarea
                    rows="3"
                    placeholder="Semester, cohort name, or contest notes..."
                    value={newDesc}
                    onChange={(e) => setNewDesc(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div className="flex items-center justify-end space-x-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowNewModal(false)}
                    className="px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={creating}
                    className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-xs font-medium"
                  >
                    {creating ? 'Creating...' : 'Create Assessment'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Side-by-side Modal */}
        {activeComparison && (
          <DiffViewer
            comparison={activeComparison}
            filesContent={result.files_content}
            boilerplateSpans={result.file_boilerplate_spans}
            onClose={() => setActiveComparison(null)}
          />
        )}

      </div>
    </div>
  );
}