// frontend/src/components/AssessmentDetail.jsx

import React, { useState, useEffect } from 'react';
import { ArrowLeft, Plus, HelpCircle, FileCode, CheckCircle, Clock } from 'lucide-react';

export default function AssessmentDetail({ assessment, onBack, onSelectQuestion }) {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      const res = await fetch(`http://127.0.0.1:8000/api/assessments/${assessment.assessment_id}/questions`);
      if (res.ok) {
        const data = await res.json();
        setQuestions(data);
      }
    } catch (err) {
      console.error('Failed to fetch questions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, [assessment.assessment_id]);

  const handleCreateQuestion = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    setSubmitting(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/assessments/${assessment.assessment_id}/questions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description }),
      });

      if (res.ok) {
        setTitle('');
        setDescription('');
        setShowAddModal(false);
        fetchQuestions();
      }
    } catch (err) {
      console.error('Failed to create question:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="inline-flex items-center space-x-2 text-xs font-medium text-slate-400 hover:text-slate-100 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to All Assessments</span>
        </button>

        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition-colors shadow-sm"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Add Question</span>
        </button>
      </div>

      {/* Header Info */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-mono text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
              {assessment.assessment_id}
            </span>
            <h2 className="text-2xl font-bold text-white mt-2">{assessment.title}</h2>
            <p className="text-slate-400 text-xs mt-1">{assessment.description || 'No description provided.'}</p>
          </div>

          <div className="flex items-center space-x-6 text-xs text-slate-400 border-t md:border-t-0 md:border-l border-slate-800 pt-4 md:pt-0 md:pl-6">
            <div>
              <p className="text-slate-500">Questions</p>
              <p className="text-lg font-bold text-slate-100 mt-0.5">{questions.length}</p>
            </div>
            <div>
              <p className="text-slate-500">Status</p>
              <p className="text-lg font-bold text-emerald-400 mt-0.5">Active</p>
            </div>
          </div>
        </div>
      </div>

      {/* Questions Section */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-slate-300">Assessment Questions</h3>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-500 bg-slate-900/30 rounded-xl border border-slate-800/60">
            Loading assessment questions...
          </div>
        ) : questions.length === 0 ? (
          <div className="p-8 text-center bg-slate-900/30 rounded-xl border border-slate-800/60 space-y-3">
            <HelpCircle className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-xs text-slate-400">No questions added to this assessment yet.</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium underline"
            >
              Add your first question
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {questions.map((q) => (
              <div
                key={q.question_id}
                onClick={() => onSelectQuestion && onSelectQuestion(q)}
                className="bg-slate-900 border border-slate-800 hover:border-slate-700 p-5 rounded-xl transition-all cursor-pointer space-y-3 group hover:shadow-md"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2.5">
                    <div className="p-2 bg-slate-800 text-indigo-400 rounded-lg group-hover:bg-indigo-600/10 transition-colors">
                      <FileCode className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-sm text-slate-100 group-hover:text-indigo-300 transition-colors">
                        {q.title}
                      </h4>
                      <span className="text-[11px] font-mono text-slate-500">{q.question_id}</span>
                    </div>
                  </div>

                  {q.is_analyzed ? (
                    <span className="flex items-center space-x-1 text-[11px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      <CheckCircle className="w-3 h-3" />
                      <span>Analyzed</span>
                    </span>
                  ) : (
                    <span className="flex items-center space-x-1 text-[11px] text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                      <Clock className="w-3 h-3" />
                      <span>Pending Uploads</span>
                    </span>
                  )}
                </div>

                <p className="text-xs text-slate-400 line-clamp-2">
                  {q.description || 'No question description or problem statement provided.'}
                </p>

                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
                  <span>Submissions: <strong className="text-slate-300">{q.submission_count}</strong></span>
                  <span className="text-indigo-400 group-hover:translate-x-0.5 transition-transform">Configure / Upload →</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Question Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md p-6 space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Add Problem to Assessment</h3>
            <form onSubmit={handleCreateQuestion} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Problem Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Question 1: Dynamic Programming Fibonacci"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Problem Description (Optional)</label>
                <textarea
                  rows="3"
                  placeholder="Constraints, expected signatures, or problem summary..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex items-center justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-xs font-medium"
                >
                  {submitting ? 'Creating...' : 'Create Question'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}