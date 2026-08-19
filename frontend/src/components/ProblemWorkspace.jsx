// frontend/src/components/ProblemWorkspace.jsx

import React, { useState, useEffect, useRef } from 'react';
import { 
  ArrowLeft, 
  Play, 
  Send, 
  CheckCircle2, 
  AlertCircle,
  Code2, 
  Terminal, 
  Clock, 
  Cpu, 
  RotateCcw,
  RefreshCw,
  History,
  Trophy,
  Copy,
  Check,
  ChevronRight,
  ChevronDown
} from 'lucide-react';
import SubmissionModal from './SubmissionModal';

export default function ProblemWorkspace({ problemSlug, contestId, contestTitle, currentUser, onBack }) {
  const [problem, setProblem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [code, setCode] = useState('');
  const [activeTab, setActiveTab] = useState('description');
  const [submissionsList, setSubmissionsList] = useState([]);
  const [loadingSubmissions, setLoadingSubmissions] = useState(false);
  const [selectedTestCaseIndex, setSelectedTestCaseIndex] = useState(0);
  const [consoleOutput, setConsoleOutput] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedSubmissionModal, setSelectedSubmissionModal] = useState(null);

  // Time tracking ref
  const startTimeRef = useRef(Date.now());

   const activeUserId = currentUser?.user_id || 'guest_user';
   const activeUserName = currentUser?.user_name || 'Guest';

  const fetchProblem = async () => {
    try {
      setLoading(true);
      const res = await fetch(`http://127.0.0.1:8000/api/problems/${problemSlug}`);
      if (res.ok) {
        const data = await res.json();
        setProblem(data);
        setCode(data.starter_code || '#include <iostream>\nusing namespace std;\n\nint main() {\n    // Write your solution here\n    return 0;\n}');
      }
    } catch (err) {
      console.error('Failed to load problem:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSubmissions = async () => {
    try {
      setLoadingSubmissions(true);
      const res = await fetch(`http://127.0.0.1:8000/api/problems/${problemSlug}/submissions`);
      if (res.ok) {
        const data = await res.json();
        setSubmissionsList(data);
      }
    } catch (err) {
      console.error('Failed to load submissions:', err);
    } finally {
      setLoadingSubmissions(false);
    }
  };

  useEffect(() => {
    startTimeRef.current = Date.now();
    fetchProblem();
    fetchSubmissions();
  }, [problemSlug]);

  const handleKeyDown = (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = e.target.selectionStart;
      const end = e.target.selectionEnd;
      const newCode = code.substring(0, start) + '    ' + code.substring(end);
      setCode(newCode);
      setTimeout(() => {
        e.target.selectionStart = e.target.selectionEnd = start + 4;
      }, 0);
    }
  };

  const handleRunCode = async () => {
    setIsRunning(true);
    setConsoleOutput({
      status: 'Compiling & Running',
      message: 'Executing against sample test cases...'
    });

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/problems/${problemSlug}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          source_code: code,
          user_id: activeUserId,
          user_name: activeUserName,
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Execution request failed.');
      }

      const data = await res.json();
      const activeTest = problem?.sample_test_cases?.[selectedTestCaseIndex];

      setConsoleOutput({
        status: data.status,
        passed_test_cases: data.passed_test_cases,
        total_test_cases: data.total_test_cases,
        execution_time_ms: data.execution_time_ms,
        stdout: data.stdout,
        stderr: data.stderr,
        error_message: data.error_message,
        input: activeTest ? activeTest.input_data : 'Sample Case',
        expected: activeTest ? activeTest.expected_output : '',
      });
    } catch (err) {
      setConsoleOutput({
        status: 'Error',
        error_message: err.message || 'Failed to connect to execution backend.'
      });
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmitSolution = async () => {
    setIsSubmitting(true);
    setConsoleOutput({
      status: 'Evaluating Solution',
      message: 'Running against test case suite...'
    });

    const elapsedSeconds = (Date.now() - startTimeRef.current) / 1000.0;

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/problems/${problemSlug}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          source_code: code,
          user_id: activeUserId,
          user_name: activeUserName,
          contest_id: contestId || null,
          time_taken_seconds: elapsedSeconds
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Submission request failed.');
      }

      const data = await res.json();
      setConsoleOutput({
        submission_id: data.submission_id,
        status: data.status,
        passed_test_cases: data.passed_test_cases,
        total_test_cases: data.total_test_cases,
        execution_time_ms: data.execution_time_ms,
        stdout: data.stdout,
        stderr: data.stderr,
        error_message: data.error_message,
        submitted_at: data.submitted_at,
      });

      fetchSubmissions();
    } catch (err) {
      setConsoleOutput({
        status: 'Submission Failed',
        error_message: err.message || 'Failed to evaluate submission.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Accepted':
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
      case 'Wrong Answer':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      default:
        return 'text-red-400 bg-red-500/10 border-red-500/30';
    }
  };

  if (loading) {
    return (
      <div className="p-16 text-center text-xs text-slate-500 bg-[#1e1e1e] rounded-2xl border border-[#2a2a2a]">
        Loading problem workspace...
      </div>
    );
  }

  if (!problem) return null;

  return (
    <div className="space-y-4">
      {/* Top Bar */}
      <div className="flex items-center justify-between bg-[#1e1e1e] border border-[#2a2a2a] px-4 py-3 rounded-xl">
        <div className="flex items-center space-x-3">
          <button
            onClick={onBack}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-[#2a2a2a] transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-bold text-slate-100">{problem.title}</h2>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full border bg-[#141414] text-emerald-400 border-emerald-500/30">
                {problem.difficulty}
              </span>
              {contestTitle && (
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full border bg-indigo-500/10 text-indigo-400 border-indigo-500/30 flex items-center space-x-1">
                  <Trophy className="w-3 h-3 text-amber-400" />
                  <span>{contestTitle}</span>
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setCode(problem.starter_code)}
            title="Reset to starter code"
            className="p-1.5 text-slate-400 hover:text-slate-200 rounded-lg hover:bg-[#2a2a2a] transition-colors cursor-pointer"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={handleRunCode}
            disabled={isRunning || isSubmitting}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-[#2a2a2a] hover:bg-[#333] text-slate-200 rounded-lg text-xs font-medium transition-colors cursor-pointer border border-[#3a3a3a] disabled:opacity-50"
          >
            {isRunning ? <RefreshCw className="w-3.5 h-3.5 animate-spin text-emerald-400" /> : <Play className="w-3.5 h-3.5 text-emerald-400" />}
            <span>Run</span>
          </button>
          <button
            onClick={handleSubmitSolution}
            disabled={isRunning || isSubmitting}
            className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold transition-colors shadow-sm cursor-pointer disabled:opacity-50"
          >
            {isSubmitting ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
            <span>Submit</span>
          </button>
        </div>
      </div>

      {/* Main Split Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-[calc(100vh-210px)] min-h-[580px]">
        
        {/* Left Pane: Description & Submissions */}
        <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-xl flex flex-col overflow-hidden">
          <div className="flex items-center border-b border-[#2a2a2a] bg-[#171717] px-4">
            <button
              onClick={() => setActiveTab('description')}
              className={`py-2.5 px-3 text-xs font-medium border-b-2 transition-colors cursor-pointer ${
                activeTab === 'description'
                  ? 'border-emerald-500 text-emerald-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              Description
            </button>
            <button
              onClick={() => { setActiveTab('submissions'); fetchSubmissions(); }}
              className={`py-2.5 px-3 text-xs font-medium border-b-2 transition-colors cursor-pointer flex items-center space-x-1.5 ${
                activeTab === 'submissions'
                  ? 'border-emerald-500 text-emerald-400'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <History className="w-3.5 h-3.5" />
              <span>Submissions ({submissionsList.length})</span>
            </button>
          </div>

          <div className="p-6 overflow-y-auto space-y-6 text-slate-300 text-xs leading-relaxed flex-1">
            {activeTab === 'description' ? (
              <>
                <p className="whitespace-pre-line text-slate-200 font-sans text-sm">
                  {problem.description}
                </p>

                {problem.examples && problem.examples.length > 0 && (
                  <div className="space-y-4">
                    <h4 className="font-semibold text-slate-200 text-xs uppercase tracking-wider">Examples</h4>
                    {problem.examples.map((ex, idx) => (
                      <div key={idx} className="bg-[#141414] border border-[#2a2a2a] rounded-lg p-3 space-y-1.5 font-mono text-[11px]">
                        <p className="text-slate-400 font-sans font-semibold text-xs">Example {idx + 1}:</p>
                        <div><span className="text-slate-500">Input: </span><span className="text-slate-200">{ex.input}</span></div>
                        <div><span className="text-slate-500">Output: </span><span className="text-emerald-400">{ex.output}</span></div>
                        {ex.explanation && <div className="text-slate-400 font-sans text-[11px] pt-1 border-t border-[#222]">{ex.explanation}</div>}
                      </div>
                    ))}
                  </div>
                )}

                {problem.constraints && (
                  <div className="space-y-2">
                    <h4 className="font-semibold text-slate-200 text-xs uppercase tracking-wider">Constraints</h4>
                    <ul className="list-disc list-inside space-y-1 text-slate-400 font-mono text-[11px]">
                      {problem.constraints.map((c, idx) => <li key={idx}><span className="text-slate-300">{c}</span></li>)}
                    </ul>
                  </div>
                )}
              </>
            ) : (
              /* Submissions History List */
              <div className="space-y-2">
                {submissionsList.map((sub) => (
                  <div
                    key={sub.submission_id}
                    onClick={() => setSelectedSubmissionModal(sub)}
                    className="p-3 bg-[#141414] border border-[#2a2a2a] rounded-xl flex items-center justify-between hover:border-emerald-500/50 cursor-pointer transition-all"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${getStatusBadge(sub.status)}`}>
                          {sub.status}
                        </span>
                        <span className="font-mono text-[11px] text-slate-400">{sub.passed_test_cases}/{sub.total_test_cases} tests</span>
                      </div>
                      <p className="text-[10px] text-slate-500">
                        {new Date(sub.submitted_at).toLocaleTimeString()} • Solved in {Math.round(sub.time_taken_seconds)}s
                      </p>
                    </div>

                    <div className="text-right">
                      <span className="text-xs font-mono font-bold text-slate-200 block">{sub.execution_time_ms} ms</span>
                      <span className="text-[10px] text-emerald-400 font-mono">View Details →</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Pane: Code Editor & Bottom Console */}
        <div className="flex flex-col space-y-4">
          <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-xl flex-1 flex flex-col overflow-hidden">
            <div className="flex items-center justify-between border-b border-[#2a2a2a] bg-[#171717] px-4 py-2 text-xs">
              <div className="flex items-center space-x-2 text-slate-300">
                <Code2 className="w-4 h-4 text-emerald-400" />
                <span className="font-semibold">C++ (g++ 17)</span>
              </div>
              <span className="text-[11px] text-slate-500 font-mono">{activeUserName}</span>
            </div>

            <div className="relative flex-1 bg-[#141414] p-4">
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                onKeyDown={handleKeyDown}
                spellCheck="false"
                className="w-full h-full bg-transparent font-mono text-xs text-indigo-100 placeholder:text-slate-600 focus:outline-none resize-none leading-relaxed selection:bg-emerald-600/30"
              />
            </div>
          </div>

          {/* Bottom Console Panel */}
          <div className="h-44 bg-[#1e1e1e] border border-[#2a2a2a] rounded-xl flex flex-col overflow-hidden">
            <div className="flex items-center justify-between border-b border-[#2a2a2a] bg-[#171717] px-4 py-2">
              <div className="flex items-center space-x-2">
                <Terminal className="w-3.5 h-3.5 text-slate-400" />
                <span className="text-xs font-semibold text-slate-300">Execution Output</span>
              </div>
              {problem.sample_test_cases && (
                <div className="flex space-x-1">
                  {problem.sample_test_cases.map((_, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSelectedTestCaseIndex(idx)}
                      className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors cursor-pointer ${
                        selectedTestCaseIndex === idx ? 'bg-emerald-600 text-white' : 'bg-[#2a2a2a] text-slate-400'
                      }`}
                    >
                      Case {idx + 1}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="p-3 overflow-y-auto flex-1 font-mono text-[11px] space-y-2 bg-[#141414] text-slate-300">
              {consoleOutput ? (
                <div className="space-y-1.5">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${getStatusBadge(consoleOutput.status)}`}>
                      {consoleOutput.status}
                    </span>
                    {consoleOutput.passed_test_cases !== undefined && (
                      <span className="text-slate-400 text-[10px]">
                        ({consoleOutput.passed_test_cases}/{consoleOutput.total_test_cases} test cases passed)
                      </span>
                    )}
                    {consoleOutput.execution_time_ms !== undefined && (
                      <span className="text-slate-500 text-[10px]">
                        • {consoleOutput.execution_time_ms} ms
                      </span>
                    )}
                  </div>

                  {consoleOutput.error_message && (
                    <div className="p-2 bg-red-500/10 border border-red-500/20 rounded text-red-300">
                      {consoleOutput.error_message}
                    </div>
                  )}

                  {consoleOutput.stdout && (
                    <div>
                      <span className="text-slate-500">Output: </span>
                      <span className="text-emerald-300">{consoleOutput.stdout}</span>
                    </div>
                  )}
                </div>
              ) : (
                <span className="text-slate-600">Click "Run" for sample tests or "Submit" for evaluation.</span>
              )}
            </div>
          </div>
        </div>

      </div>

      {/* Submission Inspector Modal */}
      {selectedSubmissionModal && (
        <SubmissionModal
          submission={selectedSubmissionModal}
          onClose={() => setSelectedSubmissionModal(null)}
        />
      )}
    </div>
  );
}