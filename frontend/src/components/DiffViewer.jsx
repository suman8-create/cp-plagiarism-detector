// frontend/src/components/DiffViewer.jsx

import React from 'react';
import { X, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function DiffViewer({ comparison, filesContent, boilerplateSpans, onClose }) {
  if (!comparison) return null;

  const codeA = filesContent[comparison.file_a] || '';
  const codeB = filesContent[comparison.file_b] || '';

  const linesA = codeA.split('\n');
  const linesB = codeB.split('\n');

  const spansBoilerplateA = (boilerplateSpans && boilerplateSpans[comparison.file_a]) || [];
  const spansBoilerplateB = (boilerplateSpans && boilerplateSpans[comparison.file_b]) || [];

  const isMatched = (lineNum, spans) => {
    return spans.some(span => lineNum >= span.start_line && lineNum <= span.end_line);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-6xl h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${comparison.similarity_score >= 70 ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'}`}>
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-100">
                {comparison.file_a} <span className="text-slate-500 font-normal">vs</span> {comparison.file_b}
              </h2>
              <div className="flex items-center space-x-3 text-xs text-slate-400 mt-0.5">
                <span>Similarity: <strong className="text-red-400">{comparison.similarity_score}%</strong></span>
                <span>•</span>
                <span>Shared Hashes: <strong className="text-slate-200">{comparison.shared_fingerprints_count}</strong></span>
              </div>
            </div>
          </div>

          {/* Legend & Close Button */}
          <div className="flex items-center space-x-4">
            <div className="hidden sm:flex items-center space-x-3 text-xs">
              <span className="flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-sm bg-red-500"></span>
                <span className="text-slate-400">Plagiarized</span>
              </span>
              <span className="flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-sm bg-blue-500/60"></span>
                <span className="text-slate-400">Ignored Boilerplate</span>
              </span>
            </div>
            <button 
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Side-by-side code panes */}
        <div className="grid grid-cols-2 flex-1 divide-x divide-slate-800 overflow-hidden font-mono text-xs">
          
          {/* File A */}
          <div className="flex flex-col h-full overflow-hidden">
            <div className="bg-slate-950 px-4 py-2 text-slate-400 border-b border-slate-800 font-sans font-medium flex justify-between">
              <span>{comparison.file_a}</span>
              <span className="text-slate-500">{linesA.length} lines</span>
            </div>
            <div className="flex-1 overflow-y-auto p-3 bg-slate-900/40">
              {linesA.map((line, idx) => {
                const lineNum = idx + 1;
                const plagiarized = isMatched(lineNum, comparison.matched_lines_a);
                const boilerplate = !plagiarized && isMatched(lineNum, spansBoilerplateA);

                let lineClass = 'text-slate-300';
                if (plagiarized) lineClass = 'bg-red-500/20 border-l-2 border-red-500 text-red-200 font-semibold';
                else if (boilerplate) lineClass = 'bg-blue-500/10 border-l-2 border-blue-500/50 text-blue-300 opacity-75';

                return (
                  <div key={idx} className={`flex items-start px-2 py-0.5 rounded leading-5 ${lineClass}`}>
                    <span className="w-8 select-none text-right pr-3 text-slate-600 shrink-0">{lineNum}</span>
                    <pre className="overflow-x-auto whitespace-pre">{line || ' '}</pre>
                  </div>
                );
              })}
            </div>
          </div>

          {/* File B */}
          <div className="flex flex-col h-full overflow-hidden">
            <div className="bg-slate-950 px-4 py-2 text-slate-400 border-b border-slate-800 font-sans font-medium flex justify-between">
              <span>{comparison.file_b}</span>
              <span className="text-slate-500">{linesB.length} lines</span>
            </div>
            <div className="flex-1 overflow-y-auto p-3 bg-slate-900/40">
              {linesB.map((line, idx) => {
                const lineNum = idx + 1;
                const plagiarized = isMatched(lineNum, comparison.matched_lines_b);
                const boilerplate = !plagiarized && isMatched(lineNum, spansBoilerplateB);

                let lineClass = 'text-slate-300';
                if (plagiarized) lineClass = 'bg-red-500/20 border-l-2 border-red-500 text-red-200 font-semibold';
                else if (boilerplate) lineClass = 'bg-blue-500/10 border-l-2 border-blue-500/50 text-blue-300 opacity-75';

                return (
                  <div key={idx} className={`flex items-start px-2 py-0.5 rounded leading-5 ${lineClass}`}>
                    <span className="w-8 select-none text-right pr-3 text-slate-600 shrink-0">{lineNum}</span>
                    <pre className="overflow-x-auto whitespace-pre">{line || ' '}</pre>
                  </div>
                );
              })}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}