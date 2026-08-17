// frontend/src/App.jsx

import React, { useState } from 'react';
import { 
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
  CheckCircle2, 
  AlertTriangle 
} from 'lucide-react';
import DiffViewer from './components/DiffViewer';

export default function App() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [activeComparison, setActiveComparison] = useState(null);
  const [expandedForensics, setExpandedForensics] = useState({});

  const handleFileChange = (e) => {
    setSelectedFiles(Array.from(e.target.files));
    setError('');
  };

  const toggleForensicExpand = (fname) => {
    setExpandedForensics((prev) => ({
      ...prev,
      [fname]: !prev[fname],
    }));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least 2 .cpp files or a .zip file.');
      return;
    }

    setLoading(true);
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
      setError(err.message || 'Failed to connect to backend server. Make sure FastAPI is running on port 8000.');
    } finally {
      setLoading(false);
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
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="space-y-3">
          <div className="inline-flex items-center space-x-2 px-3 py-1 bg-indigo-500/10 border border-indigo-500/30 rounded-full text-indigo-400 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AST Normalizer • Winnowing Engine • LLM Ghostwriter Buster</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-white">
            CP Plagiarism & AI Forensic Dashboard
          </h1>
          <p className="text-slate-400 text-sm md:text-base">
            Upload C++ submissions to detect structural plagiarism, auto-purge starter boilerplate, and unmask ChatGPT/Claude-generated submissions.
          </p>
        </div>

        {/* File Upload Box */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-4">
          <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500/60 transition-colors rounded-xl p-8 text-center flex flex-col items-center justify-center space-y-3 cursor-pointer relative bg-slate-900/30">
            <input 
              type="file" 
              multiple 
              accept=".cpp,.cc,.cxx,.zip"
              onChange={handleFileChange}
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
            onClick={handleUpload}
            disabled={loading || selectedFiles.length === 0}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium py-3 rounded-xl transition-all shadow-lg shadow-indigo-600/20 flex items-center justify-center space-x-2 cursor-pointer"
          >
            {loading ? (
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
                                onClick={() => toggleForensicExpand(fname)}
                                className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800 transition-colors cursor-pointer"
                              >
                                {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                              </button>
                            )}
                          </div>
                        </div>

                        {/* Red Flags List */}
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

            {/* Comparisons Table */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-slate-800 bg-slate-950/60">
                <h3 className="font-semibold text-slate-200">Plagiarism Comparison Leaderboard</h3>
              </div>
              <div className="divide-y divide-slate-800">
                {result.comparisons.map((comp, idx) => (
                  <div 
                    key={idx} 
                    className="p-4 flex items-center justify-between hover:bg-slate-800/40 transition-colors"
                  >
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