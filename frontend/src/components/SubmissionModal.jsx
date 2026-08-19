// frontend/src/components/SubmissionModal.jsx

import React, { useState } from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Cpu, 
  Copy, 
  Check, 
  X, 
  Code2,
  Sparkles,
  BarChart3,
  Timer
} from 'lucide-react';

export default function SubmissionModal({ submission, onClose }) {
  const [copied, setCopied] = useState(false);
  const isAccepted = submission.status === 'Accepted';

  const handleCopy = () => {
    navigator.clipboard.writeText(submission.source_code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
        
        {/* Header Banner */}
        <div className="p-5 border-b border-[#2a2a2a] bg-[#171717] flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {isAccepted ? (
              <CheckCircle2 className="w-6 h-6 text-emerald-400" />
            ) : (
              <XCircle className="w-6 h-6 text-red-400" />
            )}
            <div>
              <div className="flex items-center space-x-2">
                <h3 className={`text-base font-extrabold ${isAccepted ? 'text-emerald-400' : 'text-red-400'}`}>
                  {submission.status}
                </h3>
                <span className="text-xs text-slate-400 font-mono">
                  {submission.passed_test_cases} / {submission.total_test_cases} testcases passed
                </span>
              </div>
              <p className="text-[11px] text-slate-500">
                Submitted by {submission.user_name} at {new Date(submission.submitted_at).toLocaleString()}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-[#2a2a2a] transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-5 overflow-y-auto flex-1 text-xs">
          
          {/* Performance Tiles (Runtime & Memory & Time to Solve) */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-[#141414] border border-[#2a2a2a] p-3.5 rounded-xl space-y-1">
              <div className="flex items-center space-x-1.5 text-slate-400 text-[11px]">
                <Clock className="w-3.5 h-3.5 text-emerald-400" />
                <span>Runtime</span>
              </div>
              <div className="text-lg font-bold font-mono text-slate-100">
                {submission.execution_time_ms} <span className="text-xs text-slate-500 font-normal">ms</span>
              </div>
              <span className="text-[10px] text-emerald-400 font-semibold block">Beats 100.00%</span>
            </div>

            <div className="bg-[#141414] border border-[#2a2a2a] p-3.5 rounded-xl space-y-1">
              <div className="flex items-center space-x-1.5 text-slate-400 text-[11px]">
                <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                <span>Memory</span>
              </div>
              <div className="text-lg font-bold font-mono text-slate-100">
                {submission.memory_mb || 46.38} <span className="text-xs text-slate-500 font-normal">MB</span>
              </div>
              <span className="text-[10px] text-emerald-400 font-semibold block">Beats 77.96%</span>
            </div>

            <div className="bg-[#141414] border border-[#2a2a2a] p-3.5 rounded-xl space-y-1">
              <div className="flex items-center space-x-1.5 text-slate-400 text-[11px]">
                <Timer className="w-3.5 h-3.5 text-amber-400" />
                <span>Time to Solve</span>
              </div>
              <div className="text-lg font-bold font-mono text-slate-100">
                {Math.round(submission.time_taken_seconds)} <span className="text-xs text-slate-500 font-normal">sec</span>
              </div>
              <span className="text-[10px] text-slate-500 block">Solving duration</span>
            </div>
          </div>

          {/* LeetCode Beats Distribution Histogram Graphic */}
          <div className="bg-[#141414] border border-[#2a2a2a] p-4 rounded-xl space-y-2">
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span className="font-semibold text-slate-300">Runtime Distribution</span>
              <span className="text-emerald-400 font-mono font-bold">Your Runtime: {submission.execution_time_ms} ms</span>
            </div>
            <div className="h-20 flex items-end justify-around gap-2 pt-2 border-b border-[#2a2a2a]">
              <div className="w-12 bg-indigo-600 rounded-t h-full flex items-center justify-center text-[10px] text-white font-bold relative">
                <span className="absolute -top-4 text-[9px] text-indigo-300">You</span>
              </div>
              <div className="w-12 bg-[#2a2a2a] rounded-t h-12" />
              <div className="w-12 bg-[#2a2a2a] rounded-t h-6" />
              <div className="w-12 bg-[#2a2a2a] rounded-t h-3" />
            </div>
            <div className="flex justify-around text-[10px] font-mono text-slate-500">
              <span>{submission.execution_time_ms}ms</span>
              <span>15ms</span>
              <span>30ms</span>
              <span>50ms</span>
            </div>
          </div>

          {/* Submitted Code Viewer */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-300">Submitted C++ Code</span>
              <button
                onClick={handleCopy}
                className="inline-flex items-center space-x-1 px-2.5 py-1 bg-[#2a2a2a] hover:bg-[#333] text-slate-300 rounded text-[11px] transition-colors cursor-pointer"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
            <pre className="p-4 bg-[#141414] border border-[#2a2a2a] rounded-xl text-[11px] font-mono text-slate-200 overflow-x-auto max-h-56 leading-relaxed">
              {submission.source_code}
            </pre>
          </div>
        </div>

      </div>
    </div>
  );
}