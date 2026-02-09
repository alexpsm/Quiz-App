import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus } from 'lucide-react';
import { Layout } from '../components/Layout';
import { PoweredByScore90 } from '../components/Score90Logo';
import { questions as questionsApi } from '../lib/api';

const CATEGORIES = ['League', 'Club', 'Country', 'Fan Culture', 'Stadiums', 'Players', 'History'];

export default function Admin() {
  const [authenticated, setAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    question_text: '',
    option_a: '',
    option_b: '',
    option_c: '',
    option_d: '',
    correct_option: 'A',
    category: 'League',
    difficulty: 1,
  });

  useEffect(() => {
    if (authenticated) {
      loadQuestions();
    }
  }, [authenticated]);

  const handleLogin = (e) => {
    e.preventDefault();
    if (password === 'quizball_admin_2026') {
      setAuthenticated(true);
      setError('');
    } else {
      setError('Invalid password');
    }
  };

  const loadQuestions = async () => {
    try {
      const response = await questionsApi.list();
      setQuestions(response.data);
    } catch (error) {
      console.error('Failed to load questions:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await questionsApi.create(formData, 'quizball_admin_2026');
      setFormData({
        question_text: '',
        option_a: '',
        option_b: '',
        option_c: '',
        option_d: '',
        correct_option: 'A',
        category: 'League',
        difficulty: 1,
      });
      loadQuestions();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create question');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = "w-full bg-black/50 border-2 border-neon-blue/30 focus:border-neon-pink focus:ring-2 focus:ring-neon-pink/50 h-12 rounded-sm text-white placeholder:text-white/30 px-4 outline-none transition-all";

  if (!authenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-[#1a1a2e] to-background flex items-center justify-center p-5">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md"
        >
          <div className="text-center mb-8">
            <h1 className="text-4xl font-extrabold tracking-tighter uppercase text-transparent bg-clip-text bg-gradient-to-r from-neon-blue via-neon-pink to-neon-yellow mb-2">
              Admin Access
            </h1>
            <PoweredByScore90 size="sm" className="justify-center" />
            <p className="text-sm text-gray-400 mt-2">Content Management System</p>
          </div>

          <div className="bg-card border-2 border-neon-blue/30 rounded-lg p-6 shadow-2xl shadow-neon-blue/20">
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">Password</label>
                <input
                  type="password"
                  data-testid="admin-password-input"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={inputClass}
                  placeholder="Enter admin password"
                  required
                />
              </div>

              {error && (
                <div className="bg-destructive/10 border-2 border-destructive rounded-sm p-3 text-sm text-destructive">
                  {error}
                </div>
              )}

              <button
                type="submit"
                data-testid="admin-login-btn"
                className="w-full bg-gradient-to-r from-neon-blue to-neon-pink hover:from-neon-pink hover:to-neon-yellow h-12 px-6 rounded-sm font-bold uppercase tracking-wider shadow-neon-blue hover:shadow-neon-pink transition-all active:scale-95 text-white"
              >
                Access Admin Panel
              </button>
            </form>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <Layout showNav={false}>
      <div className="p-5 space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-extrabold tracking-tighter uppercase text-transparent bg-clip-text bg-gradient-to-r from-neon-blue via-neon-pink to-neon-yellow mb-2">
            Question Manager
          </h1>
          <PoweredByScore90 size="sm" className="justify-center" />
          <p className="text-sm text-gray-400 mt-2">Add and manage trivia questions</p>
        </div>

        {/* Add Question Form */}
        <div className="bg-card border-2 border-neon-blue/30 rounded-lg p-6 shadow-neon-blue">
          <h3 className="text-xl font-bold uppercase tracking-tight text-white mb-4 flex items-center gap-2">
            <Plus size={24} className="text-neon-pink" />
            Add New Question
          </h3>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">Question</label>
              <textarea
                data-testid="question-text-input"
                value={formData.question_text}
                onChange={(e) => setFormData({ ...formData, question_text: e.target.value })}
                className="w-full bg-black/50 border-2 border-neon-blue/30 focus:border-neon-pink focus:ring-2 focus:ring-neon-pink/50 rounded-sm text-white placeholder:text-white/30 p-3 outline-none transition-all"
                placeholder="Which player won the Ballon d'Or in 2024?"
                rows={3}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              {['A', 'B', 'C', 'D'].map((opt) => (
                <div key={opt}>
                  <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">Option {opt}</label>
                  <input
                    type="text"
                    data-testid={`option-${opt.toLowerCase()}-input`}
                    value={formData[`option_${opt.toLowerCase()}`]}
                    onChange={(e) => setFormData({ ...formData, [`option_${opt.toLowerCase()}`]: e.target.value })}
                    className={inputClass}
                    required
                  />
                </div>
              ))}
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">Correct Answer</label>
                <select
                  data-testid="correct-option-select"
                  value={formData.correct_option}
                  onChange={(e) => setFormData({ ...formData, correct_option: e.target.value })}
                  className={inputClass}
                >
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="C">C</option>
                  <option value="D">D</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">Category</label>
                <select
                  data-testid="category-select"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className={inputClass}
                >
                  {CATEGORIES.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">Difficulty</label>
                <select
                  data-testid="difficulty-select"
                  value={formData.difficulty}
                  onChange={(e) => setFormData({ ...formData, difficulty: parseInt(e.target.value) })}
                  className={inputClass}
                >
                  <option value={1}>Easy</option>
                  <option value={2}>Medium</option>
                  <option value={3}>Hard</option>
                </select>
              </div>
            </div>

            {error && (
              <div className="bg-destructive/10 border-2 border-destructive rounded-sm p-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <button
              type="submit"
              data-testid="add-question-btn"
              disabled={loading}
              className="w-full bg-gradient-to-r from-neon-blue to-neon-pink hover:from-neon-pink hover:to-neon-yellow h-12 px-6 rounded-sm font-bold uppercase tracking-wider shadow-neon-blue hover:shadow-neon-pink transition-all active:scale-95 disabled:opacity-50 text-white"
            >
              {loading ? 'Adding...' : 'Add Question'}
            </button>
          </form>
        </div>

        {/* Questions List */}
        <div>
          <h3 className="text-xl font-bold uppercase tracking-tight text-white mb-4">
            Questions ({questions.length})
          </h3>
          
          <div className="space-y-2">
            {questions.map((q) => (
              <div
                key={q.id}
                className="bg-card border-2 border-white/10 rounded-lg p-4"
              >
                <p className="text-white font-medium mb-2">{q.question_text}</p>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <span className="bg-neon-blue/20 text-neon-blue px-2 py-1 rounded">
                    {q.category}
                  </span>
                  <span>Correct: {q.correct_option}</span>
                  <span>Difficulty: {q.difficulty}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}
