import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, Trash2 } from 'lucide-react';
import { Layout } from '../components/Layout';
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

  if (!authenticated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-5">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md"
        >
          <div className="text-center mb-8">
            <h1 className="text-4xl font-extrabold tracking-tighter uppercase text-primary mb-2">
              Admin Access
            </h1>
            <p className="text-sm text-gray-400">Content Management System</p>
          </div>

          <div className="bg-card border border-white/10 rounded-lg p-6 shadow-2xl">
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Password</label>
                <input
                  type="password"
                  data-testid="admin-password-input"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-black/50 border border-white/20 focus:border-primary focus:ring-1 focus:ring-primary h-12 rounded-sm text-white placeholder:text-white/30 px-4 outline-none"
                  placeholder="Enter admin password"
                  required
                />
              </div>

              {error && (
                <div className="bg-destructive/10 border border-destructive/50 rounded-sm p-3 text-sm text-destructive">
                  {error}
                </div>
              )}

              <button
                type="submit"
                data-testid="admin-login-btn"
                className="w-full bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-6 rounded-sm font-bold uppercase tracking-wider shadow-[0_0_15px_rgba(251,191,36,0.3)] transition-all active:scale-95"
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
          <h1 className="text-3xl font-extrabold tracking-tighter uppercase text-white mb-2">
            Question Manager
          </h1>
          <p className="text-sm text-gray-400">Add and manage trivia questions</p>
        </div>

        {/* Add Question Form */}
        <div className="bg-card border border-white/10 rounded-lg p-6">
          <h3 className="text-xl font-bold uppercase tracking-tight text-white mb-4 flex items-center gap-2">
            <Plus size={24} />
            Add New Question
          </h3>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Question</label>
              <textarea
                data-testid="question-text-input"
                value={formData.question_text}
                onChange={(e) => setFormData({ ...formData, question_text: e.target.value })}
                className="w-full bg-black/50 border border-white/20 focus:border-primary focus:ring-1 focus:ring-primary rounded-sm text-white placeholder:text-white/30 p-3 outline-none"
                placeholder="Which player won the Ballon d'Or in 2024?"
                rows={3}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Option A</label>
                <input
                  type="text"
                  data-testid="option-a-input"
                  value={formData.option_a}
                  onChange={(e) => setFormData({ ...formData, option_a: e.target.value })}
                  className="w-full bg-black/50 border border-white/20 focus:border-primary focus:ring-1 focus:ring-primary h-12 rounded-sm text-white placeholder:text-white/30 px-4 outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Option B</label>
                <input
                  type="text"
                  data-testid="option-b-input"
                  value={formData.option_b}
                  onChange={(e) => setFormData({ ...formData, option_b: e.target.value })}
                  className="w-full bg-black/50 border border-white/20 focus:border-primary focus:ring-1 focus:ring-primary h-12 rounded-sm text-white placeholder:text-white/30 px-4 outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Option C</label>
                <input
                  type="text"
                  data-testid="option-c-input"
                  value={formData.option_c}
                  onChange={(e) => setFormData({ ...formData, option_c: e.target.value })}
                  className="w-full bg-black/50 border border-white/20 focus:border-primary focus:ring-1 focus:ring-primary h-12 rounded-sm text-white placeholder:text-white/30 px-4 outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Option D</label>
                <input
                  type="text"
                  data-testid="option-d-input"
                  value={formData.option_d}
                  onChange={(e) => setFormData({ ...formData, option_d: e.target.value })}
                  className="w-full bg-black/50 border border-white/20 focus:border-primary focus:ring-1 focus:ring-primary h-12 rounded-sm text-white placeholder:text-white/30 px-4 outline-none"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Correct Answer</label>
                <select
                  data-testid="correct-option-select"
                  value={formData.correct_option}
                  onChange={(e) => setFormData({ ...formData, correct_option: e.target.value })}
                  className="w-full bg-black/50 border border-white/20 focus:border-primary focus:ring-1 focus:ring-primary h-12 rounded-sm text-white px-4 outline-none"
                >
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="C">C</option>
                  <option value="D">D</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Category</label>
                <select
                  data-testid="category-select"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full bg-black/50 border border-white/20 focus:border-primary focus:ring-1 focus:ring-primary h-12 rounded-sm text-white px-4 outline-none"
                >
                  {CATEGORIES.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Difficulty</label>
                <select
                  data-testid="difficulty-select"
                  value={formData.difficulty}
                  onChange={(e) => setFormData({ ...formData, difficulty: parseInt(e.target.value) })}
                  className="w-full bg-black/50 border border-white/20 focus:border-primary focus:ring-1 focus:ring-primary h-12 rounded-sm text-white px-4 outline-none"
                >
                  <option value={1}>Easy</option>
                  <option value={2}>Medium</option>
                  <option value={3}>Hard</option>
                </select>
              </div>
            </div>

            {error && (
              <div className="bg-destructive/10 border border-destructive/50 rounded-sm p-3 text-sm text-destructive">
                {error}
              </div>
            )}

            <button
              type="submit"
              data-testid="add-question-btn"
              disabled={loading}
              className="w-full bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-6 rounded-sm font-bold uppercase tracking-wider shadow-[0_0_15px_rgba(251,191,36,0.3)] transition-all active:scale-95 disabled:opacity-50"
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
                className="bg-card border border-white/10 rounded-lg p-4"
              >
                <div className="flex items-start justify-between mb-2">
                  <p className="text-white font-medium flex-1">{q.question_text}</p>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <span className="bg-primary/20 text-primary px-2 py-1 rounded">
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